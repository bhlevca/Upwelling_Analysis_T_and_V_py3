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
import smooth
import display_data

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

    results = smooth.smoothfit(dateTime, temp, span, window)

    # print "Station:%s group:%s depth: %d residuals:%f determination:%f " % (k, name, pair[k], results['residual'], results['determination'])
    # writer.writerow([k, name, id, pair[k], results['residual'], results['determination']])
    ifile.close()
    return [dateTime, temp, results['smoothed']]


def read_files(path):
    windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
    window_default = 1
    window_hour = 900  # every 4sec
    window_6hour = window_hour * 6

    window_day = window_hour * 24
    window_half_day = window_hour * 12
    dirs = numpy.array(os.listdir(path))
    dirList = dirs[dirs.argsort()]
    dateTimeArr = numpy.zeros(len(dirList), dtype = numpy.ndarray)
    tempArr = numpy.zeros(len(dirList), dtype = numpy.ndarray)
    resultsArr = numpy.zeros(len(dirList), dtype = numpy.ndarray)
    k = numpy.zeros(len(dirList), dtype = numpy.ndarray)
    fNameArr = numpy.zeros(len(dirList), dtype = numpy.ndarray)
    i = 0
    dirNo = 0
    for fname in dirList:
        # skip dirs
        if os.path.isdir(path + '/' + fname):
            dirNo += 1
            continue
        fNameArr[i] = fname
        print "Reading file %s" % fname
        dateTime, temp, results = get_data_from_file(fname, window_hour, windows[1])
        # index is specific to the files read and needs to be modified for other readings
        minidx = 50000
        maxidx = 2500000  # 30000
        dateTimeArr[i] = numpy.append(dateTimeArr[i], dateTime[minidx:maxidx])
        resultsArr[i] = numpy.append(resultsArr[i], results[minidx:maxidx])
        tempArr[i] = numpy.append(tempArr[i], temp[minidx:maxidx])
        k[i] = numpy.append(k[i], i)
        i += 1
    # end for

    revert = True

    display_data.display_temperatures(dateTimeArr[:-dirNo], tempArr[:-dirNo], resultsArr[:-dirNo], k[:-dirNo], fNameArr[:-dirNo], revert)

    t11 = ['0', '2', '4', '6', '8', '10', '12', '14', '16', '18', '20']
    t12 = [20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0]
    tick = [t11, t12]
    maxdepth = 20
    firstlogdepth = 4
    maxtemp = 25
    display_data.display_img_temperatures(dateTimeArr[:-dirNo], tempArr[:-dirNo], resultsArr[:-dirNo], k[:-dirNo], tick, maxdepth, firstlogdepth, maxtemp, revert)

    # profile is specific to the files read and needs to be modified for other readings
    profiles = [80000, 120000, 350000, 540000, 730000, 920000, 1110000, 1300000]
    legendpos = 2  # upper left
    display_data.display_vertical_temperature_profiles(dateTimeArr[:-dirNo], tempArr[:-dirNo], resultsArr[:-dirNo], k[:-dirNo], firstlogdepth, profiles, revert, legendpos)


# main

if __name__ == '__main__':

    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    read_files(path)
    print "Done!"
