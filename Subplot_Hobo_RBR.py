import csv
import numpy
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
import env_can_weather_data_processing as envir

sys.path.insert(0, '/software/SAGEwork/Seiches')
import fft.filters as filters

windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
window_6hour = 30 * 6
window_hour = 30
window_day = 30 * 24
window_half_day = 30 * 12


'''
Logging start 12/07/16 00:00:00
Logging end   12/11/22 07:49:04
'''

# turn off warning in polyfit
import warnings
warnings.simplefilter('ignore', numpy.RankWarning)
import smooth


def read_LOntario_files(paths, fnames, dateinterval):

    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

    # get hobo file
    hobofilename = fnames[0]  # '18_2393005.csv'
    print "Reading file %s" % hobofilename
    dateTime, temp, results = readTempHoboFiles.get_data_from_file(hobofilename, window_hour, windows[1], dateinterval, paths[0])
    HOBOdateTimeArr = dateTime
    HOBOresultsArr = results
    HOBOtempArr = temp

    # get RBR file
    RBRfilename = fnames[1]  # '019513.dat'
    print "Reading file %s" % RBRfilename
    dateTime, temp, results = read_RBR.get_data_from_file(RBRfilename, window_hour, windows[1], [start_num, end_num], paths[1])
    # index is specific to the files read and needs to be modified for other readings
    RBRdateTimeArr = dateTime
    RBRresultsArr = results
    RBRtempArr = temp

    k = [[0, 0], [0, 1]]
    print "Start display"
    display_data.display_temperatures_subplot([HOBOdateTimeArr, RBRdateTimeArr], [HOBOtempArr, RBRtempArr], [HOBOresultsArr, RBRresultsArr], k, fnames = ["Hobo-10m", "RBR-10m"])

    display_data.display_temperatures([HOBOdateTimeArr, RBRdateTimeArr], [HOBOtempArr, RBRtempArr], [HOBOresultsArr, RBRresultsArr], k, fnames = ["Hobo-10m", "RBR-10m"])

    tunits = 'day'

    if tunits == 'day':
        factor = 86400
    elif tunits == 'hour':
        factor = 3600
    else:
        factor = 1



    # Poincare 17h filter
    highcut = 1.0 / 16.5 / 3600
    lowcut = 1.0 / 17.5 / 3600
    legend1 = ["Hobo-10m-filter-17h", "RBR-10m-filter-17h"]
    btype = 'band'

    fs1 = 1.0 / ((HOBOdateTimeArr[1] - HOBOdateTimeArr[0]) * factor)
    # data1 = filters.fft_bandpassfilter(HOBOtempArr, fs1, lowcut, highcut)
    data1, w, h, N, delay1 = filters.butterworth(HOBOtempArr, btype, lowcut, highcut, fs1, output = 'zpk')
    # data1, w, h, N, delay1 = filters.firwin(HOBOtempArr, btype, lowcut, highcut, fs1, output = 'ba')

    fs2 = 1.0 / ((RBRdateTimeArr[1] - RBRdateTimeArr[0]) * factor)
    # data2 = filters.fft_bandpassfilter(RBRtempArr, fs2, lowcut, highcut)
    data2, w, h, N, delay2 = filters.butterworth(RBRtempArr, btype, lowcut, highcut, fs2, output = 'zpk')
    # data2, w, h, N, delay2 = filters.firwin(RBRtempArr, btype, lowcut, highcut, fs2, output = 'ba')

    display_data.display_temperatures_subplot([HOBOdateTimeArr, RBRdateTimeArr], [data1, data2], [HOBOresultsArr, RBRresultsArr], k, fnames = legend1, yday = True, delay = [delay1, delay2])
    display_data.display_temperatures([numpy.subtract(HOBOdateTimeArr, delay1), numpy.subtract(RBRdateTimeArr, delay2)], [data1, data2], [HOBOresultsArr, RBRresultsArr], k, fnames = legend1)


    # Kelvin?
    lowcut = 1.0 / (24 * 10) / 3600
    highcut = 1.0 / (24 * 3) / 3600
    legend2 = ["Hobo-10m-filter-3-10 days", "RBR-10m-filter-3-10 days"]
    fs3 = 1.0 / ((HOBOdateTimeArr[1] - HOBOdateTimeArr[0]) * factor)
    # data3 = filters.fft_bandpassfilter(HOBOtempArr, fs3, lowcut, highcut)
    data3, w, h, N, delay3 = filters.butterworth(HOBOtempArr, btype, lowcut, highcut, fs3, output = 'zpk')
    # data3, w, h, N, delay3 = filters.firwin(HOBOtempArr, btype, lowcut, highcut, fs3, output = 'ba')

    fs4 = 1 / ((RBRdateTimeArr[1] - RBRdateTimeArr[0]) * factor)
    # data4 = filters.fft_bandpassfilter(RBRtempArr, fs4, lowcut, highcut)
    data4, w, h, N, delay4 = filters.butterworth(RBRtempArr, btype, lowcut, highcut, fs4, output = 'zpk')
    # data4, w, h, N, delay4 = filters.firwin(RBRtempArr, btype, lowcut, highcut, fs4, output = 'ba')

    display_data.display_temperatures_subplot([HOBOdateTimeArr, RBRdateTimeArr], [data3, data4], [HOBOresultsArr, RBRresultsArr], k, fnames = legend2, yday = True, delay = [delay3, delay4])
    display_data.display_temperatures([numpy.subtract(HOBOdateTimeArr, delay3), numpy.subtract(RBRdateTimeArr, delay4)], [data3, data4], [HOBOresultsArr, RBRresultsArr], k, fnames = legend2)



    Data = [data1, data2, data3, data4]
    Result = [HOBOresultsArr, RBRresultsArr, HOBOresultsArr, RBRresultsArr]
    legend = [legend1[0], legend1[1], legend2[0], legend2[1]]
    timeint_subplot = [HOBOdateTimeArr, RBRdateTimeArr, HOBOdateTimeArr, RBRdateTimeArr]
    timeint = [numpy.subtract(HOBOdateTimeArr, delay1), numpy.subtract(RBRdateTimeArr, delay2), numpy.subtract(HOBOdateTimeArr, delay3), numpy.subtract(RBRdateTimeArr, delay4)]

    display_data.display_temperatures_subplot(timeint, Data, Result, k, fnames = legend, yday = True, delay = [delay1, delay2, delay3, delay4])
    display_data.display_temperatures(timeint, Data, Result, k, fnames = legend)


def read_Tor_Harbour_files():
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

    startdate = '12/07/19 00:00:00'
    enddate = '12/10/24 00:00:00'
    dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
    start_num = date2num(dt)
    dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
    end_num = date2num(dt)


    # get hobo file

    paths = ['/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed/upwelling-LO-21-10-37-38',
            '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed/upwelling-LO-21-15-13',
            '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed/upwelling-LO-21-15-14',
            '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed/upwelling-LO-21-17-2',
            '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed/upwelling-LO-28-21-34-32-49-50'
            ]

    for path in paths:
        dateTime, temp, results, k , fnames = readTempHoboFiles.read_files(window_hour, windows[1], [start_num, end_num], path)
        HOBOdateTimeArr = dateTime
        HOBOresultsArr = results
        HOBOtempArr = temp

        # Kelvin?
        lowcut = 1.0 / (24 * 10) / 3600
        highcut = 1.0 / (24 * 3) / 3600
        tunits = 'day'

        if tunits == 'day':
            factor = 86400
        elif tunits == 'hour':
            factor = 3600
        else:
            factor = 1

        Filtered_data = numpy.zeros(len(HOBOdateTimeArr) + 1, dtype = numpy.ndarray)
        i = 0
        btype = 'band'
        for data in HOBOdateTimeArr:
            fs = 1.0 / ((HOBOdateTimeArr[i][2] - HOBOdateTimeArr[i][1]) * factor)
            # Filtered_data[i] = filters.fft_bandpassfilter(HOBOtempArr[i], fs, lowcut, highcut)
            Filtered_data[i], w, h, N = filters.butterworth(HOBOtempArr[i], btype, lowcut, highcut, fs)
            i += 1



        # get hobo file
        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE-Apr-May_2012-Thermistor_chain/csv_processed'
        hobofilename = '18_2393005.csv'
        print "Reading file %s" % hobofilename
        dateTime, temp, results = readTempHoboFiles.get_data_from_file(hobofilename, window_hour, windows[1], [start_num, end_num], path)

        HOBOdateTimeArr = numpy.resize(HOBOdateTimeArr, len(HOBOdateTimeArr) + 1)
        HOBOresultsArr = numpy.resize(HOBOresultsArr, len(HOBOresultsArr) + 1)
        HOBOtempArr = numpy.resize(HOBOtempArr, len(HOBOtempArr) + 1)

        HOBOdateTimeArr[len(HOBOdateTimeArr) - 1] = dateTime
        HOBOresultsArr[len(HOBOresultsArr) - 1] = results
        HOBOtempArr[len(HOBOtempArr) - 1] = temp


        fnames = numpy.append(fnames, hobofilename)

        fs = 1.0 / ((dateTime[2] - dateTime[1]) * factor)

        btype = 'band'
        # Filtered_data[len(HOBOresultsArr) - 1] = filters.fft_bandpassfilter(temp, fs, lowcut, highcut)
        Filtered_data[len(HOBOresultsArr) - 1], w, h, N = filters.butterworth(temp, btype, lowcut, highcut, fs)


        print "Start display"
        display_data.display_temperatures_subplot(HOBOdateTimeArr, HOBOtempArr, HOBOresultsArr, k, fnames = fnames)

        # superimposed filtered data for 1-3 days oscillation freq
        difflines = True
        display_data.display_temperatures(HOBOdateTimeArr, Filtered_data, HOBOresultsArr, k, fnames = fnames, difflines = difflines)
    # end for path


def wind_airpress_airtemp_water_temp():
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

    startdate = '12/07/19 00:00:00'
    enddate = '12/10/24 00:00:00'
    dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
    start_num = date2num(dt)
    dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
    end_num = date2num(dt)


    # get hobo file
    path = '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE-Apr-May_2012-Thermistor_chain/csv_processed'
    hobofilename = '18_2393005.csv'
    print "Reading file %s" % hobofilename
    dateTime, temp, results = readTempHoboFiles.get_data_from_file(hobofilename, window_hour, windows[1], [start_num, end_num], path)
    HOBOdateTimeArr = dateTime
    HOBOresultsArr = results
    HOBOtempArr = temp

    weather_path = '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE deployment 18-07-2012/Data/ClimateData'
    wfile = open(weather_path + '/eng-hourly-07012012-11302012.csv', 'rb')

    wreader = csv.reader(wfile, delimiter = ',', quotechar = '"')
    [temp, dateTime, windDir, windSpd, press] = envir.read_stringdatefile(wreader)
    # 2) select the dates
    [wtemp, wdateTime, windDir, windSpd, press] = envir.select_dates_string(start_num, end_num, dateTime, temp, windDir, windSpd, press)
    envir.display("temperature", ' temperature ($^\circ$C)', [wdateTime], [wtemp], ['r'])
    envir.display("wind direction & speed", ' wind dir deg*10/wind speed Km/h', [wdateTime, wdateTime], [windDir, windSpd], ['r', 'b'])
    # display("wind speed", ' wind speed km/h', [wdateTime], [windSpd], ['r'])
    plt = envir.display("pressure", ' air pressure  kPa', [wdateTime], [press], ['r'])
    # call show() so that the window does not disappear.
    plt.show()
    # 3) interplate every 10 minutes
    # dirList = os.listdir(path_in)
    [iwtemp, iwdateTime, iwindDir, iwindSpd, iPress] = envir.interpolateData(10, wtemp, wdateTime, windDir, windSpd, press)

    dataArray = numpy.array([iwtemp, iwindDir, iwindSpd, iPress, HOBOtempArr])
    timeArray = numpy.array([iwdateTime, iwdateTime, iwdateTime, iwdateTime, HOBOdateTimeArr])

    lowcut = 1.0 / (24 * 10) / 3600
    highcut = 1.0 / (24 * 3) / 3600
    tunits = 'day'

    if tunits == 'day':
        factor = 86400
    elif tunits == 'hour':
        factor = 3600
    else:
        factor = 1

    Filtered_data = numpy.zeros(len(dataArray), dtype = numpy.ndarray)
    fnames = numpy.array(['air temp', 'wind dir', 'wind spd', 'air press', 'water temp 10 m'])
    k = [1, 2, 3, 4, 5]


    i = 0
    btype = 'band'
    for data in dataArray:
        fs = 1.0 / ((timeArray[i][2] - timeArray[i][1]) * factor)
        # Filtered_data[i] = filters.fft_bandpassfilter(data, fs, lowcut, highcut)
        Filtered_data[i], w, h, N = filters.butterworth(data, btype, lowcut, highcut, fs)

        i += 1


    custom = numpy.array(['Air temp.($^\circ$C)', 'Wind dir.', 'Wind speed (m/s)', 'Air pres. (hPa)', 'Water temp.($^\circ$C)'])
    print "Start display"
    display_data.display_temperatures_subplot(timeArray, dataArray, dataArray, k, fnames = fnames, custom = custom)

    # superimposed filtered data for 1-3 days oscillation freq
    difflines = True
    display_data.display_temperatures(timeArray, Filtered_data, Filtered_data, k, fnames = fnames, difflines = difflines, custom = custom)


def find_depthoftemp(isotemp, waterdepth, top_log_depth, delta_L, dateTimeArr, tempArr, revert = False, name = "default"):
    # first dimension is the number of loggers/files
    depthArr = numpy.zeros(numpy.shape(dateTimeArr[0]))
    missing = numpy.zeros(numpy.shape(dateTimeArr[0]))
    firstlog_depth = waterdepth - len(dateTimeArr)

    debug = False
    if debug:
        ofile = open("/tmp" + '/' + name + ".csv", "wb")
        writer = csv.writer(ofile, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
        y = 0

    for i in range(0, len(dateTimeArr[0])):
        for j in range(0, len(dateTimeArr)):
            if j == 0:
                depthArr[i] = 0
                continue;

            # Loop for shorter series (sensor malfuction) that need interpolation
            # Conditions:
            #    1- the  first and timeseries must be good
            #    2 - The bad timeseries can not be last or first (actually is implied from 1.
            try:
                if (i > len(dateTimeArr[j]) - 1) and (i < len(dateTimeArr[0])):
                    prev = tempArr[j - 1][i]
                    next = tempArr[j + 1][i]

                    temp = (prev + next) / 2.0
                    missing[i] = temp
                else:
                    temp = tempArr[j][i]

                if (i > len(dateTimeArr[j - 1]) - 1) and (i < len(dateTimeArr[0])):
                    tempprev = missing[i]
                else:
                    tempprev = tempArr[j - 1][i]

                if (isotemp >= tempprev and isotemp <= temp)\
                    or (isotemp <= tempprev and isotemp >= temp):

                    # j is current depth
                    if revert:  # counted from top)
                        c = delta_L * temp / (tempprev - temp)
                        y = c * (isotemp - temp) / temp
                        depthArr[i] = j * delta_L - y + top_log_depth
                    else:  # count from bottom
                        # c = delta_L * tempprev / (tempprev - temp)
                        c = delta_L * temp / (temp - tempprev)
                        y = c * (isotemp - tempprev) / tempprev
                        depthArr[i] = waterdepth - ((j - 1) * delta_L + y)  # j-i is the correct verified formula when first looger is at bottom

            except Exception as e:
                print "Error i=%d, j=%d" % (i, j)
                print "Error %s" % e

        # end for j

        # if depth is still zero it means that the temperature is too cold or too warm
        # a weak approximation would be that the depth is that of the previous time step
        if depthArr[i] == 0 :
            depthArr[i] = depthArr[i - 1]

        if debug:
            print "i=%d, j=%d, y=%f,  depth[%d]=%f" % (i, j, y, i, depthArr[i])
            writer.writerow([i, j, y, depthArr[i]])
    # end for i
    if debug:
        ofile.close()

    return depthArr



def isoterm_oscillation(isotemp, paths, wdepths, top_log_depths, delta_Ls, dateinterval, filter = None):
    '''
    analyse the isotherm oscillation and not the temperature at a certain depth
    filter: in [Hi freq, lo freq} = > [ lo period, hi period] period in hours
    '''
    start_num, end_num = dateinterval
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')


    # get hobo files
    print "Reading path %s" % paths[0]

    dateTime, temp, results, k , fnames = readTempHoboFiles.read_files(window_hour, windows[1], dateinterval, paths[0])
    HOBOdateTimeArr = dateTime
    HOBOresultsArr = results
    HOBOtempArr = temp
    waterdepth = wdepths[0]  # m
    top_log_depth = top_log_depths[0]
    revert = True  # hobo loggers order was read reversed from top to bottom
    HOBODepthArr = find_depthoftemp(isotemp, waterdepth, top_log_depth, delta_Ls[0], HOBOdateTimeArr, HOBOtempArr, revert, "HOBO")


    # get RBR files

    print "Reading path %s" % paths[1]
    dateTime, temp, results, k , fnames = read_RBR.read_files(window_hour, windows[1], dateinterval, paths[1])
    # index is specific to the files read and needs to be modified for other readings
    RBRdateTimeArr = dateTime
    RBRresultsArr = results
    RBRtempArr = temp
    waterdepth = wdepths[1]
    top_log_depth = top_log_depths[1]
    revert = False  # RBRs are bottom read first so we need to invert
    RBRDepthArr = find_depthoftemp(isotemp, waterdepth, top_log_depth, delta_Ls[1], RBRdateTimeArr, RBRtempArr, revert, "RBR")


    k = [[0, 0], [0, 1]]
    print "Start display: isoterm_oscillation"
    fname1 = "Hobo-%d ($^\circ$C)" % isotemp
    fname2 = "RBR-%d ($^\circ$C)" % isotemp
    fnames = [fname1, fname2]

    if filter != None:
        tunits = 'day'

        if tunits == 'day':
            factor = 86400
        elif tunits == 'hour':
            factor = 3600
        else:
            factor = 1
        #
        filt_hi = filter[0]
        filt_lo = filter[1]
        highcut = 1.0 / filt_hi / 3600
        lowcut = 1.0 / filt_lo / 3600
        fnames = ["Hobo-10m-filter-17h", "RBR-10m-filter-17h"]

        btype = 'band'
        fs1 = 1.0 / ((HOBOdateTimeArr[1] - HOBOdateTimeArr[0]) * factor)
        # HOBODepthArr = filters.fft_bandpassfilter(HOBODepthArr, fs1, lowcut, highcut)
        HOBODepthArr, w, h, N = filters.butterworth(HOBODepthArr, btype, lowcut, highcut, fs1)

        fs2 = 1 / ((RBRdateTimeArr[1] - RBRdateTimeArr[0]) * factor)
        # RBRDepthArr = filters.fft_bandpassfilter(RBRDepthArr, fs2, lowcut, highcut)
        RBRDepthArr, w, h, N = filters.butterworth(RBRDepthArr, btype, lowcut, highcut, fs2)

    # end filter
    custom1 = "Isotherme %d ($^\circ$C) depth (m)" % isotemp
    custom2 = "Isotherme %d ($^\circ$C) depth (m)" % isotemp
    custom = [custom1, custom2]


    t01 = ['0', '3', '6', '9', '12', '15', '18', '21', '24', '27']
    t02 = [27, 24, 21, 18, 15, 12, 9, 6, 3, 0]
    t11 = ['0', '2', '4', '6', '8', '10', '12', '14', '16', '18', '20']
    t12 = [20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0]


    tick1 = [t01, t02]
    tick2 = [t11, t12]
    tick = [tick1, tick2]
    revert = True


    display_data.display_depths_subplot([HOBOdateTimeArr[0][1:], RBRdateTimeArr[0][1:]], [HOBODepthArr[1:], RBRDepthArr[1:]], maxdepth = wdepths, \
                                       fnames = fnames, revert = revert, tick = tick, custom = custom, firstlog = None)


    tick = [tick1]
    revert_y = True  # this will revern only depths tick on the y axis

    display_data.display_depths_subplot([HOBOdateTimeArr[0][1:]], [HOBODepthArr[1:]], maxdepth = [wdepths[0]], \
                                         fnames = [fnames[0]], revert = revert_y, tick = tick, custom = [custom[0]], firstlog = None)


    tick = [tick2]
    revert_y = True


    display_data.display_depths_subplot([RBRdateTimeArr[0][1:]], [RBRDepthArr[1:]], maxdepth = [wdepths[1]], \
                                         fnames = [fnames[1]], revert = revert_y, tick = tick, custom = [custom[1]], firstlog = None)

    return [ [HOBOdateTimeArr[0][1:], HOBODepthArr[1:]], [RBRdateTimeArr[0][1:], RBRDepthArr[1:]] ]

# end isoterm_oscillation

def poincare_wave_in_lontario(period, dateinterval, data, fnames, wdepths, isotemp):

    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

    HOBOdateTimeArr = data[0][0]
    HOBODepthArr = data[0][1]
    RBRdateTimeArr = data[1][0]
    RBRDepthArr = data[1][1]

    # Poincare Waves
    highcut = 1.0 / period / 3600
    lowcut = 1.0 / (period + 0.2) / 3600
    tunits = 'day'

    if tunits == 'day':
        factor = 86400
    elif tunits == 'hour':
        factor = 3600
    else:
        factor = 1

    Filtered_data = numpy.zeros(len(HOBOdateTimeArr) + 1, dtype = numpy.float)
    fs = 1.0 / ((HOBOdateTimeArr[2] - HOBOdateTimeArr[1]) * factor)
    Filtered_data, w, h, N = filters.butterworth(HOBODepthArr, 'band', lowcut, highcut, fs, debug = 'False')

    Filtered_data_rbr = numpy.zeros(len(HOBOdateTimeArr) + 1, dtype = numpy.float)
    fs2 = 1.0 / ((RBRdateTimeArr[2] - RBRdateTimeArr[1]) * factor)
    Filtered_data_rbt, w, h, N = filters.butterworth(RBRDepthArr, 'band', lowcut, highcut, fs2, debug = 'False')

    print "Start display: poincare_wave_in_lontario"

    # superimposed filtered data for he period oscillation freq
    custom1 = "Isotherme %d ($^\circ$C) depth (m)" % isotemp
    custom2 = "Isotherme %d ($^\circ$C) depth (m)" % isotemp
    custom = [custom1, custom2]
    t01 = ['0', '3', '6', '9', '12', '15', '18', '21', '24', '27']
    t02 = [27, 24, 21, 18, 15, 12, 9, 6, 3, 0]
    t11 = ['0', '2', '4', '6', '8', '10', '12', '14', '16', '18', '20']
    t12 = [20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0]
    tick1 = [t01, t02]
    tick2 = [t11, t12]
    tick = [tick1, tick2]
    revert_y = True

    display_data.display_depths_subplot([HOBOdateTimeArr[1:], RBRdateTimeArr[1:]], [Filtered_data[1:], Filtered_data_rbt[1:]], maxdepth = None, \
                                       fnames = [fnames[0]], revert = False, tick = None, custom = custom, firstlog = None)

    debug = False;
    if debug:
        # tick = [tick1]
        revert_y = True  # this will revert only depths tick on the y axis

        display_data.display_depths_subplot([HOBOdateTimeArr[1:], HOBOdateTimeArr[1:]], [HOBODepthArr[1:], Filtered_data[1:]], maxdepth = None, \
                                             fnames = fnames, revert = False, tick = None, custom = [custom1, "FFT"], firstlog = None)

def poincare_wave_in_harbour(period, dateinterval, paths):

    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

    for path in paths:
        dateTime, temp, results, k , fnames = readTempHoboFiles.read_files(window_hour, windows[1], dateinterval, path)
        HOBOdateTimeArr = dateTime
        HOBOresultsArr = results
        HOBOtempArr = temp

        # Poincare Waves
        highcut = 1.0 / period / 3600
        lowcut = 1.0 / (period + 0.2) / 3600
        tunits = 'day'

        if tunits == 'day':
            factor = 86400
        elif tunits == 'hour':
            factor = 3600
        else:
            factor = 1

        Filtered_data = numpy.zeros(len(HOBOdateTimeArr) + 1, dtype = numpy.ndarray)
        i = 0
        btype = 'band'
        for data in HOBOdateTimeArr:
            fs = 1.0 / ((HOBOdateTimeArr[i][2] - HOBOdateTimeArr[i][1]) * factor)
            # Filtered_data[i] = filters.fft_bandpassfilter(HOBOtempArr[i], fs, lowcut, highcut)
            Filtered_data[i], w, h, N = filters.butterworth(HOBOtempArr[i], btype, lowcut, highcut, fs)
            i += 1

        # get hobo file from the lake
        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE-Apr-May_2012-Thermistor_chain/csv_processed'
        hobofilename = '18_2393005.csv'
        print "Reading file %s" % hobofilename
        dateTime, temp, results = readTempHoboFiles.get_data_from_file(hobofilename, window_hour, windows[1], [start_num, end_num], path)

        HOBOdateTimeArr = numpy.resize(HOBOdateTimeArr, len(HOBOdateTimeArr) + 1)
        HOBOresultsArr = numpy.resize(HOBOresultsArr, len(HOBOresultsArr) + 1)
        HOBOtempArr = numpy.resize(HOBOtempArr, len(HOBOtempArr) + 1)

        HOBOdateTimeArr[len(HOBOdateTimeArr) - 1] = dateTime
        HOBOresultsArr[len(HOBOresultsArr) - 1] = results
        HOBOtempArr[len(HOBOtempArr) - 1] = temp


        fnames = numpy.append(fnames, hobofilename)

        fs = 1.0 / ((dateTime[2] - dateTime[1]) * factor)
        # Filtered_data[len(HOBOresultsArr) - 1] = filters.fft_bandpassfilter(temp, fs, lowcut, highcut)
        Filtered_data[len(HOBOresultsArr) - 1], w, h, N = filters.butterworth(temp, btype, lowcut, highcut, fs)


        print "Start display"
        display_data.display_temperatures_subplot(HOBOdateTimeArr, HOBOtempArr, HOBOresultsArr, k, fnames = fnames)

        # superimposed filtered data for the period oscillation freq
        difflines = True
        custom = "%sh filter- Temperature " % str(period)
        display_data.display_temperatures(HOBOdateTimeArr, Filtered_data, HOBOresultsArr, k, fnames = fnames, difflines = difflines, custom = custom)
    # end for path

def calculate_statistics(arr):
    sz = len(arr)
    avg = numpy.average(arr)
    min = numpy.min(arr)
    max = numpy.max(arr)
    return  [avg, max, min]

def write_statistics(writer, station, day, unixtime, avg, max, min):
    idx = 0
    numdat = []
    prev = 0
    prevtxt = ''
    # print "len(depth) :%d, len(dateTime):%d" % (len(depth), len(dateTime))
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    writer.writerow([station, day, unixtime, avg, max, min])


def harbour_statistics(path, path_out, timeinterv):
    '''
    calculate avg, min, max /day/sensor
    '''

    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')


    dateTime, temp, results, k , fnames = readTempHoboFiles.read_files(window_hour, windows[1], timeinterv, path)
    HOBOdateTimeArr = dateTime
    HOBOresultsArr = results
    HOBOtempArr = temp



    for i in range(0, len(HOBOdateTimeArr)):
        dayOfTheYear = 0
        OlddayOfTheYear = 0
        daytemps = []

        station = fnames[i]
        print "Stats for %s" % station
        ofile = open(path_out + '/' + station, "wb")
        writer = csv.writer(ofile, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
        write_statistics(writer, "Station", "Date", "Timestamp", "Avg Temp", "Max Temp", "Min Temp")

        dateTime = HOBOdateTimeArr[i][1:]
        temp = HOBOtempArr[i][1:]

        for j in range(0, len(dateTime)):
            datet = num2date(dateTime[j])
            dayOfTheYear = datet.timetuple().tm_yday
            daytemps.append(temp[j])

            if dayOfTheYear != OlddayOfTheYear and j != 0:
                day = num2date(dateTime[j - 1])
                daystr = day.strftime("%d %B %Y")

                # calculate stats
                [avg, max, min] = calculate_statistics(numpy.array(daytemps))
                # insert in a spreadsheet
                write_statistics(writer, station, daystr, dateTime[j], avg, max, min)

                # clear the array
                OlddayOfTheYear = dayOfTheYear
                daytemps = []
            elif j == 0:
                OlddayOfTheYear = dayOfTheYear

        # END FOR
        ofile.close()
    # end for
# end harbour_statistics

def draw_harbour_statistics(path, timeinterv, selector):

    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

    for i in range(0, len(selector)):

        type = selector[i]

        dateTime, temp, result, k, fnames = readTempHoboFiles.read_stat_files(window_hour, windows[1], timeinterv, path, type)
        HOBOdateTimeArr = dateTime
        HOBOtempArr = temp
        HOBOresultsArr = result
        print "Start display %s" % type

        # display_data.display_temperatures_subplot(HOBOdateTimeArr, HOBOtempArr, HOBOresultsArr, k, fnames = fnames)

        # superimposed filtered data for he period oscillation freq
        difflines = False

        custom = "%s - Temperature " % type
        display_data.display_temperatures(HOBOdateTimeArr, HOBOtempArr, HOBOresultsArr, k, fnames = fnames, difflines = difflines, custom = custom)



if __name__ == '__main__':


    #---------------------------------
    # Set the start and end date-time
    #---------------------------------
    startdate = '12/07/19 00:00:00'
    enddate = '12/10/24 00:00:00'
    dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
    start_num = date2num(dt)
    dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
    end_num = date2num(dt)


    #-----------------------------------------------------------
    # Set the paths and sepcific data for the isotherm locations
    #-----------------------------------------------------------
    paths = ['/home/bogdan/Documents/UofT/PhD/Data_Files/MOE-Apr-May_2012-Thermistor_chain/csv_processed',
             '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE deployment 18-07-2012/Data/RBR']
    waterdepths = [27, 20]  # water depths at the location
    top_log_depths = [3, 4]
    delta_ls = [1, 1]  # loggers interval

    fnames = ['18_2393005.csv', '019513.dat']
    read_LOntario_files(paths, fnames, [start_num, end_num])

    print "Done!"
    os.abort()


     # draw the isotherm oscillations
    temp = 13.0
    # Filter in [Hi freq, lo freq} = > [ lo period, hi period]
    filter = None  # [16.8, 17.2]

    [hobo, rbr] = isoterm_oscillation(temp, paths, waterdepths, top_log_depths, delta_ls, [start_num, end_num], filter)
    period_hours = 17
    startdate = '12/07/19 00:00:00'
    enddate = '12/10/24 00:00:00'
    dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
    start_num = date2num(dt)
    dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
    end_num = date2num(dt)
    fnames = ['Hobo t-Chain', 'RBR t-Chain']
    poincare_wave_in_lontario(period_hours, [start_num, end_num], [hobo, rbr], fnames, waterdepths, temp)
    print "Done!"
    os.abort()

    #---------------------------------------------------
    # Read all files in Toronto Harbour for temperature
    #----------------------------------------------------
    read_Tor_Harbour_files()  # this can filter too and  exhibit poincare waves


    #---------------------------------------------------
    # Correlate with meteorologic data
    #---------------------------------------------------
    wind_airpress_airtemp_water_temp()

    period_hours = 24
    paths = ['/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed/upwelling-LO-21-10-37-38',
            '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed/upwelling-LO-21-17-2',
            ]

    startdate = '12/07/19 00:00:00'
    enddate = '12/10/24 00:00:00'
    dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
    start_num = date2num(dt)
    dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
    end_num = date2num(dt)
    poincare_wave_in_harbour(period_hours, [start_num, end_num], paths)

    #---------------------------------------------------------
    # Simple statititics for the NSERC Files
    #---------------------------------------------------------
    path = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed'
    path_out = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed/stats'
    path = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Apr2012-Tor_Harb/csv_processed'
    path_out = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Apr2012-Tor_Harb/csv_processed/stats'
    # path_out = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Apr2012-Tor_Harb/csv_processed/stats/sample'

    startdate = '11/02/01 00:00:00'
    enddate = '12/10/24 00:00:00'
    dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
    start_num = date2num(dt)
    dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
    end_num = date2num(dt)

    #-----------------------------------------------------------------
    # Calculate statitics
    # harbour_statistics(path, path_out, [start_num, end_num])
    # draw some graphs
    #-------------------------------------------------------------------
    draw_harbour_statistics(path_out, [start_num, end_num], ['max', 'avg', 'min'])
    print "Done!"

