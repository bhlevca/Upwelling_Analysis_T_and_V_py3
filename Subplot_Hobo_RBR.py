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


import spectral_analysis
import tor_harb_windrose
import upwelling
import fish_detection

import utils.hdf_tools as hdf

sys.path.insert(0, '/software/SAGEwork/Seiches')
import fft.filters as filters
import fft.fft_utils as fft_utils


windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
window_6hour = "window_6hour"  # 30 * 6 for a 2 minute sampling
window_hour = "window_hour"  # 30
window_day = "window_day"  # 30 * 24
window_half_day = "window_half_day"  # 30 * 12
window_3days = "window_3days"  # 3 * 30 * 24
window_7days = "window_7days"  # 7 * 30 * 24

'''
Logging start 12/07/16 00:00:00
Logging end   12/11/22 07:49:04
'''

# turn off warning in polyfit
import warnings
warnings.simplefilter('ignore', numpy.RankWarning)
from utils import smooth


def read_LOntario_files(paths, fnames, dateinterval, chain = "all" , zNames = None, bfilter = False, bkelvin = False):

    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    print "Start read_LOntario_files()"

    if chain == "all" or chain == "hobo":
        # get hobo file
        hobofilename = fnames[0]  # '18_2393005.csv'
        print "Reading file %s" % hobofilename
        dateTime, temp, results = readTempHoboFiles.get_data_from_file(hobofilename, window_hour, windows[1], dateinterval, paths[0])
        HOBOdateTimeArr = dateTime
        HOBOresultsArr = results
        HOBOtempArr = temp

    if chain == "all" or chain == "rbr":
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
    if zNames == None:
        zNames = ["Hobo ", "RBR "]
    if chain == "all":
        utils.display_data.display_temperatures_subplot([HOBOdateTimeArr, RBRdateTimeArr], [HOBOtempArr, RBRtempArr], [HOBOresultsArr, RBRresultsArr], k, fnames = ["Hobo-10m", "RBR-10m"])
        utils.display_data.display_temperatures([HOBOdateTimeArr, RBRdateTimeArr], [HOBOtempArr, RBRtempArr], k, fnames = zNames)
    elif chain == "hobo":
        utils.display_data.display_temperatures([HOBOdateTimeArr], [HOBOtempArr], k, fnames = zNames[0])
    elif chain == "rbr":
        utils.display_data.display_temperatures([RBRdateTimeArr], [RBRtempArr], k, fnames = zNames[1])

    if bkelvin and chain == 'all':
        [hobo, rbr] = [ [HOBOdateTimeArr[1:], HOBOtempArr[1:]], [RBRdateTimeArr[1:], RBRtempArr[1:]] ]
        kelvin_wave_in_lontario([hobo, rbr], zNames)
    # end bkelvin

    if bfilter:
        tunits = 'day'

        if tunits == 'day':
            factor = 86400
        elif tunits == 'hour':
            factor = 3600
        else:
            factor = 1



        # Poincare 17h filter
        fnumber = 27
        delta = 0.5
        highcut = 1.0 / (fnumber - delta) / 3600
        lowcut = 1.0 / (fnumber + delta) / 3600

        # Diurnal  24h filter
        # highcut = 1.0 / 23.8 / 3600
        # lowcut = 1.0 / 24.2 / 3600

        # Kelvin
        # highcut = 1.0 / 24 * 10 / 3600
        # lowcut = 1.0 / 24 *15 / 3600

        btype = 'band'


        yday = True
        debug = False
        order = None
        gpass = 9
        astop = 32
        recurse = True

        if chain == "hobo"  or chain == "all":
            fs1 = 1.0 / ((HOBOdateTimeArr[1] - HOBOdateTimeArr[0]) * factor)
            # data1 = filters.fft_bandpassfilter(HOBOtempArr, fs1, lowcut, highcut)
            data1, w, h, N, delay1 = filters.butterworth(HOBOtempArr, btype, lowcut, highcut, fs1, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = True, debug = debug)
            if len(data1) != len(HOBOdateTimeArr):
                HOBOdateTimeArr_res1 = scipy.signal.resample(HOBOdateTimeArr, len(data1))
            else :
                HOBOdateTimeArr_res1 = HOBOdateTimeArr


        # data1, w, h, N, delay1 = filters.firwin(HOBOtempArr, btype, lowcut, highcut, fs1, output = 'ba')

        if chain == "rbr" or chain == "all":
            fs2 = 1.0 / ((RBRdateTimeArr[1] - RBRdateTimeArr[0]) * factor)
            # data2 = filters.fft_bandpassfilter(RBRtempArr, fs2, lowcut, highcut)
            data2, w, h, N, delay2 = filters.butterworth(RBRtempArr, btype, lowcut, highcut, fs2, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = True, debug = debug)
            if len(data2) != len(RBRdateTimeArr):
                RBRdateTimeArr_res2 = scipy.signal.resample(RBRdateTimeArr, len(data2))
            else :
                RBRdateTimeArr_res2 = RBRdateTimeArr

        strg1 = " %s - filter: %d h" % (zNames[0], int(fnumber))
        strg2 = " %s -filter- %d h" % (zNames[1], int(fnumber))


        if chain == "all":
            legend1 = [strg1, strg2]
            # legend1 = ["Hobo-10m-filter-24h", "RBR-10m-filter-24h"]
            utils.display_data.display_temperatures_subplot([HOBOdateTimeArr_res1, RBRdateTimeArr_res2], [data1, data2], [HOBOresultsArr, RBRresultsArr], k, fnames = legend1, yday = yday, delay = [delay1, delay2])
            utils.display_data.display_temperatures([numpy.subtract(HOBOdateTimeArr_res1, delay1), numpy.subtract(RBRdateTimeArr_res2, delay2)], [data1, data2], k, fnames = legend1)
        elif chain == "hobo":
            legend1 = [strg1]
            # legend1 = ["Hobo-10m-filter-24h"]

            utils.display_data.display_temperatures([numpy.subtract(HOBOdateTimeArr_res1, delay1)], [data1], k, fnames = legend1)
        elif chain == "rbr":
            legend1 = [strg2]
            # legend1 = ["RBR-10m-filter-24h"]
            utils.display_data.display_temperatures([numpy.subtract(RBRdateTimeArr_res2, delay2)], [data2], k, fnames = legend1)




        # Kelvin?
        f2number = 12.5
        delta = 2.5
        highcut = 1.0 / (24 * (f2number - delta)) / 3600
        lowcut = 1.0 / (24 * (f2number + delta)) / 3600

        if chain == "hobo"  or chain == "all":
            fs3 = 1.0 / ((HOBOdateTimeArr[1] - HOBOdateTimeArr[0]) * factor)
            # data3 = filters.fft_bandpassfilter(HOBOtempArr, fs3, lowcut, highcut)
            data3, w, h, N, delay3 = filters.butterworth(HOBOtempArr, btype, lowcut, highcut, fs3, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = True, debug = debug)
            if len(data3) != len(HOBOdateTimeArr):
                HOBOdateTimeArr_res3 = scipy.signal.resample(HOBOdateTimeArr, len(data3))
            else :
                HOBOdateTimeArr_res3 = HOBOdateTimeArr

        if chain == "rbr"  or chain == "all":
            fs4 = 1 / ((RBRdateTimeArr[1] - RBRdateTimeArr[0]) * factor)
            # data4 = filters.fft_bandpassfilter(RBRtempArr, fs4, lowcut, highcut)
            data4, w, h, N, delay4 = filters.butterworth(RBRtempArr, btype, lowcut, highcut, fs4, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = True, debug = debug)
            if len(data4) != len(RBRdateTimeArr):
                RBRdateTimeArr_res4 = scipy.signal.resample(RBRdateTimeArr, len(data4))
            else :
                RBRdateTimeArr_res4 = RBRdateTimeArr


        strg1 = "%s - filter: %d-%d  days" % (zNames[0], int(f2number - delta), int(f2number + delta))
        strg2 = "%s - filter- %d-%d days" % (zNames[1], int(f2number - delta), int(f2number + delta))

        if chain == "all":
            legend2 = [strg1, strg2]

            utils.display_data.display_temperatures_subplot([HOBOdateTimeArr_res3, RBRdateTimeArr_res4], [data3, data4], [HOBOresultsArr, RBRresultsArr], k, fnames = legend2, yday = yday, delay = [delay3, delay4])
            utils.display_data.display_temperatures([numpy.subtract(HOBOdateTimeArr_res3, delay3), numpy.subtract(RBRdateTimeArr_res4, delay4)], [data3, data4], k, fnames = legend2)
        elif chain == "hobo":
            legend2 = [strg1]
            utils.display_data.display_temperatures([numpy.subtract(HOBOdateTimeArr_res3, delay3)], [data3], k, fnames = legend2, custom = "Filtered Temperature Oscillation")

        elif chain == "rbr":
            legend2 = [strg2]
            utils.display_data.display_temperatures([numpy.subtract(RBRdateTimeArr_res4, delay4)], [data4], k, fnames = legend2, custom = "Filtered Temperature Oscillation")




        if chain == "all":
            Data = [data1, data2, data3, data4]
            Result = [HOBOresultsArr, RBRresultsArr, HOBOresultsArr, RBRresultsArr]
            legend = [legend1[0], legend1[1], legend2[0], legend2[1]]
            timeint = [numpy.subtract(HOBOdateTimeArr_res1, delay1), numpy.subtract(RBRdateTimeArr_res2, delay2), numpy.subtract(HOBOdateTimeArr_res3, delay3), numpy.subtract(RBRdateTimeArr_res4, delay4)]

            utils.display_data.display_temperatures_subplot(timeint, Data, Result, k, fnames = legend, yday = yday, delay = [delay1, delay2, delay3, delay4], custom = "Filtered Temperature Oscillation")
            utils.display_data.display_temperatures(timeint, Data, k, fnames = legend, custom = "Filtered Temperature Oscillation")
        elif chain == "hobo":
            legend = [legend1[0], legend2[0]]
            trim = int(len(HOBOdateTimeArr_res1) / 10)
            trim2 = int(len(HOBOdateTimeArr_res3) / 10)
            Data = [data1[trim:-trim], data3[trim2:-trim2]]
            Result = [HOBOresultsArr[trim:-trim], HOBOresultsArr[trim:-trim]]

            timeint = [numpy.subtract(HOBOdateTimeArr_res1, delay1)[trim:-trim], numpy.subtract(HOBOdateTimeArr_res3, delay3)[trim2:-trim2]]

            # display_data.display_temperatures_subplot(timeint, Data, Result, k, fnames = legend, yday = yday, delay = [delay1, delay3], custom = "Filtered Temperature Oscillation")
            utils.display_data.display_temperatures(timeint, Data, k, fnames = legend, custom = "Filtered Temperature Oscillation", ylim = [-4, 8])
        elif chain == "rbr":
            Data = [data2, data4]
            Result = [RBRresultsArr, RBRresultsArr]
            legend = [legend1[1], legend2[1]]
            timeint = [numpy.subtract(RBRdateTimeArr_res2, delay2), numpy.subtract(RBRdateTimeArr_res4, delay4)]

            utils.display_data.display_temperatures_subplot(timeint, Data, Result, k, fnames = legend, yday = yday, delay = [delay2, delay4])
            utils.display_data.display_temperatures(timeint, Data, k, fnames = legend, custom = "Filtered Temperature Oscillation")

    # end bfilter

def read_Tor_Harbour_files(paths, lo_path, lo_file, moving_avg, filemap, period, filter = None):
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

    print "Start read_Tor_Harbour_files()"

    startdate = period[0]
    senddate = period[1]


    dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
    start_num = date2num(dt)
    dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
    end_num = date2num(dt)


    # get hobo file
    for path in paths:
        dateTime, temp, results, k , fnames = readTempHoboFiles.read_files(moving_avg, windows[1], [start_num, end_num], path)
        HOBOdateTimeArr = dateTime
        HOBOresultsArr = results
        HOBOtempArr = temp

        locnames = []
        for name in fnames:
            locnames.append(filemap[name][0] + "_" + str(filemap[name][1]))

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

        if filter != None:
            lowcut = filter[0]
            highcut = filter[1]
            Filtered_data = numpy.zeros(len(HOBOdateTimeArr) + 1, dtype = numpy.ndarray)
            HOBOdateTimeArr_res = numpy.zeros(len(HOBOdateTimeArr) + 1, dtype = numpy.ndarray)
            delay = numpy.zeros(len(HOBOdateTimeArr) + 1, dtype = numpy.ndarray)
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

        # get L. Ontario hobo file
        # hobofilename = '18_2393005.csv'
        print "Reading file %s" % lo_file
        dateTime2, temp2, results2 = readTempHoboFiles.get_data_from_file(lo_file, moving_avg, windows[1], [start_num, end_num], lo_path)

        HOBOdateTimeArr = numpy.resize(HOBOdateTimeArr, len(HOBOdateTimeArr) + 1)
        HOBOresultsArr = numpy.resize(HOBOresultsArr, len(HOBOresultsArr) + 1)
        HOBOtempArr = numpy.resize(HOBOtempArr, len(HOBOtempArr) + 1)

        HOBOdateTimeArr[len(HOBOdateTimeArr) - 1] = dateTime2
        HOBOresultsArr[len(HOBOresultsArr) - 1] = results2
        HOBOtempArr[len(HOBOtempArr) - 1] = temp2


        locnames = numpy.append(locnames, 'Lake Ontario')



        if filter != None:
            btype = 'band'
            fs = 1.0 / ((dateTime2[2] - dateTime2[1]) * factor)
            # Filtered_data[len(HOBOresultsArr) - 1] = filters.fft_bandpassfilter(temp, fs, lowcut, highcut)
            Filtered_data[len(HOBOresultsArr) - 1], w, h, N, delay[len(HOBOresultsArr) - 1] = filters.butterworth(temp, btype, lowcut, highcut, fs, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = True, debug = debug)
            if len(Filtered_data[len(HOBOresultsArr) - 1]) != len(HOBOdateTimeArr[len(HOBOdateTimeArr) - 1]):
                HOBOdateTimeArr_res[len(HOBOresultsArr) - 1] = scipy.signal.resample(HOBOdateTimeArr[len(HOBOresultsArr) - 1], len(Filtered_data[len(HOBOresultsArr) - 1]))
            else :
                HOBOdateTimeArr_res[len(HOBOresultsArr) - 1] = HOBOdateTimeArr[len(HOBOresultsArr) - 1]

        print "Start display"
        # display_data.display_temperatures_subplot(HOBOdateTimeArr, HOBOtempArr, HOBOresultsArr, k, fnames = locnames, yday = yday, delay = delay)
        utils.display_data.display_temperatures(HOBOdateTimeArr, HOBOresultsArr, k, fnames = locnames, difflines = True, custom = "Temperature Timseries - Toronto Harbour")
        # superimposed filtered data for 1-3 days oscillation freq
        difflines = True
        # cut the 1/10 atc each end with bad filtered data

        if filter != None:
            for i in range (len(Filtered_data)) :
                trim = int (len(Filtered_data[i]) / 10)
                Filtered_data[i] = Filtered_data[i][trim:-trim];
                HOBOdateTimeArr_res[i] = HOBOdateTimeArr_res[i][trim:-trim]

            utils.display_data.display_temperatures(HOBOdateTimeArr_res, Filtered_data, k, fnames = locnames, difflines = difflines, custom = "Filtered Temperature Timeseries - Toronto Harbour")
    # end for path

def read_TRCA_files(paths):
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

    print "Start read_TRCA_files()"
    # startdate = '12/05/29 00:00:00'
    # enddate = '12/10/04 00:00:00'
    startdate = '13/05/29 00:00:00'
    enddate = '13/10/04 00:00:00'


    dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
    start_num = date2num(dt)
    dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
    end_num = date2num(dt)


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

        yday = True
        debug = False
        order = None
        gpass = 9
        astop = 32
        recurse = True

        Filtered_data = numpy.zeros(len(HOBOdateTimeArr) + 1, dtype = numpy.ndarray)
        HOBOdateTimeArr_res = numpy.zeros(len(HOBOdateTimeArr) + 1, dtype = numpy.ndarray)
        delay = numpy.zeros(len(HOBOdateTimeArr) + 1, dtype = numpy.ndarray)
        i = 0
        btype = 'band'
        for data in HOBOdateTimeArr:
            fs = 1.0 / ((HOBOdateTimeArr[i][2] - HOBOdateTimeArr[i][1]) * factor)
            Filtered_data[i], w, h, N, delay[i] = filters.butterworth(HOBOtempArr[i], btype, lowcut, highcut, fs, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = True, debug = debug)
            if len(Filtered_data[i]) != len(HOBOdateTimeArr[i]):
                HOBOdateTimeArr_res[i] = sp.signal.resample(HOBOdateTimeArr[i], len(Filtered_data[i]))
            else :
                HOBOdateTimeArr_res[i] = HOBOdateTimeArr[i]

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
        Filtered_data[len(HOBOresultsArr) - 1], w, h, N, delay[len(HOBOresultsArr) - 1] = filters.butterworth(temp, btype, lowcut, highcut, fs, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = True, debug = debug)
        if len(Filtered_data[len(HOBOresultsArr) - 1]) != len(HOBOdateTimeArr[len(HOBOdateTimeArr) - 1]):
            HOBOdateTimeArr_res[len(HOBOresultsArr) - 1] = sp.signal.resample(HOBOdateTimeArr[len(HOBOresultsArr) - 1], len(Filtered_data[len(HOBOresultsArr) - 1]))
        else :
            HOBOdateTimeArr_res[len(HOBOresultsArr) - 1] = HOBOdateTimeArr[len(HOBOresultsArr) - 1]

        print "Start display"
        if len(HOBOdateTimeArr) <= 9:
            utils.display_data.display_temperatures_subplot(HOBOdateTimeArr, HOBOtempArr, HOBOresultsArr, k, fnames = fnames, yday = yday, delay = delay)
        # superimposed filtered data for 1-3 days oscillation freq
        difflines = False
        utils.display_data.display_temperatures(HOBOdateTimeArr_res, Filtered_data, k, fnames = fnames, difflines = difflines)
    # end for path


def wind_airpress_airtemp_water_temp():
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

    print "Start wind_airpress_airtemp_water_temp()"
    startdate = '12/07/19 00:00:00'
    enddate = '12/10/24 00:00:00'
    dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
    start_num = date2num(dt)
    dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
    end_num = date2num(dt)


    # get hobo file
    path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2012/MOE-Apr-May_2012-Thermistor_chain/csv_processed'
    hobofilename = '18_2393005.csv'
    print "Reading file %s" % hobofilename
    dateTime, temp, results = readTempHoboFiles.get_data_from_file(hobofilename, window_hour, windows[1], [start_num, end_num], path)
    HOBOdateTimeArr = dateTime
    HOBOresultsArr = results
    HOBOtempArr = temp

    weather_path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2012/MOE deployment 18-07-2012/Data/ClimateData/all'
    wfile = open(weather_path + '/eng-hourly-07012012-11302012-all.csv', 'rb')

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
    names = numpy.array(["Air Temp", "Wind Dir", "Wind spd", "Atm press", "Water temp"])
    labels = numpy.array(["Air Temp ($^\circ$C)", "Wind Dir ($^\circ$)", "Wind spd (m/s)", "Atm press (hPa)", "Water Temp ($^\circ$C)"])
    Time = numpy.zeros(len(dataArray), dtype = numpy.ndarray)
    y = numpy.zeros(len(dataArray), dtype = numpy.ndarray)
    x05 = numpy.zeros(len(dataArray), dtype = numpy.ndarray)
    x95 = numpy.zeros(len(dataArray), dtype = numpy.ndarray)

    # Frequency domain analysis
    # Todo: Add cospectogram for:air press, wind spd, wind dir, air temp, LW radiation and SW radiation
    i = 0
    numseg = 1
    draw = False
    # funits = "Hz"
    funits = "cph"
    # tunits = "sec"
    tunits = "day"
    title = "Lake Ontario Scarborough Bluffs"
    for data in dataArray:
        dat = [timeArray[i], data]

        [Time[i], y[i], x05[i], x95[i]] = spectral_analysis.doSpectralAnalysis(dat, names[i], labels[i], title, draw, window = "hanning", num_segments = numseg, tunits = tunits, funits = funits, b_wavelets = False)
        i += 1

    water_temp = dataArray[len(dataArray) - 1]
    # do cospectral of water temp with each of the weather data
    for i in range(0, len(dataArray) - 2):
        spectral_analysis.doCospectralAnalysis(y[i], water_temp)


    # Time domanin analysis
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

    # rcParams['text.usetex'] = True
    custom = numpy.array(['Air T($^\circ$C)', 'Wind dir', 'Wind spd(m/s)', 'Air p(hPa)', 'Water T($^\circ$C)'])
    # ToDO: Add short and long radiation
    print "Start display wind_airpress_airtemp_water_temp subplots "
    utils.display_data.display_temperatures_subplot(timeArray, dataArray, dataArray, k, fnames = fnames, custom = custom)

    # superimposed filtered data for 1-3 days oscillation freq
    difflines = True
    print "Start display wind_airpress_airtemp_water_temp plot "
    utils.display_data.display_temperatures(timeArray, Filtered_data, k, fnames = fnames, difflines = difflines, custom = "Weather variables and water temperature")


    print "Start display  Atmospheric radiation "
    path = "/home/bogdan/Documents/UofT/PhD/Data_Files/CloudData/Toronto-Jan-Dec-2012/HDF"
    startdate = '12/07/19 00:00:00'
    enddate = '12/10/24 00:00:00'
    var1 = 'swgnt'
    var2 = 'lwgnt'
    var3 = 'cldtot'
    ix = 0
    iy = 1
    timeidx = [0, 23]
    dateTime1, results1 = hdf.read_hdf_dir(path, var1, ix, iy, timeidx, startdate, enddate)
    dateTime2, results2 = hdf.read_hdf_dir(path, var2, ix, iy, timeidx, startdate, enddate)
    dateTime3, results3 = hdf.read_hdf_dir(path, var3, ix, iy, timeidx, startdate, enddate)


    utils.display_data.display_temperatures([dateTime1, dateTime2, dateTime3], [results1, results2, results3 * 100], [1, 2, 3],
                                      fnames = [var1, var2, var3], difflines = False, custom = "Radiation data (W/m$^2$)")



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
    print "Start isoterm_oscillation()"

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
    print "Start : isoterm_oscillation"
    fname1 = "Hobo-%d ($^\circ$C)" % isotemp
    fname2 = "RBR-%d ($^\circ$C)" % isotemp
    fnames = [fname1, fname2]

    if filter != None:
        print "Start filtering: isoterm_oscillation"

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


        debug = False
        order = None
        gpass = 9
        astop = 32
        recurse = True


        btype = 'band'
        fs1 = 1.0 / ((HOBOdateTimeArr[0][2] - HOBOdateTimeArr[0][1]) * factor)
        # HOBODepthArr = filters.fft_bandpassfilter(HOBODepthArr, fs1, lowcut, highcut)
        HOBODepthArr, w, h, N, delay = filters.butterworth(HOBODepthArr, btype, lowcut, highcut, fs1, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = recurse, debug = debug)

        if len(HOBODepthArr) != len(HOBOdateTimeArr[0]):
            HOBOdateTimeArr_res = scipy.signal.resample(HOBOdateTimeArr[0], len(HOBODepthArr))
        else :
            HOBOdateTimeArr_res = HOBOdateTimeArr[0]


        fs2 = 1 / ((RBRdateTimeArr[0][2] - RBRdateTimeArr[0][1]) * factor)
        # RBRDepthArr = filters.fft_bandpassfilter(RBRDepthArr, fs2, lowcut, highcut)
        RBRDepthArr, w, h, N, delay = filters.butterworth(RBRDepthArr, btype, lowcut, highcut, fs2, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = recurse, debug = debug)

        if len(RBRDepthArr) != len(RBRdateTimeArr[0]):
            RBRdateTimeArr_res = scipy.signal.resample(RBRdateTimeArr[0], len(HOBODepthArr))
        else :
            RBRdateTimeArr_res = RBRdateTimeArr[0]


        print "End filtering: isoterm_oscillation"
     # end filter

    else:
        HOBOdateTimeArr_res = HOBOdateTimeArr[0]
        RBRdateTimeArr_res = RBRdateTimeArr[0]





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
    yday = True

    print "Start display: isoterm_oscillation"

    utils.display_data.display_depths_subplot([HOBOdateTimeArr_res[1:], RBRdateTimeArr_res[1:]], [HOBODepthArr[1:], RBRDepthArr[1:]], maxdepth = wdepths, \
                                       fnames = fnames, yday = yday, revert = revert, tick = tick, custom = custom, firstlog = None)


    tick = [tick1]
    revert_y = True  # this will revert only depths tick on the y axis

    utils.display_data.display_depths_subplot([HOBOdateTimeArr_res[1:]], [HOBODepthArr[1:]], maxdepth = [wdepths[0]], \
                                         fnames = [fnames[0]], yday = yday, revert = revert_y, tick = tick, custom = [custom[0]], firstlog = None)


    tick = [tick2]
    revert_y = True


    utils.display_data.display_depths_subplot([RBRdateTimeArr_res[1:]], [RBRDepthArr[1:]], maxdepth = [wdepths[1]], \
                                         fnames = [fnames[1]], yday = yday, revert = revert_y, tick = tick, custom = [custom[1]], firstlog = None)

    return [ [HOBOdateTimeArr[0][1:], HOBODepthArr[1:]], [RBRdateTimeArr[0][1:], RBRDepthArr[1:]] ]

# end isoterm_oscillation

def poincare_wave_in_lontario(period, dateinterval, data, fnames, wdepths, isotemp):

    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    print "Start poincare_wave_in_lontario()"
    HOBOdateTimeArr = data[0][0]
    HOBODepthArr = data[0][1]
    RBRdateTimeArr = data[1][0]
    RBRDepthArr = data[1][1]

    # Poincare Waves
    highcut = 1.0 / (period - 0.5) / 3600
    lowcut = 1.0 / (period + 0.5) / 3600
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


    btype = 'band'
    fs1 = 1.0 / ((HOBOdateTimeArr[2] - HOBOdateTimeArr[1]) * factor)
    Filtered_data = numpy.zeros(len(HOBOdateTimeArr) + 1, dtype = numpy.float)
    Filtered_data, w, h, N, delay = filters.butterworth(HOBODepthArr, btype, lowcut, highcut, fs1, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = recurse, debug = debug)
    if len(Filtered_data) != len(HOBOdateTimeArr):
        HOBOdateTimeArr_res = scipy.signal.resample(HOBOdateTimeArr, len(Filtered_data))
    else :
        HOBOdateTimeArr_res = HOBOdateTimeArr


    fs2 = 1.0 / ((RBRdateTimeArr[2] - RBRdateTimeArr[1]) * factor)
    Filtered_data_rbr, w, h, N, delay = filters.butterworth(RBRDepthArr, btype, lowcut, highcut, fs2, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = recurse, debug = debug)
    if len(Filtered_data_rbr) != len(RBRdateTimeArr):
        RBRdateTimeArr_res = scipy.signal.resample(RBRdateTimeArr, len(Filtered_data_rbr))
    else :
        RBRdateTimeArr_res = RBRdateTimeArr


    print "Start display: poincare_wave_in_lontario"

    # superimposed filtered data for he period oscillation freq
    custom1 = "Poincare signature in Lake Ontario"  # % isotemp
    custom2 = custom1
    # custom2 = "Isotherme %d ($^\circ$C) depth (m)" % isotemp
    custom = [custom1, custom2]
    t01 = ['0', '3', '6', '9', '12', '15', '18', '21', '24', '27']
    t02 = [27, 24, 21, 18, 15, 12, 9, 6, 3, 0]
    t11 = ['0', '2', '4', '6', '8', '10', '12', '14', '16', '18', '20']
    t12 = [20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0]
    tick1 = [t01, t02]
    tick2 = [t11, t12]
    tick = [tick1, tick2]
    revert_y = True



    utils.display_data.display_depths_subplot([HOBOdateTimeArr_res[1:], RBRdateTimeArr_res[1:]], [Filtered_data[1:], Filtered_data_rbr[1:]], maxdepth = None, \
                                       fnames = fnames, yday = yday, revert = False, tick = None, custom = custom, firstlog = None)

    debug = False;
    if debug:
        # tick = [tick1]
        revert_y = True  # this will revert only depths tick on the y axis

        utils.display_data.display_depths_subplot([HOBOdateTimeArr[1:], HOBOdateTimeArr_res[1:]], [HOBODepthArr[1:], Filtered_data[1:]], maxdepth = None, \
                                             fnames = fnames, yday = yday, revert = False, tick = None, custom = [custom1, "FFT"], firstlog = None)

def kelvin_wave_in_lontario(data, fnames):

    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    print "Start kelvin_wave_in_lontario()"
    HOBOdateTimeArr = data[0][0]
    HOBODepthArr = data[0][1]
    RBRdateTimeArr = data[1][0]
    RBRDepthArr = data[1][1]

    # Kelvin 10-15 day
    lowcut = 1.0 / (24 * 10) / 3600
    highcut = 1.0 / (24 * 3) / 3600
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


    btype = 'band'
    fs1 = 1.0 / ((HOBOdateTimeArr[2] - HOBOdateTimeArr[1]) * factor)
    Filtered_data = numpy.zeros(len(HOBOdateTimeArr) + 1, dtype = numpy.float)
    Filtered_data, w, h, N, delay1 = filters.butterworth(HOBODepthArr, btype, lowcut, highcut, fs1, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = recurse, debug = debug)
    if len(Filtered_data) != len(HOBOdateTimeArr):
        HOBOdateTimeArr_res = scipy.signal.resample(HOBOdateTimeArr, len(Filtered_data))
    else :
        HOBOdateTimeArr_res = HOBOdateTimeArr


    fs2 = 1.0 / ((RBRdateTimeArr[2] - RBRdateTimeArr[1]) * factor)
    Filtered_data_rbr, w, h, N, delay2 = filters.butterworth(RBRDepthArr, btype, lowcut, highcut, fs2, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = recurse, debug = debug)
    if len(Filtered_data_rbr) != len(RBRdateTimeArr):
        RBRdateTimeArr_res = scipy.signal.resample(RBRdateTimeArr, len(Filtered_data_rbr))
    else :
        RBRdateTimeArr_res = RBRdateTimeArr


    print "Start display: poincare_wave_in_lontario"

    # superimposed filtered data for he period oscillation freq
    custom1 = "Hobo Kelvin signature in Lake Ontario"  # % isotemp
    custom2 = "RBR Kelvin signature in Lake Ontario"
    # custom2 = "Isotherme %d ($^\circ$C) depth (m)" % isotemp
    custom = [custom1, custom2]
    t01 = ['0', '3', '6', '9', '12', '15', '18', '21', '24', '27']
    t02 = [27, 24, 21, 18, 15, 12, 9, 6, 3, 0]
    t11 = ['0', '2', '4', '6', '8', '10', '12', '14', '16', '18', '20']
    t12 = [20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0]
    tick1 = [t01, t02]
    tick2 = [t11, t12]
    tick = [tick1, tick2]
    revert_y = True



    # display_data.display_depths_subplot([HOBOdateTimeArr_res[1:], RBRdateTimeArr_res[1:]], [Filtered_data[1:], Filtered_data_rbr[1:]], maxdepth = None, \
    #                                   fnames = fnames, yday = yday, revert = False, tick = None, custom = custom, firstlog = None)

    # superimposed filtered data for the period oscillation freq
    difflines = True
    utils.display_data.display_temperatures([numpy.subtract(HOBOdateTimeArr_res[1:], delay1), numpy.subtract(RBRdateTimeArr_res[1:], delay1)], [Filtered_data[1:], Filtered_data_rbr[1:]],
                                       [], fnames = fnames, difflines = difflines, custom = custom)



def poincare_wave_in_harbour(period, dateinterval, paths):

    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    print "Start poincare_wave_in_harbour()"
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
        yday = True
        debug = False
        order = None
        gpass = 9
        astop = 32
        recurse = True


        btype = 'band'

        for data in HOBOdateTimeArr:
            fs1 = 1.0 / ((HOBOdateTimeArr[i][2] - HOBOdateTimeArr[i][1]) * factor)
            Filtered_data[i], w, h, N, delay = filters.butterworth(HOBOtempArr[i], btype, lowcut, highcut, fs1, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = recurse, debug = debug)
            i += 1

        # get hobo file from the lake
        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE-Apr-May_2012-Thermistor_chain/csv_processed'
        hobofilename = '18_2393005.csv'  # 10m deep sensor
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
        Filtered_data[len(HOBOresultsArr) - 1], w, h, N, delay = filters.butterworth(temp, btype, lowcut, highcut, fs, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = recurse, debug = debug)


        print "Start display ####### SHOULD BE display_depths??????? "
        # SHOULD BE display_depths ?????
        utils.display_data.display_temperatures_subplot(HOBOdateTimeArr, HOBOtempArr, HOBOresultsArr, k, fnames = fnames, yday = yday)

        # superimposed filtered data for the period oscillation freq
        difflines = True
        custom = "%sh filter- Temperature " % str(period)
        utils.display_data.display_temperatures(HOBOdateTimeArr, Filtered_data, k, fnames = fnames, difflines = difflines, custom = custom)
    # end for path

def calculate_statistics(arr):
    sz = len(arr)
    avg = numpy.average(arr)
    min = numpy.min(arr)
    max = numpy.max(arr)

    dof = fft_utils.dof(arr)
    out = scipy.stats.bayes_mvs(arr, alpha = 0.95)

    # take the median as that is what we are interested in
    avgidx = 0
    (x05, x95) = out[avgidx][1]

    # test with other method
    # CImean = bootstrap.ci(data = arr, statfunction = scipy.mean)
    # print "Bootstrapped 95% confidence intervals  MEAN\nLow:", CImean[0], "\nHigh:", CImean[1]



    return  [avg, max, min, x05, x95]

def write_statistics(writer, station, day, unixtime, avg, max, min, x05 = None, x95 = None, all = False):
    idx = 0
    numdat = []
    prev = 0
    prevtxt = ''
    # print "len(depth) :%d, len(dateTime):%d" % (len(depth), len(dateTime))
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    if all == False:
        writer.writerow([day, unixtime, avg, max, min])
    else:
        writer.writerow([day, unixtime, avg, max, min, x05, x95])


def calculate_harbour_statistics(path, path_out, timeinterv, all = False, NOVAPRIL = None):
    '''
    calculate avg, min, max /day/sensor-
    '''

    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

    dateTime, temp, results, k , fnames = readTempHoboFiles.read_files(window_hour, windows[1], timeinterv, path)
    HOBOdateTimeArr = dateTime
    HOBOresultsArr = results
    HOBOtempArr = temp

    if all == False:
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
                    [savg, smax, smin] = calculate_statistics(numpy.array(daytemps))
                    # insert in a spreadsheet
                    write_statistics(writer, station, daystr, dateTime[j], savg, smax, smin)

                    # clear the array
                    OlddayOfTheYear = dayOfTheYear
                    daytemps = []
                elif j == 0:
                    OlddayOfTheYear = dayOfTheYear
            # END FOR
            ofile.close()
        # end for
    else:
        g_ofile = open(path_out + '/' + 'all_stations.csv', "wb")
        gwriter = csv.writer(g_ofile, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
        write_statistics(gwriter, "Station", "Date", "Timestamp", "Avg Temp", "Max Temp", "Min Temp", "Con. lev 5%", "Conf lev 95%", all = all)

        dayOfTheYear = 0
        OlddayOfTheYear = 0
        gdaytemps = numpy.zeros(366, numpy.ndarray)  # days in a year
        for k in range(0, 366):
            gdaytemps[k] = []
        maxlen = 0
        for k in range(0, len(HOBOdateTimeArr)):
            maxlen = max(maxlen, len(HOBOdateTimeArr[k]))

        for j in range(1, maxlen):  # loop over time
            try:
                datet = num2date(HOBOdateTimeArr[0][j])
            except IndexError:
                # this is expected as not all recoreds have the same length
                continue
            except Exception:
                print "This is not expected error"

            dayOfTheYear = datet.timetuple().tm_yday


            if dayOfTheYear != OlddayOfTheYear and j != 1:
                day = num2date(HOBOdateTimeArr[0][j - 1])
                daystr = day.strftime("%d %B %Y")

                datet = num2date(HOBOdateTimeArr[0][j])
                dayOfTheYear = datet.timetuple().tm_yday

                # calculate stats
                [gavg, gmax, gmin, x05, x95] = calculate_statistics(numpy.array(gdaytemps[OlddayOfTheYear]))

                # insert in a spreadsheet
                write_statistics(gwriter, j, daystr, HOBOdateTimeArr[0][j], gavg, gmax, gmin, x05, x95, all = all)

                # clear the array
                OlddayOfTheYear = dayOfTheYear
                # gdaytemps = []
            elif j == 1:
                OlddayOfTheYear = dayOfTheYear

            try:
                for i in range(0, len(HOBOdateTimeArr)):  # loop over all stations
                    station = fnames[i]

                    # eliminate faulty data
                    if NOVAPRIL != None:
                        if HOBOtempArr[i][j] > 13 and (dayOfTheYear > 270 or dayOfTheYear < 150):
                            day = num2date(HOBOdateTimeArr[i][j])
                            daystr = day.strftime("%d %B %Y")
                            print "* Faulty station : %s: temp:%f, date:%s" % (station, HOBOtempArr[i][j], daystr)
                        else:  # add data
                            gdaytemps[dayOfTheYear].append(HOBOtempArr[i][j])
                    else:
                        gdaytemps[dayOfTheYear].append(HOBOtempArr[i][j])
            except Exception as e:
                # print "** Bad series : %s" % (station)
                # print 'Exception error is: %s' % e
                pass
            # end for i

        # end for
        g_ofile.close()
    # end if all == False

# end harbour_statistics

def draw_harbour_statistics(path, timeinterv, selector, all = False):

    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')



    for i in range(0, len(selector)):

        type = selector[i]

        if all:
            dateTime, temp, result, k, fnames, x05, x95 = readTempHoboFiles.read_stat_files(window_hour, windows[1], timeinterv, path, type, all = all)
        else:
            dateTime, temp, result, k, fnames = readTempHoboFiles.read_stat_files(window_hour, windows[1], timeinterv, path, type, all = all)

        if all:
            difflines = False
            custom = "%s - Temperature " % type
            utils.display_data.display_temperatures(numpy.array([dateTime[1:]]), numpy.array([temp[1:]]), \
                                              numpy.array([result[1:]]), k, fnames = [ type], difflines = difflines, custom = custom)

        else:
            HOBOdateTimeArr = dateTime
            HOBOtempArr = temp
            HOBOresultsArr = result
            print "Start display %s" % type

            # display_data.display_temperatures_subplot(HOBOdateTimeArr, HOBOtempArr, HOBOresultsArr, k, fnames = fnames)

            # superimposed filtered data for he period oscillation freq
            difflines = False

            custom = "%s - Temperature " % type

            if type == 'avg':
                utils.display_data.display_temperatures(numpy.array([HOBOdateTimeArr[0][1:], HOBOdateTimeArr[0][1:], HOBOdateTimeArr[0][1:]]), numpy.array([HOBOtempArr[0][1:], x05, x95]), \
                                              numpy.array([HOBOresultsArr[0][1:], HOBOresultsArr[0][1:], HOBOresultsArr[0][1:]]), k, fnames = [ type, '5%', '95%'], difflines = difflines, custom = custom)
            else:
                utils.display_data.display_temperatures(numpy.array([HOBOdateTimeArr[0][1:]]), numpy.array([HOBOtempArr[0][1:]]), \
                                              numpy.array([HOBOresultsArr[0][1:]]), k, fnames = [ type], difflines = difflines, custom = custom)

def harbour_statistics(all = False):
    #---------------------------------------------------------
    # Simple statititics for the NSERC Files
    #---------------------------------------------------------
    path = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed'
    path_out = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed/stats'
    # path = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Apr2012-Tor_Harb/csv_processed'
    # if all == False:
    #    path_out = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Apr2012-Tor_Harb/csv_processed/stats'
    # else:
    #    path_out = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Apr2012-Tor_Harb/csv_processed/allstats'
    # path_out = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Apr2012-Tor_Harb/csv_processed/stats/sample'

    # startdate = '11/02/01 00:00:00'
    # enddate = '12/10/24 00:00:00'
    startdate = '12/04/21 00:00:00'
    enddate = '12/10/24 00:00:00'

    dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
    start_num = date2num(dt)
    dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
    end_num = date2num(dt)

    #-----------------------------------------------------------------
    # Calculate statitics
    calculate_harbour_statistics(path, path_out, [start_num, end_num], all = all)
    # draw some graphs
    #-------------------------------------------------------------------
    draw_harbour_statistics(path_out, [start_num, end_num], ['max', 'avg', 'min'], all = all)
    print "Done!"




if __name__ == '__main__':
    harbour_stats = False  # 0
    LO_hobot_rbrt_10m = False  # 1
    LO_isotherm = False  # 2
    Toronto_harbour = False  # 3
    atm_correlation = False  # 4
    Toronto_harb_filter = False  # 5
    TRCA_data = False  # 6
    Upwelling_zone = False  # 7
    Fish_detection = True  # 8

    exit_if = [False, False, False, False, False, False, False, False, False]

    if harbour_stats:
        all = True
        harbour_statistics(all)
        print "Done!harbour_stats "
        if exit_if[0]:
            "Exit!"
            os.abort()

    #---------------------------------
    # Set the start and end date-time
    #---------------------------------
    startdate = '12/07/19 00:00:00'
    enddate = '12/10/24 00:00:00'
    dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
    start_num = date2num(dt)
    dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
    end_num = date2num(dt)


    if LO_hobot_rbrt_10m:
        #-----------------------------------------------------------
        # Set the paths and sepcific data for the isotherm locations
        #-----------------------------------------------------------
        paths = ['/home/bogdan/Documents/UofT/PhD/Data_Files/MOE-Apr-May_2012-Thermistor_chain/csv_processed',
                 '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE deployment 18-07-2012/Data/RBR']
        # paths = ['/home/bogdan/Documents/UofT/PhD/Data_Files/MOE-Apr-May_2012-Thermistor_chain/csv_processed', '']
        paths = ['/home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/nLake/Cell3', '']
        waterdepths = [27, 20]  # water depths at the location
        top_log_depths = [3, 4]
        delta_ls = [1, 1]  # loggers interval

        fnames = ['18_2393005.csv', '019513.dat']
        zNames = ['Hobo', 'RBR']

        # fnames = ['18_2393005.csv', ''];  zNames = ['L_Ontario', '']
        # fnames = ['Surf_Cell_3.csv', '']; zNames = ['Hobo - Cell 3 Surf', '']
        fnames = ['Bot_Cell_3.csv', '']; zNames = ['Hobo - Cell 3 Bot', '']

        read_LOntario_files(paths, fnames, [start_num, end_num], chain = "hobo" , zNames = zNames, bfilter = True, bkelvin = True)

        if exit_if[1]:
            print "Done! LO_hobot_rbrt_10m"
            os.abort()

    if LO_isotherm:
        paths = ['/home/bogdan/Documents/UofT/PhD/Data_Files/MOE-Apr-May_2012-Thermistor_chain/csv_processed',
                 '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE deployment 18-07-2012/Data/RBR']

        waterdepths = [27, 20]  # water depths at the location
        top_log_depths = [3, 4]
        delta_ls = [1, 1]  # loggers interval
        # draw the isotherm oscillations
        temp = 13.0
        # Filter in [ lo period, hi period] = > [Hi freq, lo freq]
        filter = None  # [16.5, 17.5]

        period_hours = 17
        startdate = '12/07/19 00:00:00'
        enddate = '12/10/24 00:00:00'
        dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
        start_num = date2num(dt)
        dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
        end_num = date2num(dt)

        [hobo, rbr] = isoterm_oscillation(temp, paths, waterdepths, top_log_depths, delta_ls, [start_num, end_num], filter)

        fnames = ['Hobo t-Chain', 'RBR t-Chain']
        # poincare_wave_in_lontario(period_hours, [start_num, end_num], [hobo, rbr], fnames, waterdepths, temp)
        # kelvin_wave_in_lontario(period_hours, [hobo, rbr], fnames, waterdepths, temp)
        kelvin_wave_in_lontario([hobo, rbr], fnames)

        print "Done! LO_isotherm"
        if exit_if[2]:
            print "Exit! "
            os.abort()

    if Toronto_harbour:
        #---------------------------------------------------
        # Read all files in Toronto Harbour for temperature
        #----------------------------------------------------

        #           Filename        [Location, depth, total-depth]
#===============================================================================
#         filemap = {
#                    'Stn_21_-_Curtain_-_9678892.csv'      : ['Stn 21', 7, 6.5],
#                    'Stn_29_-_E_Western_Gap_-_9992436.csv'   : ['Stn 29', 9, 8.5],
#                    'Stn_34_-_Don_River_Mouth_-_9988085.csv'  : ['Stn 34', 3, 3.5],
#                    'Stn_50_-_Don_River_-_9988088.csv' : ['Stn 50', 2, 1.5],
#                    'Stn_28_-_W_Western_Gap_-_9674471.csv'   : ['Stn 28', 9, ],
#                    'Stn_32-_S_Eastern_Gap_-_1020953.csv'    : ['Stn 32', 10, ],
#                    'Stn_49_-_turning_basin_-_2393007.csv' : ['Stn 49', 5, 4.5],
#                    'Stn_10_-_Embayment_C_-_9674470.csv'   : ['Stn 10', 6, 5.5],
#                    'Stn_37_-_Cell_3_-_1020754.csv'   : ['Stn 37', 5, 4.5],
#                    'Stn38_-_Cell_2_-_1020773.csv' : ['Stn 38', 3, 2.5],
#                    'stn_17_-_2393004.csv' : ['Stn 17', 6, 5.5],
#                    'Stn_2_-_Cherry_Beach_-_1020769.csv': ['Stn 2', 11, 10.5],
#                    }
#         paths = ['/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed/upwelling-LO-21-10-37-38',
#                 # '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed/upwelling-LO-21-15-13',
#                 # '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed/upwelling-LO-21-15-14',
#                 '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed/upwelling-LO-21-17-2',
#                 '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed/upwelling-LO-28-21-34-32-49-50'
#                 ]
#
#
#         lo_path = '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE-Apr-May_2012-Thermistor_chain/csv_processed'
#         lo_file = '/18_2393005.csv'
#
#         startdate = '12/05/09 00:00:00'
#         enddate = '12/10/24 00:00:00'
#===============================================================================

        filemap = {'10098826.csv' : ['TC1', 8, 8],
                   '10098827.csv' : ['TC1', 7, 8],
                   '10098838.csv' : ['TC2', 10.2, 10.2],
                   '10098839.csv' : ['TC2', 9, 10.2],
                   '10226021.csv' : ['TC4', 6.5, 6.5],
                   '10226030.csv' : ['TC4', 5.5, 6.5],
                   '10298872.csv' : ['TC3', 10.7 , 10.7],
                   '10298873.csv' : ['TC3', 9.7 , 10.7],
                   '1020767.csv'  : ['St 2', 9.2, 11.2],
                   '1020769.csv'  : ['St 2', 8.2, 11.2],
                   '1157458.csv'  : ['St 2', 10.2, 11.2],
                   'Station21November.csv':  ["St 21", 9, 10],
                   }

        paths = ['/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/csv_processed']
        # path = '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE-Apr-May_2012-Thermistor_chain/csv_processed'
        lo_path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-LakeOntario/csv_processed'
        lo_file = '/24_10298867.csv'  # '/11_2395420.csv'  # '/07_2393002.csv'
        startdate = '13/05/01 00:00:00'
        enddate = '13/10/30 00:00:00'



        period = [startdate, enddate]

        # filter
        lowcut = 1.0 / (24 * 10) / 3600
        highcut = 1.0 / (24 * 3) / 3600
        filter = [lowcut, highcut]
        moving_avg = window_7days  # for upwellin

        filter = None
        moving_avg = window_hour  # for regular study

        read_Tor_Harbour_files(paths, lo_path, lo_file, moving_avg, filemap, period, filter = None)  # this can filter too and  exhibit poincare waves
        print "Done! Toronto harbour"
        if exit_if[3]:
            print "Exit! "
            os.abort()

    if atm_correlation:
        #---------------------------------------------------
        # Correlate with meteorologic data
        #---------------------------------------------------
        wind_airpress_airtemp_water_temp()
        print "Done! atm_correlation"
        if exit_if[4]:
            print "Exit! "
            os.abort()

    if Toronto_harb_filter:
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

        print "Done! Toronto_harb_filter"
        if exit_if[5]:
            print "Exit!"
            os.abort()
    if TRCA_data:
        paths = ['/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo-TRCA/2012/csv_processed/selected']
        read_TRCA_files(paths)
        if exit_if[6]:
            print "Exit!"
            os.abort()

    if Upwelling_zone:
        # no lake data
        # path = '/home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/nLake'
        # with lake data
        # path = '/home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/wLake'
        # FFT
        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/FFT_Surf'
        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/FFT_Bot'
        # path = '/home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/allStations'
        startdate = '12/05/19 00:00:00'
        enddate = '12/10/24 00:00:00'

        # filtering
        filt = "semidiurnal"

        if filt == "k3_7":
            # Kelvin 3-7 days
            lowcut = 1.0 / (24 * 10) / 3600
            highcut = 1.0 / (24 * 3) / 3600
            filter = [lowcut, highcut]
        elif filt == "k10_15":
            # Kelvin 10-15 days
            lowcut = 1.0 / (24 * 15) / 3600
            highcut = 1.0 / (24 * 10) / 3600
            filter = [lowcut, highcut]
        elif filt == "poincare":
            # poincare
            lowcut = 1.0 / (17.3) / 3600
            highcut = 1.0 / (16.6) / 3600
            filter = [lowcut, highcut]
        elif filt == "diurnal":
            # diurnal
            lowcut = 1.0 / (24.2) / 3600
            highcut = 1.0 / (23.8) / 3600
            filter = [lowcut, highcut]
        elif filt == "semidiurnal":
            # diurnal
            lowcut = 1.0 / (12.1) / 3600
            highcut = 1.0 / (11.9) / 3600
            filter = [lowcut, highcut]
        else:
            filter = None



        dateTime, results, temp, fnames, tunits, zoneName = upwelling.read_Upwelling_files(path, [startdate, enddate], timeavg = window_3days, subplot = None, fft = False)
        # upwelling.read_Upwelling_files(path, [startdate, enddate], timeavg = window_3days, subplot = None, filter = None, fft = True, stats = True, with_weather = False)
        # upwelling.draw_upwelling_correlation('/home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/SelectedZonesMouth-NoLO.csv')
        # upwelling.draw_upwelling_correlation('/home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/UCIZones.csv')
        # upwelling.draw_upwelling_correlation_all('/home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/AllZones.csv')
        # upwelling.draw_upwelling_correlation('/home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/SelectedZones-NoLO.csv')
        # upwelling.draw_upwelling_correlation_IQR('/home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/SelectedZones-NoLO.csv')

        # Calculate upwelling indices and plot the shaded uwelling zones defined by the 30 days running average.
        upwelling.calculate_Upwelling_indices(dateTime, results, fnames, tunits, zoneName)

        if filter:
            upwelling.plot_buterworth_filtered_data(dateTime, temp, filter, stats = True,)

        if exit_if[7]:
            print "Exit Upwelling!"
            os.abort()

    if Fish_detection:
        path = "/home/bogdan/Documents/UofT/PhD/Data_Files/2012/Fish-data-Apr-Dec-2012/NumDate-May-Nov2012.csv"

        startdate = '12/05/19 00:00:00'
        enddate = '12/10/24 00:00:00'

        path = "/home/bogdan/Documents/UofT/PhD/Data_Files/2013/FishData/numdate_bass_2013.csv"
        startdate = '13/06/20 00:00:00'
        enddate = '13/10/24 00:00:00'


        count_detect = True
        draw = False
        year = 2013
        # this is just to estimate detection
        if count_detect:
            fish_detection.fish_detection(path, [startdate, enddate], year)

        if draw:
            upwelling.draw_upwelling_fish_correlation('/home/bogdan/Documents/UofT/PhD/Data_Files/2012/UpwellingZones/SelectedZonesFishDetection.csv')
            # upwelling.draw_upwelling_fish_correlation_all('/home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/AllZones.csv')
            # NO cells file is not good.
            # upwelling.draw_upwelling_fish_correlation_all('/home/bogdan/Documents/UofT/PhD/Data_Files/UpwellingZones/AllZonesNoCells.csv')
        if exit_if[8]:
            print "Exit!"
            os.abort()
    print "Done! Script"

