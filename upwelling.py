import csv
import numpy
import scipy
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import date2num, num2date
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates
import time, os, sys, inspect, locale, math
from scipy.interpolate import UnivariateSpline
from utils import display_data
import read_RBR
import readTempHoboFiles
# import scikits.bootstrap as bootstrap
from utils import env_can_weather_data_processing as envir
from matplotlib import rcParams

sys.path.insert(0, '/software/SAGEwork/Seiches')
import fft.filters as filters
import fft.fft_utils as fft_utils
import fft.peakdetect as peakdetect
import spectral_analysis
import tor_harb_windrose
import scipy.integrate


import utils.interpolate as interpolate

sys.path.insert(0, '/software/SAGEwork/Pressure_analysis')
import utils.hdf_tools as hdf
import utils.read_csv as read_csv
import utils.stats as stat

# turn off warning in polyfit
import warnings
warnings.simplefilter('ignore', numpy.RankWarning)
from utils import smooth

windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
window_6hour = "window_6hour"  # 30 * 6 for a 2 minute sampling
window_hour = "window_hour"  # 30
window_day = "window_day"  # 30 * 24
window_half_day = "window_half_day"  # 30 * 12
window_3days = "window_3days"  # 3 * 30 * 24
window_7days = "window_7days"  # 7 * 30 * 24


def calculate_total_flux():
    pass


def calculate_30days_running_mean(dateTime, temp, tunits):
    dt = dateTime[2] - dateTime[1]  # usually days
    if tunits == "day":
        nspan = 30 / dt
    elif tunits == "sec":
        nspan = 30 / dt * 3600 * 24
    else:
        raise Exception("time unit unsupported")

    mean_month = utils.smooth.smoothfit(dateTime, temp, nspan, windows[1])

#===============================================================================
#     mean_month = numpy.zeros(len(temp))
#     for i in range(0, len(dateTime)):
#         sumval = 0
#         for j in range(0, min(int(nspan), len(temp) - i)):
#             sumval += temp[i + j]
#         avg = sumval / nspan
#         for k in range(0, min(int(nspan), len(temp) - i)):
#             mean_month[i + k] = avg
#
#         # increment
#         i += int(nspan)
#     # end for
#===============================================================================
    return mean_month['smoothed']

def calculate_cooling_rate(time, month_mean, maxpeaks, minpeaks, tunits):
    xm = [p[0] for p in maxpeaks]
    ym = [p[1] for p in maxpeaks]
    xn = [p[0] for p in minpeaks]
    yn = [p[1] for p in minpeaks]
    j = 0

    cr = numpy.zeros(len(maxpeaks))


    for i in range(0, len(xm)):
        try:
            if xm[i] > xn[i]:  # skip, we need to start with a max
                xmax = xm[i]
                xmin = xn[i + 1]
                ymax = ym[i]
                ymin = yn[i + 1]
            else:  # good
                xmax = xm[i]
                xmin = xn[i]
                ymax = ym[i]
                ymin = yn[i]
        except:
            print " Out of bounds nodes. Ignore!"

        mm_value = None
        # find month_mean value for
        for k in range(0, len(time)):
            if time[k] > xmax:
                mm_value = month_mean[k]
                break
        # end for
        if mm_value == None:
            raise Exception("month_mean value not found!")

        if  mm_value != None and ymax > mm_value and ymin < mm_value:
            dt = ymax - ymin
            dur = xmin - xmax
            cr[j] = dt / dur
            j += 1
    # END FOR
    return cr


def calculate_Upwelling_indices(time, temp, fnames, tunits, zoneName):
    # calculate for each month

    # calculate IA = integrated anomaly
    for i in range(0, len(time)):

        month_mean = calculate_30days_running_mean(time[i], temp[i], tunits)

        # calculate the area under the month_mean but trim the ends by 10% to eliminte errors
        trim = int (len(month_mean) / 10)
        minarr = [ min(month_mean[j], temp[i][j]) for j in range(0, len(time[i]))]
        area_min = scipy.integrate.simps(minarr[trim:-trim], time[i][trim:-trim])
        area_line = scipy.integrate.simps(month_mean[trim:-trim], time[i][trim:-trim])
        A = area_line - area_min
        Tm = numpy.mean(temp[i][trim:-trim])
        print "name=%s UIA=%f mean SST=%f" % (fnames[i], A, Tm)
        # calculate peaks
        _max, _min = peakdetect.peakdetect(temp[i][trim:-trim], time[i][trim:-trim], 100, 0.30)

        # calculate roots TOO slow
        # rx, ry1, ry2, p1, p2 = interpolate.find_roots(time[i][trim:-trim], temp[i][trim:-trim], time[i][trim:-trim], month_mean[trim:-trim])

        # calculate cooling intensity UCI
        uci = calculate_cooling_rate(time[i][trim:-trim], month_mean[trim:-trim], _max, _min, tunits)

        #=======================================================================
        # print "max-min-uci : %s, len uci = %d" % (fnames[i], len(uci))
        # for j in range(0, len(uci)):
        #     print "%f" % uci[j]
        #=======================================================================

        UCI_mean = uci.sum() / len(uci)
        print "name=%s UCI=%f" % (fnames[i], UCI_mean)
        utils.display_data.display_temperatures_and_peaks([time[i][trim:-trim], time[i][trim:-trim]], [month_mean[trim:-trim], temp[i][trim:-trim]],
                                                       [_max], [_min], [], fnames = ['30 day mean', fnames[i]], custom = zoneName, fill = True)



def calculate_correlation():
    pass


def draw_upwelling_correlation_IQR(filepath):

    '''
    Works as is with
    /home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/FFT_Surf
        and
    /home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/FFT_Bot

    and
    /home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/SelectedZones-NoLO.csv
    '''
    ########################################################
    # Inter Quartile range 25-75
    ########################################################
    # bottom UIA
    #########################################################################################################
    # The indices passed to the read_csv must be in ascending order to match what we expect in the output
    #########################################################################################################
    data = read_csv.read_csv(filepath, 1, [1, 11, 16])
    temp = data[2]  # .astype(numpy.float)
    uia = data[1]  # .astype(numpy.float)
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, temp)
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    stat.plot_regression(uia, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                          x_label = "UIA ($^oC$ day)", y_label = "Bottom Temp. 75-25  IQR  ($^oC$)", title = "Bot Temp IQR vs. Upwelling Integrated Anomaly Index", \
                          r_value = r_value, p_value = p_value)

    # bottom UIC
    data = read_csv.read_csv(filepath, 1, [1, 12, 16])
    temp = data[2]  # .astype(numpy.float)
    uci = data[1]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uci, temp)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(uci, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "UCI ($^oC$/day)", y_label = "Bottom Temp 75-25 IQR  ($^oC$)", title = "Bot Temp IQR vs. Upwelling Cooling Intensity Index", \
                         r_value = r_value, p_value = p_value)

    #------------------------------------------------------------------------------------------------------
    # Surface UIA
    #------------------------------------------------------------------------------------------------------
    data = read_csv.read_csv(filepath, 1, [1, 8, 15])
    temp = data[2]  # .astype(numpy.float)
    uia = data[1]  # .astype(numpy.float)
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, temp)
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    stat.plot_regression(uia, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                          x_label = "UIA ($^oC$ day)", y_label = "Surface Temp 75-25 IQR  ($^oC$)", title = "Surf Temp IQR vs. Upwelling Integrated Anomaly Index", \
                          r_value = r_value, p_value = p_value)

    # Surface UIC
    data = read_csv.read_csv(filepath, 1, [1, 9, 15])
    temp = data[2]  # .astype(numpy.float)
    uci = data[1]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uci, temp)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(uci, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "UCI ($^oC$/day)", y_label = "Surface Temp 75-25 IQR ($^oC$)", title = "Surf Temp IQR vs. Upwelling Cooling Intensity Index", \
                         r_value = r_value, p_value = p_value)

    ########################################################
    # Mean depth
    ########################################################
    # bottom Temp
    data = read_csv.read_csv(filepath, 1, [1, 2, 16])
    depth = data[1]  # .astype(numpy.float)
    temp = data[2]
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(depth, temp)

    stat.plot_regression(depth, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "Mean depth ($m$)", y_label = "Bot Temp 75-25 IQR  ($C^o$)", title = "Bottom Temp IQR vs. Mean depth", \
                         r_value = r_value, p_value = p_value)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)


    #------------------------------------------------------------------------------------------------------
    # Surface Temp
    #------------------------------------------------------------------------------------------------------
    data = read_csv.read_csv(filepath, 1, [1, 2, 15])
    depth = data[1]  # .astype(numpy.float)
    temp = data[2]
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(depth, temp)
    stat.plot_regression(depth, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "Mean depth ($m$)", y_label = "Surface Temp 75-25 IQR ($C^o$)", title = "Surface Temp IQR  vs. Mean depth", \
                         r_value = r_value, p_value = p_value)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)


    ########################################################
    # 25% Quartile
    ########################################################
    # bottom UIA
    #########################################################################################################
    # The indices passed to the read_csv must be in ascending order to match what we expect in the output
    #########################################################################################################
    data = read_csv.read_csv(filepath, 1, [1, 11, 18])
    temp = data[2]  # .astype(numpy.float)
    uia = data[1]  # .astype(numpy.float)
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, temp)
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    stat.plot_regression(uia, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                          x_label = "UIA ($^oC$ day)", y_label = "Bottom Temp. 25% Quartile  ($^oC$)", title = "Bot Temp 25% Quartile Upwelling Integrated Anomaly Index", \
                          r_value = r_value, p_value = p_value)

    # bottom UIC
    data = read_csv.read_csv(filepath, 1, [1, 12, 18])
    temp = data[2]  # .astype(numpy.float)
    uci = data[1]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uci, temp)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(uci, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "UCI ($^oC$/day)", y_label = "Bottom Temp 25% Quartile  ($^oC$)", title = "Bot Temp 25% Quartile vs. Upwelling Cooling Intensity Index", \
                         r_value = r_value, p_value = p_value)

    #------------------------------------------------------------------------------------------------------
    # Surface UIA
    #------------------------------------------------------------------------------------------------------
    data = read_csv.read_csv(filepath, 1, [1, 8, 17])
    temp = data[2]  # .astype(numpy.float)
    uia = data[1]  # .astype(numpy.float)
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, temp)
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    stat.plot_regression(uia, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                          x_label = "UIA ($^oC$ day)", y_label = "Surface Temp 25% Quartile ($^oC$)", title = "Surf Temp 25% Quartile vs. Upwelling Integrated Anomaly Index", \
                          r_value = r_value, p_value = p_value)

    # Surface UIC
    data = read_csv.read_csv(filepath, 1, [1, 9, 17])
    temp = data[2]  # .astype(numpy.float)
    uci = data[1]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uci, temp)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(uci, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "UCI ($^oC$/day)", y_label = "Surface Temp 25% Quartile ($^oC$)", title = "Surf Temp 25% Quartile vs. Upwelling Cooling Intensity Index", \
                         r_value = r_value, p_value = p_value)

    ########################################################
    # Mean depth
    ########################################################
    # bottom Temp
    data = read_csv.read_csv(filepath, 1, [1, 2, 18])
    depth = data[1]  # .astype(numpy.float)
    temp = data[2]
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(depth, temp)

    stat.plot_regression(depth, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "Mean depth ($m$)", y_label = "Bot Temp 25% Quartile($C^o$)", title = "Bottom Temp 25% Quartile vs. Mean depth", \
                         r_value = r_value, p_value = p_value)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)


    #------------------------------------------------------------------------------------------------------
    # Surface Temp
    #------------------------------------------------------------------------------------------------------
    data = read_csv.read_csv(filepath, 1, [1, 2, 17])
    depth = data[1]  # .astype(numpy.float)
    temp = data[2]
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(depth, temp)
    stat.plot_regression(depth, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "Mean depth ($m$)", y_label = "Surface Temp 25% Quartile ($C^o$)", title = "Surface Temp 25% Quartile vs. Mean depth", \
                         r_value = r_value, p_value = p_value)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)


def draw_upwelling_correlation(filepath):

    '''
    Works as is with
    /home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/FFT_Surf
        and
    /home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/FFT_Bot

    and
    /home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/SelectedZones-NoLO.csv
    '''
    ########################################################
    # Mean Temperature
    ########################################################
    # bottom UIA
    #########################################################################################################
    # The indices passed to the read_csv must be in ascending order to match what we expect in the output
    #########################################################################################################
    data = read_csv.read_csv(filepath, 1, [1, 10, 11])
    temp = data[1]  # .astype(numpy.float)
    uia = data[2]  # .astype(numpy.float)
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, temp)
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    stat.plot_regression(uia, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                          x_label = "UIA ($^oC$ day)", y_label = "Bottom Mean Temperature ($^oC$)", title = "Temperature vs. Upwelling Integrated Anomaly Index", \
                          r_value = r_value, p_value = p_value)

    # bottom UIC
    data = read_csv.read_csv(filepath, 1, [1, 10, 12])
    temp = data[1]  # .astype(numpy.float)
    uci = data[2]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uci, temp)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(uci, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "UCI ($^oC$/day)", y_label = "Bootom Mean Temperature ($^oC$)", title = "Temperature vs. Upwelling Cooling Intensity Index", \
                         r_value = r_value, p_value = p_value)

    #------------------------------------------------------------------------------------------------------
    # Surface UIA
    #------------------------------------------------------------------------------------------------------
    data = read_csv.read_csv(filepath, 1, [1, 7, 8])
    temp = data[1]  # .astype(numpy.float)
    uia = data[2]  # .astype(numpy.float)
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, temp)
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    stat.plot_regression(uia, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                          x_label = "UIA ($^oC$ day)", y_label = "Surface Mean Temperature ($^oC$)", title = "Temperature vs. Upwelling Integrated Anomaly Index", \
                          r_value = r_value, p_value = p_value)

    # Surface UIC
    data = read_csv.read_csv(filepath, 1, [1, 7, 9])
    temp = data[1]  # .astype(numpy.float)
    uci = data[2]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uci, temp)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(uci, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "UCI ($^oC$/day)", y_label = "Surface Mean Temperature ($^oC$)", title = "Temperature vs. Upwelling Cooling Intensity Index", \
                         r_value = r_value, p_value = p_value)


    ########################################################
    # Min Temperature
    ########################################################
    # bot UIA
    #########################################################################################################
    # The indices passed to the read_csv must be in ascending order to match what we expect in the output
    #########################################################################################################
    data = read_csv.read_csv(filepath, 1, [1, 11, 14])
    temp = data[2]  # .astype(numpy.float)
    uia = data[1]  # .astype(numpy.float)
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, temp)
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    stat.plot_regression(uia, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                          x_label = "UIA ($^oC$ day)", y_label = "Bottom Min Temperature ($^oC$)", title = "Min Temperature vs. Upwelling Integrated Anomaly Index", \
                          r_value = r_value, p_value = p_value)

    # bottom UIC
    data = read_csv.read_csv(filepath, 1, [1, 12, 14])
    temp = data[2]  # .astype(numpy.float)
    uci = data[1]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uci, temp)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(uci, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "UCI ($^oC$/day)", y_label = "Bottom Min Temperature ($^oC$)", title = "Min Temperature vs. Upwelling Cooling Intensity Index", \
                         r_value = r_value, p_value = p_value)

    #------------------------------------------------------------------------------------------------------
    # Surface UIA
    #------------------------------------------------------------------------------------------------------
    data = read_csv.read_csv(filepath, 1, [1, 8, 13])
    temp = data[2]  # .astype(numpy.float)
    uia = data[1]  # .astype(numpy.float)
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, temp)
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    stat.plot_regression(uia, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                          x_label = "UIA ($^oC$ day)", y_label = "Surface Min Temperature ($^oC$)", title = "Min Temperature vs. Upwelling Integrated Anomaly Index", \
                          r_value = r_value, p_value = p_value)

    # Surface UIC
    data = read_csv.read_csv(filepath, 1, [1, 9, 13])
    temp = data[2]  # .astype(numpy.float)
    uci = data[1]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uci, temp)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(uci, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "UCI ($^oC$/day)", y_label = "Surface Min Temperature ($^oC$)", title = "Min Temperature vs. Upwelling Cooling Intensity Index", \
                         r_value = r_value, p_value = p_value)




    ########################################################
    # Standard deviation
    ########################################################
    # bottom UIA
    data = read_csv.read_csv(filepath, 1, [1, 6, 11])
    temp = data[1]  # .astype(numpy.float)
    uia = data[2]  # .astype(numpy.float)
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, temp)
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    stat.plot_regression(uia, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                          x_label = "UIA ($^oC$ day)", y_label = "Bottom SD Temperature ($^oC$)", title = "SD Bottom Temperature vs. Upwelling Integrated Anomaly Index", \
                          r_value = r_value, p_value = p_value)

    # bottom UIC
    data = read_csv.read_csv(filepath, 1, [1, 6, 12])
    temp = data[1]  # .astype(numpy.float)
    uci = data[2]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uci, temp)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(uci, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "UCI ($^oC$/day)", y_label = "Bootom SD Temperature ($^oC$)", title = "SD Bottom Temperature vs. Upwelling Cooling Intensity Index", \
                         r_value = r_value, p_value = p_value)

    #------------------------------------------------------------------------------------------------------
    # Surface UIA
    #------------------------------------------------------------------------------------------------------
    data = read_csv.read_csv(filepath, 1, [1, 5, 8])
    temp = data[1]  # .astype(numpy.float)
    uia = data[2]  # .astype(numpy.float)
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, temp)
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    stat.plot_regression(uia, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                          x_label = "UIA ($^oC$ day)", y_label = "Surface SD Temperature ($^oC$)", title = "SD Surface Temperature vs. Upwelling Integrated Anomaly Index", \
                          r_value = r_value, p_value = p_value)

    # Surface UIC
    data = read_csv.read_csv(filepath, 1, [1, 5, 9])
    temp = data[1]  # .astype(numpy.float)
    uci = data[2]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uci, temp)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(uci, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "UCI ($^oC$/day)", y_label = "Surface SD Temperature ($^oC$)", title = "SD Surface Temperature vs. Upwelling Cooling Intensity Index", \
                         r_value = r_value, p_value = p_value)

    #------------------------------------------------------------------
    # SD vs mean depth
    #------------------------------------------------------------------
    # bottom Temp
    data = read_csv.read_csv(filepath, 1, [1, 2, 6])
    depth = data[1]  # .astype(numpy.float)
    temp = data[2]
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(depth, temp)

    stat.plot_regression(depth, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "Mean depth ($m$)", y_label = "Bottom SD Temperature ($^oC$)", title = "Bottom SD Temp vs. Mean depth", \
                         r_value = r_value, p_value = p_value)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)


    #------------------------------------------------------------------------------------------------------
    # Surface Temp
    #------------------------------------------------------------------------------------------------------
    data = read_csv.read_csv(filepath, 1, [1, 2, 5])
    depth = data[1]  # .astype(numpy.float)
    temp = data[2]
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(depth, temp)
    stat.plot_regression(depth, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "Mean depth ($m$)", y_label = "Surface SD Temp ($C^o$)", title = "Surface SD Temp vs. Mean depth", \
                         r_value = r_value, p_value = p_value)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)



    ########################################################
    # Mouth area & mean depth mean temperature
    ########################################################
    # bottom Temp
    bmouth = False
    if bmouth:
        data = read_csv.read_csv(filepath, 1, [1, 10, 13, 14])
        temp = data[1]  # .astype(numpy.float)
        depth = data[2]  # .astype(numpy.float)
        width = data[3]
        mouth = depth * width
        [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(mouth, temp)
        stat.plot_regression(mouth, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                             x_label = "Mouth area ($m^2$)", y_label = "Mean Bottom Temp ($C^o$)", title = "Mean bottom Temp vs. Mouth area", \
                             r_value = r_value, p_value = p_value)

    else:
        data = read_csv.read_csv(filepath, 1, [1, 2, 10])
        depth = data[1]  # .astype(numpy.float)
        temp = data[2]
        [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(depth, temp)

        stat.plot_regression(depth, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                             x_label = "Mean depth ($m$)", y_label = "Mean Bottom Temp ($C^o$)", title = "Mean bottom Temp vs. Mean depth", \
                             r_value = r_value, p_value = p_value)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)


    #------------------------------------------------------------------------------------------------------
    # Surface Temp
    #------------------------------------------------------------------------------------------------------
    if bmouth:
        data = read_csv.read_csv(filepath, 1, [1, 13, 14, 7])
        temp = data[1]  # .astype(numpy.float)

        depth = data[2]  # .astype(numpy.float)
        width = data[3]
        mouth = depth * width
        [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(mouth, temp)
        stat.plot_regression(mouth, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                             x_label = "Mouth area ($m^2$)", y_label = "Mean Surface Temp ($C^o$)", title = "Mean Surface Temp vs. Mouth area", \
                             r_value = r_value, p_value = p_value)

    else:
        data = read_csv.read_csv(filepath, 1, [1, 2, 7])
        depth = data[1]  # .astype(numpy.float)
        temp = data[2]
        [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(depth, temp)
        stat.plot_regression(depth, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                             x_label = "Mean depth ($m$)", y_label = "Mean Surface Temp ($C^o$)", title = "Mean Surface Temp vs. Mean depth", \
                             r_value = r_value, p_value = p_value)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)


def draw_upwelling_correlation_all(filepath):

    '''
    Works as is with
    /home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/allStations

    '''
    ########################################################
    # Mean Temperature
    ########################################################
    # bottom UIA
    #########################################################################################################
    # The indices passed to the read_csv must be in ascending order to match what we expect in the output
    #########################################################################################################
    data = read_csv.read_csv(filepath, 1, [1, 5, 6])
    temp = data[1]  # .astype(numpy.float)
    uia = data[2]  # .astype(numpy.float)
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, temp)
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    stat.plot_regression(uia, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                          x_label = "UIA ($^oC$ day)", y_label = "Bottom Mean Temperature ($^oC$)", title = "Temperature vs. Upwelling Integrated Anomaly Index", \
                          r_value = r_value, p_value = p_value)

    # bottom UIC
    data = read_csv.read_csv(filepath, 1, [1, 5, 7])
    temp = data[1]  # .astype(numpy.float)
    uci = data[2]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uci, temp)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(uci, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "UCI ($^oC$/day)", y_label = "Bootom Mean Temperature ($^oC$)", title = "Temperature vs. Upwelling Cooling Intensity Index", \
                         r_value = r_value, p_value = p_value)

    ########################################################
    # Standard deviation
    ########################################################
    # bottom UIA
    data = read_csv.read_csv(filepath, 1, [1, 4, 6])
    temp = data[1]  # .astype(numpy.float)
    uia = data[2]  # .astype(numpy.float)
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, temp)
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    stat.plot_regression(uia, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                          x_label = "UIA ($^oC$ day)", y_label = "Bottom SD Temperature ($^oC$)", title = "SD Temperature vs. Upwelling Integrated Anomaly Index", \
                          r_value = r_value, p_value = p_value)

    # bottom UIC
    data = read_csv.read_csv(filepath, 1, [1, 6, 7])
    temp = data[1]  # .astype(numpy.float)
    uci = data[2]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uci, temp)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(uci, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "UCI ($^oC$/day)", y_label = "Bootom SD Temperature ($^oC$)", title = "SD Temperature vs. Upwelling Cooling Intensity Index", \
                         r_value = r_value, p_value = p_value)





def draw_upwelling_fish_correlation(filepath):

    ########################################################
    # Fish detection
    ########################################################
    # bottom UIA
    data = read_csv.read_csv(filepath, 1, [1, 7, 9])
    uia = data[1]  # .astype(numpy.float)
    det = data[2]  # .astype(numpy.float)
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, det)
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    stat.plot_regression(uia, det, slope = slope, intercept = intercept, point_labels = data[0], \
                          x_label = "UIA ($^oC$ day)", y_label = "Fish detections", title = "Fish detections vs. Bottom Upwelling Integrated Anomaly Index", \
                          r_value = r_value, p_value = p_value)

    # bottom IQR
    data = read_csv.read_csv(filepath, 1, [1, 9, 17])
    iqr = data[2]  # .astype(numpy.float)
    det = data[1]  # .astype(numpy.float)


    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(iqr, det)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(iqr, det, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "Bottom IQR ($^oC$)", y_label = "Fish detections", title = "Fish detections vs. Bottom Inter Quartile Range", \
                         r_value = r_value, p_value = p_value)

    #------------------------------------------------------------------------------------------------------
    # Surface UIA
    #------------------------------------------------------------------------------------------------------
    data = read_csv.read_csv(filepath, 1, [1, 4, 9])
    uia = data[1]  # .astype(numpy.float)
    det = data[2]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, det)
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    stat.plot_regression(uia, det, slope = slope, intercept = intercept, point_labels = data[0], \
                          x_label = "UIA ($^oC$ day)", y_label = "Fish detections", title = "Fish detections vs. Surface Upwelling Integrated Anomaly Index", \
                          r_value = r_value, p_value = p_value)

    # Surface IQR
    data = read_csv.read_csv(filepath, 1, [1, 9, 16])
    iqr = data[2]  # .astype(numpy.float)
    det = data[1]  # .astype(numpy.float)


    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(iqr, det)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(iqr, det, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "Surface IQR ($^oC$)", y_label = "Fish detections", title = "Fish detections vs. Surface Inter Quartile Range", \
                         r_value = r_value, p_value = p_value)



    ########################################################
    # Surf Temp min
    ########################################################
    data = read_csv.read_csv(filepath, 1, [1, 9, 18])
    mtemp = data[2]
    det = data[1]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(mtemp, det)

    stat.plot_regression(mtemp, det, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "Surface Min Temperature ($^oC$)", y_label = "Fish detections", title = "Fish detections vs. Surface Min Temperature", \
                         r_value = r_value, p_value = p_value)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

#===============================================================================
#     ########################################################
#     # Surf Temp max
#     ########################################################
#     data = read_csv.read_csv(filepath, 1, [1, 9, 11])
#     Mtemp = data[2]
#     det = data[1]  # .astype(numpy.float)
#
#     [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(Mtemp, det)
#
#     stat.plot_regression(Mtemp, det, slope = slope, intercept = intercept, point_labels = data[0], \
#                          x_label = "Surface Max Temperature ($^oC$)", y_label = "Fish detections", title = "Fish detections vs. Surface Max Temp", \
#                          r_value = r_value, p_value = p_value)
#
#     print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
#===============================================================================


    ########################################################
    # Bot Temp min
    ########################################################
    data = read_csv.read_csv(filepath, 1, [1, 9, 19])
    mtemp = data[2]
    det = data[1]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(mtemp, det)

    stat.plot_regression(mtemp, det, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "Bottom Min Temperature ($^oC$)", y_label = "Fish detections", title = "Fish detections vs. Bottom Min Temperature", \
                         r_value = r_value, p_value = p_value)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

#===============================================================================
#     ########################################################
#     # Bot Temp max
#     ########################################################
#     data = read_csv.read_csv(filepath, 1, [1, 9, 14])
#     Mtemp = data[2]
#     det = data[1]  # .astype(numpy.float)
#
#     [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(Mtemp, det)
#
#     stat.plot_regression(Mtemp, det, slope = slope, intercept = intercept, point_labels = data[0], \
#                          x_label = "Bottom Max Temperature ($^oC$)", y_label = "Fish detections", title = "Fish detections vs. Bottom Max Temp", \
#                          r_value = r_value, p_value = p_value)
#
#     print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
#===============================================================================

#===============================================================================
#     ########################################################
#     # Mouth mean depth
#     ########################################################
#     data = read_csv.read_csv(filepath, 1, [1, 2, 9])
#     depth = data[1]
#     det = data[2]  # .astype(numpy.float)
#
#     [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(depth, det)
#
#     stat.plot_regression(depth, det, slope = slope, intercept = intercept, point_labels = data[0], \
#                          x_label = "Mean depth ($m$)", y_label = "Fish detections", title = "Fish detections vs. Mean depth", \
#                          r_value = r_value, p_value = p_value)
#
#     print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
#===============================================================================


def draw_upwelling_fish_correlation_all(filepath):


    ########################################################
    # Fish detection
    ########################################################
    # bottom UIA
    data = read_csv.read_csv(filepath, 1, [1, 6, 8])
    uia = data[1]  # .astype(numpy.float)
    det = data[2]  # .astype(numpy.float)
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, det)
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    stat.plot_regression(uia, det, slope = slope, intercept = intercept, point_labels = data[0], \
                          x_label = "UIA ($^oC$ day)", y_label = "Fish detections", title = "Fish detections vs. Bottom Upwelling Integrated Anomaly Index", \
                          r_value = r_value, p_value = p_value)

    # bottom UIC
    data = read_csv.read_csv(filepath, 1, [1, 7, 8])
    uci = data[1]  # .astype(numpy.float)
    det = data[2]  # .astype(numpy.float)


    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uci, det)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(uci, det, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "UCI ($^oC$/day)", y_label = "Fish detections", title = "Fish detections vs. Bottom Upwelling Cooling Intensity Index", \
                         r_value = r_value, p_value = p_value)

    ########################################################
    # mean Temp
    ########################################################
    data = read_csv.read_csv(filepath, 1, [1, 5, 8])
    temp = data[1]
    det = data[2]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(temp, det)

    stat.plot_regression(temp, det, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "Mean Temp ($^oC$)", y_label = "Fish detections", title = "Fish detections vs. Mean temp", \
                         r_value = r_value, p_value = p_value)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)




    ########################################################
    # SD Temp
    ########################################################
    data = read_csv.read_csv(filepath, 1, [1, 4, 8])
    sdtemp = data[1]
    det = data[2]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(sdtemp, det)

    stat.plot_regression(sdtemp, det, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "Temp Std Deviation ($^oC$)", y_label = "Fish detections", title = "Fish detections vs. Temp Std Deviation", \
                         r_value = r_value, p_value = p_value)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)


    ########################################################
    # Max -Min
    ########################################################
    data = read_csv.read_csv(filepath, 1, [1, 8, 12])
    mmtemp = data[2]
    det = data[1]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(mmtemp, det)

    stat.plot_regression(mmtemp, det, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "Max-Min Temperature ($^oC$)", y_label = "Fish detections", title = "Fish detections vs. Max - min Temperature", \
                         r_value = r_value, p_value = p_value)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)


    ########################################################
    # Temp min
    ########################################################
    data = read_csv.read_csv(filepath, 1, [1, 8, 10])
    mtemp = data[2]
    det = data[1]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(mtemp, det)

    stat.plot_regression(mtemp, det, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "Min Temperature ($^oC$)", y_label = "Fish detections", title = "Fish detections vs. Min Temperature", \
                         r_value = r_value, p_value = p_value)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    ########################################################
    # Temp max
    ########################################################
    data = read_csv.read_csv(filepath, 1, [1, 8, 11])
    Mtemp = data[2]
    det = data[1]  # .astype(numpy.float)

    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(Mtemp, det)

    stat.plot_regression(Mtemp, det, slope = slope, intercept = intercept, point_labels = data[0], \
                         x_label = "Max Temperature ($^oC$)", y_label = "Fish detections", title = "Fish detections vs. Max Temp", \
                         r_value = r_value, p_value = p_value)

    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)


def plot_Upwelling_one_fig(ppath, timeint, timeavg = None, subplot = None, filter = None, peaks = False, minorgrid = 'mondays', \
                            datetype = 'date'):
    print "plot_Upwelling_one_fig()"

    startdate = timeint[0]
    enddate = timeint[1]
    dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
    start_num = date2num(dt)
    dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
    end_num = date2num(dt)

    # funits = "Hz"
    funits = "cph"
    # tunits = "sec"
    tunits = "day"

    # Separate directories from files
    base, dirs, files = iter(os.walk(ppath)).next()

    if timeavg == None:
        moving_avg = window_hour
    else:
        moving_avg = timeavg

    atime = []
    atemp = []
    aresults = []
    azone = []
    a_max = []
    a_min = []
    afname = []

    if len(dirs) == 0 :
        dirs = [ppath]

    dirList = sorted(dirs, key = lambda x: x.split('.')[0])

    for path in dirList:
        if len(dirs) > 1 :
            dateTime, temp, results, k , fnames = readTempHoboFiles.read_files(moving_avg, windows[1], [start_num, end_num], ppath + '/' + path)
        else:
            dateTime, temp, results, k , fnames = readTempHoboFiles.read_files(moving_avg, windows[1], [start_num, end_num], path)
        HOBOdateTimeArr = dateTime
        HOBOresultsArr = results
        HOBOtempArr = temp

        difflines = False

        if len(fnames) > 0:
            fn = fnames[0][fnames[0].find("_") + 1:]
        # else:
        #    fn = fnames[0][fnames[0].find("_") + 1:]
        zoneName, fileExtension = os.path.splitext(fn)

        atime.append(dateTime[0])
        atemp.append(temp[0])
        aresults.append(results[0])
        azone.append(zoneName)
        afname.append(fnames[0])



    # end (for path)

    if peaks:
        # Calculate upwelling indices and plot the shaded uwelling zones defined by the 30 days running average.
            # calculate IA = integrated anomaly
        for i in range(0, len(atime)):
            trim = int (len(atime[i]) / 20)
            # calculate peaks
            _max, _min = peakdetect.peakdetect(aresults[i][trim:-trim], atime[i][trim:-trim], 250, 0.80)

            a_max.append(_max)
            a_min.append(_min)

        utils.display_data.display_temperatures_and_peaks(numpy.array(atime), numpy.array(aresults), \
                                                    numpy.array(a_max), numpy.array(a_min), [], fnames = numpy.array(afname), \
                                                    custom = "Upweling maxima", fill = False, minorgrid = 'hour', datetype = datetype)
    else:
        utils.display_data.display_temperatures(numpy.array(atime), numpy.array(aresults), [], fnames = numpy.array(afname), \
                                                    custom = "", fill = False, minorgrid = 'hour', datetype = datetype)

    return [a_max, a_min, afname]

# end plot_Upwelling_one_fig


def read_Upwelling_files(ppath, timeint, timeavg = None, subplot = None, fft = False):
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

    print "Start read_Upwelling_files()"
    startdate = timeint[0]
    enddate = timeint[1]
    dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
    start_num = date2num(dt)
    dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
    end_num = date2num(dt)

    # funits = "Hz"
    funits = "cph"
    # tunits = "sec"
    tunits = "day"

    # Separate directories from files
    base, dirs, files = iter(os.walk(ppath)).next()

    if timeavg == None:

        moving_avg = window_hour
    else:
        moving_avg = timeavg

    # draw windrose only once
    dr_windrose = False

    if len(dirs) == 0 :
        dirs = [ppath]

    for path in dirs:
        if len(dirs) > 1 :
            dateTime, temp, results, k , fnames = readTempHoboFiles.read_files(moving_avg, windows[1], [start_num, end_num], ppath + '/' + path)
        else:
            dateTime, temp, results, k , fnames = readTempHoboFiles.read_files(moving_avg, windows[1], [start_num, end_num], path)

        HOBOdateTimeArr = dateTime
        HOBOresultsArr = results
        HOBOtempArr = temp


        difflines = False

        if len(fnames) > 0:
            fn = fnames[0][fnames[0].find("_") + 1:]
        # else:
        #    fn = fnames[0][fnames[0].find("_") + 1:]
        zoneName, fileExtension = os.path.splitext(fn)

        for i in range(1, len(temp[0])):
            if temp[0][i] == 0.0:
                print "i = %d, t=0, date = %f" % (i, dateTime[0][i])

        t_sd = temp[0][1:].std()
        t_avg = temp[0][1:].mean()
        t_min = temp[0][1:].min()
        t_max = temp[0][1:].max()
        t_iqr = stat.interquartile_range(temp[0][1:], 25, 75)
        # print "Zone: %s, SD=%2.2f, Min=%2.2f, Max=%2.2f, extreme=%2.2f" % (zoneName, t_sd, t_min, t_max, t_max - t_min)
        print "Zone: %s, SD=%2.2f, Min=%2.2f, Max=%2.2f, IQR=%2.2f" % (zoneName, t_sd, t_min, t_max, t_iqr)

        # Plot temperature time series time averages or not
        if not fft:
            if timeavg != None:
                utils.display_data.display_temperatures(HOBOdateTimeArr, HOBOresultsArr, k, fnames = fnames, difflines = difflines, custom = zoneName)
            else:
                utils.display_data.display_temperatures(HOBOdateTimeArr, HOBOtempArr, k, fnames = fnames, difflines = difflines, custom = zoneName)

            if len(HOBOdateTimeArr) <= 9 and subplot != None:
                utils.display_data.display_temperatures_subplot(HOBOdateTimeArr, HOBOtempArr, HOBOresultsArr, k, fnames = fnames, yday = yday, delay = delay)
            # end if len
        else:
            # fft
            numseg = 10
            draw = False
            title = "Toronto Waterfront: %s" % zoneName
            dat = [HOBOdateTimeArr[0][1:], HOBOtempArr[0][1:]]  # skip first value because is usually 0
            log = True
            # log = False
            # ylabel = "Spectral Density ($^oC$/cph$)"
            ylabel = "Amplitude ($^oC$)"
            [Time, y, x05, x95] = spectral_analysis.doSpectralAnalysis(dat, zoneName, ylabel , title, draw, window = "hanning", num_segments = numseg, tunits = tunits, funits = funits, b_wavelets = False, log = log)
        # end if fft

    # end (for path)

    return dateTime, results, fnames, tunits, zoneName




def plot_weather_data(date, weather_path, wfile, windrose):
        # Plot weather related variables if required
        start_num = date[0]
        end_num = date[1]
        ifile = open(weather_path + '/' + wfile, 'rb')
        wreader = csv.reader(ifile, delimiter = ',', quotechar = '"')
        [temp, dateTime, windDir, windSpd, press] = envir.read_stringdatefile(wreader)
        ifile.close()

        # 2) select the dates
        [wtemp, wdateTime, windDir, windSpd, press] = envir.select_dates_string(start_num, end_num, dateTime, temp, windDir, windSpd, press)

        # envir.display_twinx("Filtered temperature, wind direction & speed", ' wind dir deg*10/wind speed Km/h', "Filtered temperature ($^oC$)", \
        #                    [wdateTime[1:], wdateTime[1:]], [windDir[1:], windSpd[1:]], [HOBOdateTimeArr_res[0][1:]], [Filtered_data[0][1:]], \
        #                    ['g', 'b'], ['r'])

        ########################################################
        #  multipy by 10 the degrees FROM which the wind blows
        ########################################################
        windir = map(lambda x: x * 10, windDir[1:])
        winspd = windSpd[1:]
        envir.display_twinx("Filtered water temperature, wind direction", "Filtered temperature ($^oC$)", 'wind dir ($^o$)', \
                            [wdateTime[1:]], [wtemp[1:]], [wdateTime[1:]], [windir], \
                            ['r'], ['b', 'g'], [" Temp", "Wind dir"], linewidth1 = [1.8], linewidth2 = [0.6])
        if windrose:
            tor_harb_windrose.draw_windrose(windir, winspd, 'bar', loc = (1, 0.05), fontsize = 16, unit = "[km/h]")
            plt.show()
        # end if

def subplot_weather_data(str_date, date, water_path, harbour_path, weather_path, cloud_path, lake_file, weather_file, filter = False):
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

    print "Start wind_airpress_airtemp_water_temp()"
    start_num = date[0]
    end_num = date[1]

    # 1) read all lake data
    base, dirs, files = iter(os.walk(water_path)).next()
    sorted_files = sorted(files, key = lambda x: x.split('.')[0])

    dateTimeArr = numpy.zeros(len(sorted_files), dtype = numpy.ndarray)
    tempArr = numpy.zeros(len(sorted_files), dtype = numpy.ndarray)
    resultsArr = numpy.zeros(len(sorted_files), dtype = numpy.ndarray)
    k = numpy.zeros(len(sorted_files), dtype = numpy.ndarray)
    i = 0
    for fname in sorted_files:
        dateTime, temp, results = readTempHoboFiles.get_data_from_file(fname, window_hour, windows[1], timeinterv = date, rpath = water_path)
        maxidx = 30000
        dateTimeArr[i] = numpy.append(dateTimeArr[i], dateTime[:maxidx])
        resultsArr[i] = numpy.append(resultsArr[i], results[:maxidx])
        tempArr[i] = numpy.append(tempArr[i], temp[:maxidx])
        k[i] = numpy.append(k[i], i)
        i += 1
    # end for

    # 1') read all harbour data (EG + Jarvis Dock
    base, dirs, files = iter(os.walk(harbour_path)).next()
    sorted_files = sorted(files, key = lambda x: x.split('.')[0])

    TH_dateTimeArr = numpy.zeros(len(sorted_files), dtype = numpy.ndarray)
    TH_tempArr = numpy.zeros(len(sorted_files), dtype = numpy.ndarray)
    TH_resultsArr = numpy.zeros(len(sorted_files), dtype = numpy.ndarray)
    TH_k = numpy.zeros(len(sorted_files), dtype = numpy.ndarray)
    i = 0
    for fname in sorted_files:
        dateTime, temp, results = readTempHoboFiles.get_data_from_file(fname, window_hour, windows[1], timeinterv = date, rpath = harbour_path)
        maxidx = 30000
        TH_dateTimeArr[i] = numpy.append(TH_dateTimeArr[i], dateTime[:maxidx])
        TH_resultsArr[i] = numpy.append(TH_resultsArr[i], results[:maxidx])
        TH_tempArr[i] = numpy.append(TH_tempArr[i], temp[:maxidx])
        TH_k[i] = numpy.append(TH_k[i], i)
        i += 1
    # end for




    # plot the temperature not the smoothed ones - ONLY for test
    datetype = 'dayofyear'
    # display_data.display_temperatures(dateTimeArr, tempArr, k, fnames = sorted_files, custom = "Temperature Toronto Waterfront Zones $^oC$", \
    #                                  datetype = datetype)
    # display_data.display_img_temperatures(dateTimeArr, tempArr, resultsArr, k, tick, maxdepth, firstlogdepth, maxtemp, fontsize = 18, datetype = datetype)

    # read one depth lake data
    print "Reading file %s" % lake_file
    dateTime, temp, results = readTempHoboFiles.get_data_from_file(lake_file, window_hour, windows[1], date, water_path)
    HOBOdateTimeArr = dateTime
    HOBOresultsArr = results
    HOBOtempArr = temp

    # 2) read weather data
    wfile = open(weather_path + '/' + weather_file, 'rb')
    wreader = csv.reader(wfile, delimiter = ',', quotechar = '"')
    [temp, dateTime, windDir, windSpd, press] = envir.read_stringdatefile(wreader)
    wfile.close()
    # 3) select the dates
    [wtemp, wdateTime, windDir, windSpd, press] = envir.select_dates_string(start_num, end_num, dateTime, temp, windDir, windSpd, press)

    # 4) interplate every 10 minutes
    [iwtemp, iwdateTime, iwindDir, iwindSpd, iPress] = envir.interpolateData(10, wtemp, wdateTime, windDir, windSpd, press)

    dataArray = numpy.array([iwtemp, iwindDir, iwindSpd, iPress, HOBOtempArr])
    timeArray = numpy.array([iwdateTime, iwdateTime, iwdateTime, iwdateTime, HOBOdateTimeArr])
    names = numpy.array(["Air Temp", "Wind Dir", "Wind spd", "Atm press", "Water temp"])
    labels = numpy.array(["Air Temp ($^\circ$C)", "Wind Dir ($^\circ$)", "Wind spd (km/h)", "Atm press (hPa)", "Water Temp ($^\circ$C)"])

    # 5) Time domain analysis
    lowcut = 1.0 / (24 * 10) / 3600
    highcut = 1.0 / (24 * 3) / 3600
    tunits = 'day'

    if tunits == 'day':
        factor = 86400
    elif tunits == 'hour':
        factor = 3600
    else:
        factor = 1

    # 6 Filered data
    if filter:
        Filtered_data = numpy.zeros(len(dataArray), dtype = numpy.ndarray)
        delay = numpy.zeros(len(dataArray) + 1, dtype = numpy.ndarray)
        fnames = numpy.array(['air temp', 'wind dir', 'wind spd', 'air press', 'water temp 10 m'])
        k = [1, 2, 3, 4, 5]

        i = 0
        btype = 'band'
        yday = True
        debug = False
        order = None
        gpass = 9
        astop = 32
        recurse = True

        for data in dataArray:
            fs = 1.0 / ((timeArray[i][2] - timeArray[i][1]) * factor)
            # Filtered_data[i] = filters.fft_bandpassfilter(data, fs, lowcut, highcut)

            Filtered_data[i], w, h, N, delay[i] = filters.butterworth(data, btype, lowcut, highcut, fs, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = True, debug = debug)
            if len(Filtered_data[i]) != len(timeArray[i]):
                timeArray[i] = sp.signal.resample(timeArray[i], len(Filtered_data[i]))
            i += 1
        # end for

        # superimposed filtered data for 1-3 days oscillation freq
        difflines = True
        print "Start display wind_airpress_airtemp_water_temp plot "
        utils.display_data.display_temperatures(timeArray, Filtered_data, k, fnames = fnames, difflines = difflines, custom = "Weather variables and water temperature")
        # 7) Draw subplot
        # rcParams['text.usetex'] = True
        custom = numpy.array(['Air T($^\circ$C)', 'Wind dir', 'Wind spd(km/h)', 'Air p(hPa)', 'Water T($^\circ$C)'])
        # ToDO: Add short and long radiation
        print "Start display wind_airpress_airtemp_water_temp subplots "
        utils.display_data.display_temperatures_subplot(timeArray, dataArray, dataArray, k, fnames = fnames, custom = custom)
    # end if filter


    # 8) Mixed water, air ,img data
    custom = numpy.array(['Wind spd(km/h)', 'Air (T($^\circ$C)', 'Water T($^\circ$C)', ])
    # ToDO: Add short and long radiation
    print "Start display mixed subplots "
    dateTimes1 = [iwdateTime]
    data = [utils.smooth.smoothed_by_window(iwdateTime, iwindSpd, "window_half_day")]
    varnames = ["Wind speed"]
    ylabels1 = ["Wind spd [km/h]"]
    dateTimes2 = [iwdateTime, HOBOdateTimeArr]
    ylabels2 = ["Temp. [$^\circ$C]"]
    groups = [iwtemp, HOBOresultsArr]
    groupnames = ['Air Temp', 'Water Temp']
    dateTimes3 = [dateTimeArr, TH_dateTimeArr]
    ylabels3 = ["Depth [m]", "Depth [m]"]
    imgs = [resultsArr, TH_resultsArr]
    t11 = ['0', '4', '9', '13', '18', '22', '27']
    t12 = [27, 22.5, 18, 13.5, 9, 4.5, 0]
    t21 = ['0', '3', '6', '9']
    t22 = [9, 6, 3, 0]
    tick = [[t11, t12], [t21, t22]]
    maxdepth = [27, 9]
    firstlogdepth = [3, 0]
    maxtemp = [25, 26]
    mintemps = [0, 0]
    mindepths = [3, 0]
    utils.display_data.display_mixed_subplot(dateTimes1 = dateTimes1, data = data, varnames = varnames, ylabels1 = ylabels1,
                                       dateTimes2 = dateTimes2, groups = groups, groupnames = groupnames, ylabels2 = ylabels2,
                                       dateTimes3 = dateTimes3, imgs = imgs, ylabels3 = ylabels3, ticks = tick, maxdepths = maxdepth, \
                                        mindepths = mindepths, mintemps = mintemps, firstlogs = firstlogdepth, maxtemps = maxtemp,
                          fnames = None, revert = False, custom = None, maxdepth = None, tick = None, firstlog = None, yday = True, \
                          title = False, grid = False, limits = None, sharex = True, fontsize = 18)

    # 9) Draw radiation data
    print "Start display  Atmospheric radiation "
    var1 = 'swgnt'
    var2 = 'lwgnt'
    var3 = 'cldtot'
    ix = 0
    iy = 1
    timeidx = [0, 23]
    dateTime1, results1 = hdf.read_hdf_dir(cloud_path, var1, ix, iy, timeidx, str_date[0], str_date[1])
    dateTime2, results2 = hdf.read_hdf_dir(cloud_path, var2, ix, iy, timeidx, str_date[0], str_date[1])
    dateTime3, results3 = hdf.read_hdf_dir(cloud_path, var3, ix, iy, timeidx, str_date[0], str_date[1])


    utils.display_data.display_temperatures([dateTime1, dateTime2, dateTime3], [results1, results2, results3 * 100], [1, 2, 3],
                                      fnames = [var1, var2, var3], difflines = False, custom = "Radiation data (W/m$^2$)")

    # 10) Temperature profiles in lake and harbour
    print "Temperature profiles in lake and harbour"

    dt = datetime.strptime('13/09/03 00:00:00', "%y/%m/%d %H:%M:%S")
    dtnum1 = matplotlib.dates.date2num(dt)
    dt = datetime.strptime('13/09/06 00:00:00', "%y/%m/%d %H:%M:%S")
    dtnum2 = matplotlib.dates.date2num(dt)
    profiledates = [ dtnum1, dtnum2]

    utils.display_data.display_avg_vertical_temperature_profiles_err_bar_range(dateTimeArr, resultsArr, startdepth = 3, profiledates = profiledates, revert = False, legendloc = 4)
    utils.display_data.display_avg_vertical_temperature_profiles_err_bar_range(TH_dateTimeArr, TH_resultsArr, startdepth = 0 , profiledates = profiledates, revert = False, legendloc = 4)


def plot_buterworth_filtered_data(HOBOdateTimeArr, HOBOtempArr, fnames, k, filter, ylim = None, stats = False):
        # Plot BAND buterworth filtered time series to capture only the frequencies of interest.: diurnal , poincare, upwelling etc.

        lowcut = filter[0]
        highcut = filter[1]
        tunits = 'day'
        if tunits == 'day':
            factor = 86400
        elif tunits == 'hour':
            factor = 3600
        else:
            factor = 1

        yday = True
        debug = False
        order = None
        gpass = 9
        astop = 32
        recurse = True

        Filtered_data = numpy.zeros(len(HOBOdateTimeArr) , dtype = numpy.ndarray)
        HOBOdateTimeArr_res = numpy.zeros(len(HOBOdateTimeArr), dtype = numpy.ndarray)
        delay = numpy.zeros(len(HOBOdateTimeArr) , dtype = numpy.ndarray)
        i = 0
        btype = 'band'
        for data in HOBOdateTimeArr:
            fs = 1.0 / ((HOBOdateTimeArr[i][2] - HOBOdateTimeArr[i][1]) * factor)
            Filtered_data[i], w, h, N, delay[i] = filters.butterworth(HOBOtempArr[i], btype, lowcut, highcut, fs, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = True, debug = debug)
            if len(Filtered_data[i]) != len(HOBOdateTimeArr[i]):
                HOBOdateTimeArr_res[i] = scipy.signal.resample(HOBOdateTimeArr[i], len(Filtered_data[i]))
            else :
                HOBOdateTimeArr_res[i] = HOBOdateTimeArr[i]

            i += 1
        # end for data

        print "Start display filtered data"
        for i in range(0, len(HOBOdateTimeArr_res)):

            # superimposed filtered data for 1-3 days oscillation freq
            difflines = False
            filtstr = " filter: %.0f - %.0f (h)" % (1. / filter[1] / 3600, 1. / filter[0] / 3600)

            if len(fnames) > 0:
                fn = fnames[i][fnames[i].find("_") + 1:]
            zoneName, fileExtension = os.path.splitext(fn)
            custom = " %s - %s" % (zoneName, filtstr)
            # [300:-100] eliminate the bad ends generated by the filter


            # Plot BAND buterworth filtered time series to capture only the frequencies of interest.: diurnal , poincare, upwelling etc.
            utils.display_data.display_temperatures([HOBOdateTimeArr_res[i][300:-100]], [Filtered_data[i][300:-100]], k, fnames = fnames[i],
                                              difflines = difflines, custom = custom, ylim = ylim)

        # statistics SD, max, avg, min
        if stats:
            f_sd = Filtered_data[0][300:-100].std()
            f_avg = Filtered_data[0][300:-100].mean()
            f_min = Filtered_data[0][300:-100].min()
            f_max = Filtered_data[0][300:-100].max()
            # print "SD=%f Avg=%f Min=%f Max=%f" % (f_sd, f_avg, f_min, f_max)
            print "Filtered data SD=%f" % (f_sd)


# end plot_buterworth_filtered_data

def draw_avg_temp_profile_with_variab_bars(datetime, tempdata):
    pass
