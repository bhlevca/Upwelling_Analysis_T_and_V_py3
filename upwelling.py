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
import display_data
import read_RBR
import readTempHoboFiles
# import scikits.bootstrap as bootstrap
import env_can_weather_data_processing as envir
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
import smooth

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

    mean_month = smooth.smoothfit(dateTime, temp, nspan, windows[1])

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
        display_data.display_temperatures_peaks([time[i][trim:-trim], time[i][trim:-trim]], [month_mean[trim:-trim], temp[i][trim:-trim]],
                                                       _max, _min, [], fnames = ['30 day mean', fnames[i]], custom = zoneName, fill = True)



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

def read_Upwelling_files(ppath, timeint, timeavg = None, subplot = None, filter = None, fft = False, stats = False, with_weather = False):
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

    for path in dirs:
        dateTime, temp, results, k , fnames = readTempHoboFiles.read_files(moving_avg, windows[1], [start_num, end_num], ppath + '/' + path)
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


        if not fft:
            if timeavg != None:
                display_data.display_temperatures(HOBOdateTimeArr, HOBOresultsArr, k, fnames = fnames, difflines = difflines, custom = zoneName)
            else:
                display_data.display_temperatures(HOBOdateTimeArr, HOBOtempArr, k, fnames = fnames, difflines = difflines, custom = zoneName)

            if len(HOBOdateTimeArr) <= 9 and subplot != None:
                display_data.display_temperatures_subplot(HOBOdateTimeArr, HOBOtempArr, HOBOresultsArr, k, fnames = fnames, yday = yday, delay = delay)
            # end if len
        else:
            # fft
            numseg = 10
            draw = False
            title = "Toronto Waterfront: %s" % zoneName
            dat = [HOBOdateTimeArr[0][1:], HOBOtempArr[0][1:]]  # skip first value because is usually 0
            log = True
            # ylabel = "Spectral Density ($^oC$/cph$)"
            ylabel = "Amplitude ($^oC$)"
            [Time, y, x05, x95] = spectral_analysis.doSpectralAnalysis(dat, zoneName, ylabel , title, draw, window = "hanning", num_segments = numseg, tunits = tunits, funits = funits, b_wavelets = False, log = log)
        # end if fft

        if filter != None:

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
            # superimposed filtered data for 1-3 days oscillation freq
            difflines = False
            filtstr = " filter: %.0f - %.0f (h)" % (1. / filter[1] / 3600, 1. / filter[0] / 3600)
            custom = " %s - %s" % (zoneName, filtstr)
            # [300:-100] eliminate the bad ends generated by the filter
            if with_weather:
                weather_path = '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE deployment 18-07-2012/Data/ClimateData/all'
                wfile = open(weather_path + '/eng-hourly-04012012-11302012-all.csv', 'rb')

                wreader = csv.reader(wfile, delimiter = ',', quotechar = '"')
                [temp, dateTime, windDir, windSpd, press] = envir.read_stringdatefile(wreader)
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
                                    [HOBOdateTimeArr_res[0][1:]], [Filtered_data[0][1:]], [wdateTime[1:]], [windir], \
                                    ['r'], ['b', 'g'], [zoneName + " Temp", "Wind dir"], linewidth1 = [1.8], linewidth2 = [0.6])
                envir.display_twinx("Filtered water temperature, air temp", "Filtered temperature ($^oC$)", 'air temp ($^oC$)', \
                                    [HOBOdateTimeArr_res[0][1:]], [Filtered_data[0][1:]], [wdateTime[1:]], [wtemp[1:]], \
                                    ['r'], ['b', 'g'], [zoneName + " Temp", "Wind dir"], linewidth1 = [1.8], linewidth2 = [0.6])
                if not dr_windrose:
                    tor_harb_windrose.draw_windrose(windir, winspd, 'bar', fontsize = 12)
                    dr_windrose = True
            else:
                display_data.display_temperatures([HOBOdateTimeArr_res[0][300:-100]], [Filtered_data[0][300:-100]], k, fnames = fnames,
                                              difflines = difflines, custom = custom, ylim = [-6, 6])

            # statistics SD, max, avg, min
            if stats:
                f_sd = Filtered_data[0][300:-100].std()
                f_avg = Filtered_data[0][300:-100].mean()
                f_min = Filtered_data[0][300:-100].min()
                f_max = Filtered_data[0][300:-100].max()
                # print "SD=%f Avg=%f Min=%f Max=%f" % (f_sd, f_avg, f_min, f_max)
                print "Filtered data SD=%f" % (f_sd)


        # end filter
        calculate_Upwelling_indices(dateTime, results, fnames, tunits, zoneName)
    # end (for path)
