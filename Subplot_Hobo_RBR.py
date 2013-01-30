import csv
import numpy
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import date2num, num2date
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates
import time, os, sys, inspect, locale
from scipy.interpolate import UnivariateSpline
import display_data
import read_RBR
import readTempHoboFiles
import env_can_weather_data_processing as envir

sys.path.insert(0, '/software/SAGEwork/Seiches')
import fft.filters as filters




'''
Logging start 12/07/16 00:00:00
Logging end   12/11/22 07:49:04
'''

# turn off warning in polyfit
import warnings
warnings.simplefilter('ignore', numpy.RankWarning)
import smooth


def read_LOntario_files():
    windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
    window_6hour = 30 * 6
    window_hour = 30
    window_day = 30 * 24
    window_half_day = 30 * 12
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

    # get RBR file
    path = '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE deployment 18-07-2012/Data/RBR'
    RBRfilename = '019513.dat'
    print "Reading file %s" % RBRfilename
    dateTime, temp, results = read_RBR.get_data_from_file(RBRfilename, window_hour, windows[1], [start_num, end_num], path)
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
    highcut = 1.0 / 16 / 3600
    lowcut = 1.0 / 18 / 3600
    legend1 = ["Hobo-10m-filter-17h", "RBR-10m-filter-17h"]

    fs1 = 1.0 / ((HOBOdateTimeArr[1] - HOBOdateTimeArr[0]) * factor)
    data1 = filters.fft_bandpassfilter(HOBOtempArr, fs1, lowcut, highcut)

    fs2 = 1 / ((RBRdateTimeArr[1] - RBRdateTimeArr[0]) * factor)
    data2 = filters.fft_bandpassfilter(RBRtempArr, fs2, lowcut, highcut)

    # display_data.display_temperatures_subplot([HOBOdateTimeArr, RBRdateTimeArr], [data1, data2], [HOBOresultsArr, RBRresultsArr], k, fnames = legend1)
    # display_data.display_temperatures([HOBOdateTimeArr, RBRdateTimeArr], [data1, data2], [HOBOresultsArr, RBRresultsArr], k, fnames = legend1)


    # Kelvin?
    lowcut = 1.0 / (24 * 10) / 3600
    highcut = 1.0 / (24 * 3) / 3600
    legend2 = ["Hobo-10m-filter-3-10 days", "RBR-10m-filter-3-10 days"]
    fs3 = 1.0 / ((HOBOdateTimeArr[1] - HOBOdateTimeArr[0]) * factor)
    data3 = filters.fft_bandpassfilter(HOBOtempArr, fs3, lowcut, highcut)

    fs4 = 1 / ((RBRdateTimeArr[1] - RBRdateTimeArr[0]) * factor)
    data4 = filters.fft_bandpassfilter(RBRtempArr, fs4, lowcut, highcut)

    # display_data.display_temperatures_subplot([HOBOdateTimeArr, RBRdateTimeArr], [data3, data4], [HOBOresultsArr, RBRresultsArr], k, fnames = legend2)
    # display_data.display_temperatures([HOBOdateTimeArr, RBRdateTimeArr], [data3, data4], [HOBOresultsArr, RBRresultsArr], k, fnames = legend2)



    Data = [data1, data2, data3, data4]
    Result = [HOBOresultsArr, RBRresultsArr, HOBOresultsArr, RBRresultsArr]
    legend = [legend1[0], legend1[1], legend2[0], legend2[1]]
    timeint = [HOBOdateTimeArr, RBRdateTimeArr, HOBOdateTimeArr, RBRdateTimeArr]

    display_data.display_temperatures_subplot(timeint, Data, Result, k, fnames = legend)
    display_data.display_temperatures(timeint, Data, Result, k, fnames = legend)


def read_Tor_Harbour_files():
    windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
    window_6hour = 30 * 6
    window_hour = 30
    window_day = 30 * 24
    window_half_day = 30 * 12
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
        for data in HOBOdateTimeArr:
            fs = 1.0 / ((HOBOdateTimeArr[i][2] - HOBOdateTimeArr[i][1]) * factor)
            Filtered_data[i] = filters.fft_bandpassfilter(HOBOtempArr[i], fs, lowcut, highcut)
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
        Filtered_data[len(HOBOresultsArr) - 1] = filters.fft_bandpassfilter(temp, fs, lowcut, highcut)


        print "Start display"
        display_data.display_temperatures_subplot(HOBOdateTimeArr, HOBOtempArr, HOBOresultsArr, k, fnames = fnames)

        # superimposed filtered data for 1-3 days oscillation freq
        difflines = True
        display_data.display_temperatures(HOBOdateTimeArr, Filtered_data, HOBOresultsArr, k, fnames = fnames, difflines = difflines)
    # end for path


def wind_airpress_airtemp_water_temp():



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

    weather_path = '/home/bogdan/Documents/UofT/PhD/Research-docs/Data_Files/Hobo_Files_Bogdan'
    wfile = open(weather_path + '/eng-hourly-07012012-11302012.csv', 'rb')

    wreader = csv.reader(wfile, delimiter = ',', quotechar = '"')
    [temp, dateTime, windDir, windSpd, press] = read_stringdatefile(wreader)
    # 2) select the dates
    [wtemp, wdateTime, windDir, windSpd, press] = select_dates_string(start_num, end_num, dateTime, temp, windDir, windSpd, press)
    display("temperature", ' temperature ($^\circ$C)', [wdateTime], [wtemp], ['r'])
    display("wind direction & speed", ' wind dir deg*10/wind speed Km/h', [wdateTime, wdateTime], [windDir, windSpd], ['r', 'b'])
    # display("wind speed", ' wind speed km/h', [wdateTime], [windSpd], ['r'])
    plt = display("pressure", ' air pressure  kPa', [wdateTime], [press], ['r'])
    # call show() so that the window does not disappear.
    plt.show()
    # 3) interplate every 10 minutes
    # dirList = os.listdir(path_in)
    [iwtemp, iwdateTime, iwindDir, iwindSpd, iPress] = interpolateData(10, wtemp, wdateTime, windDir, windSpd, press)

import csv
import numpy
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import date2num, num2date
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates
import time, os, sys, inspect, locale
from scipy.interpolate import UnivariateSpline
import display_data
import read_RBR
import readTempHoboFiles


sys.path.insert(0, '/software/SAGEwork/Seiches')
import fft.filters as filters




'''
Logging start 12/07/16 00:00:00
Logging end   12/11/22 07:49:04
'''

# turn off warning in polyfit
import warnings
warnings.simplefilter('ignore', numpy.RankWarning)
import smooth


def read_LOntario_files():
    windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
    window_6hour = 30 * 6
    window_hour = 30
    window_day = 30 * 24
    window_half_day = 30 * 12
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

    # get RBR file
    path = '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE deployment 18-07-2012/Data/RBR'
    RBRfilename = '019513.dat'
    print "Reading file %s" % RBRfilename
    dateTime, temp, results = read_RBR.get_data_from_file(RBRfilename, window_hour, windows[1], [start_num, end_num], path)
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
    highcut = 1.0 / 17.8 / 3600
    lowcut = 1.0 / 18.2 / 3600
    legend1 = ["Hobo-10m-filter-17h", "RBR-10m-filter-17h"]

    fs1 = 1.0 / ((HOBOdateTimeArr[1] - HOBOdateTimeArr[0]) * factor)
    data1 = filters.fft_bandpassfilter(HOBOtempArr, fs1, lowcut, highcut)

    fs2 = 1 / ((RBRdateTimeArr[1] - RBRdateTimeArr[0]) * factor)
    data2 = filters.fft_bandpassfilter(RBRtempArr, fs2, lowcut, highcut)

    # display_data.display_temperatures_subplot([HOBOdateTimeArr, RBRdateTimeArr], [data1, data2], [HOBOresultsArr, RBRresultsArr], k, fnames = legend1)
    # display_data.display_temperatures([HOBOdateTimeArr, RBRdateTimeArr], [data1, data2], [HOBOresultsArr, RBRresultsArr], k, fnames = legend1)


    # Kelvin?
    # lowcut = 1.0 / (24 * 10) / 3600
    # highcut = 1.0 / (24 * 3) / 3600
    # legend2 = ["Hobo-10m-filter-3-10 days", "RBR-10m-filter-3-10 days"]

    lowcut = 1.0 / 600 / 3600
    highcut = 1.0 / 300 / 3600
    legend2 = ["Hobo-10m-filter-300 - 600 h", "RBR-10m-filter-300 - 600 h"]
    fs3 = 1.0 / ((HOBOdateTimeArr[1] - HOBOdateTimeArr[0]) * factor)
    data3 = filters.fft_bandpassfilter(HOBOtempArr, fs3, lowcut, highcut)

    fs4 = 1 / ((RBRdateTimeArr[1] - RBRdateTimeArr[0]) * factor)
    data4 = filters.fft_bandpassfilter(RBRtempArr, fs4, lowcut, highcut)

    # display_data.display_temperatures_subplot([HOBOdateTimeArr, RBRdateTimeArr], [data3, data4], [HOBOresultsArr, RBRresultsArr], k, fnames = legend2)
    # display_data.display_temperatures([HOBOdateTimeArr, RBRdateTimeArr], [data3, data4], [HOBOresultsArr, RBRresultsArr], k, fnames = legend2)



    Data = [data1, data2, data3, data4]
    Result = [HOBOresultsArr, RBRresultsArr, HOBOresultsArr, RBRresultsArr]
    legend = [legend1[0], legend1[1], legend2[0], legend2[1]]
    timeint = [HOBOdateTimeArr, RBRdateTimeArr, HOBOdateTimeArr, RBRdateTimeArr]

    display_data.display_temperatures_subplot(timeint, Data, Result, k, fnames = legend)
    display_data.display_temperatures(timeint, Data, Result, k, fnames = legend)


def read_Tor_Harbour_files():
    windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
    window_6hour = 30 * 6
    window_hour = 30
    window_day = 30 * 24
    window_half_day = 30 * 12
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
        for data in HOBOdateTimeArr:
            fs = 1.0 / ((HOBOdateTimeArr[i][2] - HOBOdateTimeArr[i][1]) * factor)
            Filtered_data[i] = filters.fft_bandpassfilter(HOBOtempArr[i], fs, lowcut, highcut)
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
        Filtered_data[len(HOBOresultsArr) - 1] = filters.fft_bandpassfilter(temp, fs, lowcut, highcut)


        print "Start display"
        display_data.display_temperatures_subplot(HOBOdateTimeArr, HOBOtempArr, HOBOresultsArr, k, fnames = fnames)

        # superimposed filtered data for 1-3 days oscillation freq
        difflines = True
        display_data.display_temperatures(HOBOdateTimeArr, Filtered_data, HOBOresultsArr, k, fnames = fnames, difflines = difflines)
    # end for path


def wind_airpress_airtemp_water_temp():


    windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
    window_6hour = 30 * 6
    window_hour = 30
    window_day = 30 * 24
    window_half_day = 30 * 12
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
    for data in dataArray:
        fs = 1.0 / ((timeArray[i][2] - timeArray[i][1]) * factor)
        Filtered_data[i] = filters.fft_bandpassfilter(data, fs, lowcut, highcut)
        i += 1


    custom = numpy.array(['Air temp.($^\circ$C)', 'Wind dir.', 'Wind speed (m/s)', 'Air pres. (hPa)', 'Water temp.($^\circ$C)'])
    print "Start display"
    display_data.display_temperatures_subplot(timeArray, dataArray, dataArray, k, fnames = fnames, custom = custom)

    # superimposed filtered data for 1-3 days oscillation freq
    difflines = True
    display_data.display_temperatures(timeArray, Filtered_data, Filtered_data, k, fnames = fnames, difflines = difflines, custom = custom)



if __name__ == '__main__':
    read_LOntario_files()
    # read_Tor_Harbour_files()
    # wind_airpress_airtemp_water_temp()
    print "Done!"

