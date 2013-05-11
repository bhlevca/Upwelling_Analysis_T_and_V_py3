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
        UCI_mean = uci.sum() / len(uci)
        print "name=%s UCI=%f" % (fnames[i], UCI_mean)
        display_data.display_temperatures_peaks([time[i][trim:-trim], time[i][trim:-trim]], [month_mean[trim:-trim], temp[i][trim:-trim]],
                                                       _max, _min, [], fnames = ['30 day mean', fnames[i]], custom = zoneName, fill = True)



def calculate_correlation():
    pass


def read_Upwelling_files(ppath, timeint, timeavg = None, subplot = None, filter = None, fft = False, stats = False, with_weather = False):
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')



    data = read_csv.read_csv('/home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/SelectedZones.csv', 1, [9, 10])
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(data[0], data[1])
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(data[0], data[1], x_label = "UIA ($^oC$ days)", y_label = "Temperature ($^oC$)", title = "Temperature vs. Upwelling Integrated Anomaly Index", \
                          slope = slope, intercept = intercept, r_value = r_value, p_value = p_value)

    data = read_csv.read_csv('/home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/SelectedZones.csv', 1, [9, 11])
    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(data[0], data[1])
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
    stat.plot_regression(data[0], data[1], x_label = "UCI ($^oC$/days)", y_label = "Temperature ($^oC$)", title = "Temperature vs. Upwelling Cooling Intensity Index", \
                          slope = slope, intercept = intercept, r_value = r_value, p_value = p_value)
    os.abort()

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

        t_sd = temp[0].std()
        t_avg = temp[0].mean()
        t_min = temp[0].min()
        t_max = temp[0].max()
        print "Zone: %s, SD=%f" % (zoneName, t_sd)


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
            [Time, y, x05, x95] = spectral_analysis.doSpectralAnalysis(dat, zoneName, fn, title, draw, window = "hanning", num_segments = numseg, tunits = tunits, funits = funits, b_wavelets = False, log = log)
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
