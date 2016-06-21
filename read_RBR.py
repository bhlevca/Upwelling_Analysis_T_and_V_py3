import csv
import numpy
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import date2num, num2date
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates
import time, os, locale
from scipy.interpolate import UnivariateSpline

# turn off warning in polyfit
import warnings
warnings.simplefilter('ignore', numpy.RankWarning)
from utools import smooth
from utools import display_data

header = '''
RBR TR-1060  6.77 019518 (Windows: 6.13 - Minimum required: 6.13)
Host time     12/11/22 14:17:54
Logger time   12/11/22 15:16:37
Logging start 12/07/16 00:00:00
Logging end   12/11/22 07:49:04
Sample period          00:00:04
Number of channels =  1, number of samples = 2793437, mode: Logging Complete
N01%9.4f
Calibration  1: 0.003494264332975
                -0.000250840377853
                0.000002481479905
                -0.000000070159135 Degrees_C
COMMENT: 19518
Memory type: 6 AT45DB642D_LP
'''

windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
window_6hour = "window_6hour"  # window_hour * 6
window_hour = "window_hour"  #  900  # every 4sec
window_day = "window_day"  # window_hour * 24
window_half_day = "window_half_day"  # window_hour * 12
window_3days = "window_3days"  # 3 * 30 * 24
window_7days = "window_7days"  # 7 * 30 * 24


# window_hour = 900  # every 4sec
# window_6hour = window_hour * 6
# window_day = window_hour * 24
# window_half_day = window_hour * 12

path = '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE deployment 18-07-2012/Data/RBR'

def hms_to_seconds(t):
    h, m, s = [int(i) for i in t.split(':')]
    return 3600 * h + 60 * m + s

def read_version(row):
    sub = "RBR TR-1060  "
    # try:
    idx = row.index(sub)
    st = idx + len(sub)
    ver = row[st:st + 4]
    # except:
    #    pass
    return float(ver)

def read_starttime(row):
    sub = "Logging start "
    # try:
    idx = row.index(sub)
    st = idx + len(sub)
    strg = row[st:st + 17]
    dt = datetime.strptime(strg, "%y/%m/%d %H:%M:%S")
    dn = date2num(dt)
    # except:
    #    pass
    return dn

def read_endtime(row):
    sub = "Logging end   "
    # try:
    idx = row.index(sub)
    st = idx + len(sub)
    strg = row[st:st + 17]
    dt = datetime.strptime(strg, "%y/%m/%d %H:%M:%S")
    dn = date2num(dt)
    # except:
    #    pass
    return dn

def read_sampleperiod(row):
    sub = "Sample period"
    # try:
    idx = row.index(sub)
    st = idx + len(sub)
    strg = row[st + 10:st + 18]
    secs = hms_to_seconds(strg)
    # except:
    #    pass
    return secs

def read_data(reader, timeinterv = None):
    rownum = 0
    temp = []
    dateTime = []
    version = 0
    starttime = ""
    endtime = ""
    sampleperiod = ""
    curdate = 0
    rn = -1

    if timeinterv != None:
        startt = timeinterv[0]
        endt = timeinterv[1]

    datarow = 0
    for row in reader:
        rn += 1
        # try:
        if rn == 0:
            version = read_version(row[0])
            continue
        if rn == 3:
            starttime = read_starttime(row[0])
            curdate = starttime
            continue
        if rn == 4:
            endtime = read_endtime(row[0])
            continue
        if rn == 5:
            sampleperiod = read_sampleperiod(row[0])
            continue
        if rn < 15  :
            continue

        # Filter out data outside of interval if specified
        datarow += 1
        # seconds_in_a_day = 86400.0
        # time = starttime + sampleperiod / seconds_in_a_day * datarow
        if timeinterv != None:
            if curdate < startt or curdate > endt:
                curdate += matplotlib.dates.seconds(sampleperiod)
                continue

        if len(row[0]) < 20 :
            temp.append(float(row[0]))
        else:
            temp.append(float(row[0][20:]))
        # endif
        curdate += matplotlib.dates.seconds(sampleperiod)
        dateTime.append(curdate)

        # except:
        #    pass

    return [dateTime, temp]

def get_data_from_file(filename, span, window, timeinterv = None, rpath = None):
    if rpath != None:
        ppath = rpath
    else:
        ppath = path
    ifile = open(ppath + '/' + filename, 'rb')
    reader = csv.reader(ifile, delimiter = ',', quotechar = '"')
    [dateTime, temp] = read_data(reader, timeinterv)

    if span != None:
         # check if span is correct
        dt = dateTime[2] - dateTime[1]  # usually days
        if span == "window_6hour":  # 30 * 6 for a 2 minute sampling
            nspan = 6. / (dt * 24)
        elif span == "window_hour":  # 30 for a 2 minute sampling - 900 for a 4 sec sampling frequency.
            nspan = 1. / (dt * 24)
        elif span == "window_1/2hour":  # 30 for a 2 minute sampling
            nspan = 0.5 / (dt * 24)
        elif span == "window_day":  # 30 * 24 for a 2 minute sampling
            nspan = 24. / (dt * 24)
        elif span == "window_half_day":  # 30 * 12 for a 2 minute sampling
            nspan = 12. / (dt * 24)
        elif span == "window_3days":  # 3 * 30 * 24 for a 2 minute sampling
            nspan = 24. * 3 / (dt * 24)
        elif span == "window_7days":  # 7* 30 * 24 for a 2 minute sampling
            nspan = 24. * 7 / (dt * 24)

        results = utils.smooth.smoothfit(dateTime, temp, nspan, window)
    else:
        results = {}
        results['smoothed'] = temp
    # print "Station:%s group:%s depth: %d residuals:%f determination:%f " % (k, name, pair[k], results['residual'], results['determination'])
    # writer.writerow([k, name, id, pair[k], results['residual'], results['determination']])
    ifile.close()
    return [dateTime, temp, results['smoothed']]


def read_files_and_display(span, window, dateinterval, idxinterv, rpath):


    base, dirs, files = next(iter(os.walk(path)))

    dirList = sorted(files, key = lambda x: x.split('.')[0])

    dateTimeArr = numpy.zeros(len(dirList), dtype = numpy.ndarray)
    tempArr = numpy.zeros(len(dirList), dtype = numpy.ndarray)
    resultsArr = numpy.zeros(len(dirList), dtype = numpy.ndarray)
    k = numpy.zeros(len(dirList), dtype = numpy.ndarray)
    fNameArr = numpy.zeros(len(dirList), dtype = numpy.ndarray)
    i = 0
    dirNo = 0
    for fname in dirList:
        # skip dirs
        # if os.path.isdir(rpath + '/' + fname):
        #    dirNo += 1
        #    continue
        fNameArr[i] = fname
        print("Reading file %s" % fname)
        dateTime, temp, results = get_data_from_file(fname, span, window, dateinterval, rpath)
        # index is specific to the files read and needs to be modified for other readings
        minidx = idxinterv[0]
        maxidx = idxinterv[1]

        dateTimeArr[i] = numpy.append(dateTimeArr[i], dateTime[minidx:maxidx])
        resultsArr[i] = numpy.append(resultsArr[i], results[minidx:maxidx])
        tempArr[i] = numpy.append(tempArr[i], temp[minidx:maxidx])
        k[i] = numpy.append(k[i], i)
        i += 1
    # end for

    revert = True

    # display_data.display_temperatures(dateTimeArr[:-dirNo], tempArr[:-dirNo], resultsArr[:-dirNo], k[:-dirNo], fNameArr[:-dirNo], revert)
    utils.display_data.display_temperatures(dateTimeArr, tempArr, k, fNameArr, revert)

    t11 = ['0', '2', '4', '6', '8', '10', '12', '14', '16', '18', '20']
    t12 = [20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0]
    tick = [t11, t12]
    maxdepth = 20
    firstlogdepth = 4
    maxtemp = 25
    # display_data.display_img_temperatures(dateTimeArr[:-dirNo], tempArr[:-dirNo], resultsArr[:-dirNo], k[:-dirNo], tick, maxdepth, firstlogdepth, maxtemp, revert)
    utils.display_data.display_img_temperatures(dateTimeArr, tempArr, resultsArr, k, tick, maxdepth, firstlogdepth, maxtemp, revert)

    # profile is specific to the files read and needs to be modified for other readings
    profiles = [80000, 120000, 350000, 540000, 730000, 920000, 1110000, 1300000]
    legendpos = 2  # upper left
    # display_data.display_vertical_temperature_profiles(dateTimeArr[:-dirNo], tempArr[:-dirNo], resultsArr[:-dirNo], k[:-dirNo], firstlogdepth, profiles, revert, legendpos)
    utils.display_data.display_vertical_temperature_profiles(dateTimeArr, tempArr, resultsArr, k, firstlogdepth, profiles, revert, legendpos)


def read_files(span = None, window = windows[1], dateinterval = None, path = None):

    # dirs = numpy.array(os.listdir(path))
    # Separate directories from files
    base, dirs, files = next(iter(os.walk(path)))

    fileList = sorted(files, key = lambda x: x.split('.')[0])

    dateTimeArr = numpy.zeros(len(fileList), dtype = numpy.ndarray)
    tempArr = numpy.zeros(len(fileList), dtype = numpy.ndarray)
    resultsArr = numpy.zeros(len(fileList), dtype = numpy.ndarray)
    k = numpy.zeros(len(fileList), dtype = numpy.ndarray)
    fNameArr = numpy.zeros(len(fileList), dtype = numpy.ndarray)
    i = 0
    dirNo = 0
    for fname in fileList:
        fNameArr[i] = fname
        print("Reading file %s" % fname)
        dateTime, temp, results = get_data_from_file(fname, span, window, dateinterval, path)
        # index is specific to the files read and needs to be modified for other readings
        dateTimeArr[i] = numpy.append(dateTimeArr[i], dateTime)
        resultsArr[i] = numpy.append(resultsArr[i], results)
        tempArr[i] = numpy.append(tempArr[i], temp)
        k[i] = numpy.append(k[i], i)
        i += 1
    # end for
    return [dateTimeArr, tempArr, resultsArr, k, fNameArr]




# main

if __name__ == '__main__':
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

    read_files_and_display(span = window_hour, window = windows[1], dateinterval = None, idxinterv = [50000, 2500000], rpath = path)
    print("Done!")
