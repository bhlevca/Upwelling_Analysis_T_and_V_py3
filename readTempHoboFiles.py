import csv
import numpy
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import date2num, num2date
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates
import time, os, datetime
from scipy.interpolate import UnivariateSpline
import display_data


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


path = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2011/csv_processed'
path_out = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2011/csv_processed/out'
path = '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE-Apr-May_2012-Thermistor_chain/csv_processed'
path_out = '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE-Apr-May_2012-Thermistor_chain/csv_processed/out'

filelist = {2:'1020769_Stn_02_03-11-11.csv', \
            38:'1020773_Stn_38_02-11-11.csv', \
            9:'1020949_Stn_09_09-11-11.csv', \
            32:'1020953_Stn_32_04-11-11.csv', \
            17:'2393004_Stn_17_02-11-11.csv', \
            49:'2393007_Stn_49_09-11-11.csv', \
            35:'2393008_Stn_35_04-11-11.csv', \
            51:'2393009_Stn_51_04-11-11.csv', \
            31:'2395421_Stn_31_04-11-11.csv', \
            39:'9674466_Stn_39_04-11-11.csv', \
            53:'9674467_Stn_53_03-11-11.csv', \
            13:'9674469_Stn_13_03-11-11.csv', \
            10:'9674470_Stn_10_03-11-11.csv', \
            52:'9674475_Stn_52_04-11-11.csv', \
            21:'9678892_Stn_21_03-11-11.csv', \
            14:'9678893_Stn_14_02-11-11.csv', \
            1:'9678895_Stn_01_03-11-11.csv', \
            37:'1020754_Stn_37_13-12-11.csv', \
            28:'9674471_Stn_28_13-12-11.csv', \
            44:'9674468_Stn_44_13-12-11.csv'

            }




# groups
# station number:depth - dictionary
lake_num = {17:6, 21:7, 53:6.5}
channel_num = {31:10, 32:10, 28:9}
cells_shelter_num = {38:2.5, 39:1.5, 52:4, 37:5}
sheltered_shore_num = {35:3.5, 9:1, 51:9, 44:4}
embayments_num = {10:6, 13:2.5, 14:4.5, 1:5.5, 2:11, 49:10}





def read_data(reader, timeinterv = None):
    rownum = 0
    temp = []
    dateTime = []
    printHeaderVal = False

    if timeinterv != None:
        startt = timeinterv[0]
        endt = timeinterv[1]


    for row in reader:
        try:
            time = float(row[1])
            if timeinterv != None:
                if time < startt or time > endt:
                    continue

            dateTime.append(time)
            if (row[2] == ''):
                temp.append(float(1))
            else:
                temp.append(float(row[2]))
            # end if
        except:
            pass
    return [dateTime, temp]

def read_stats_data(reader, timeinterv = None, all = False):
    rownum = 0
    avgtemp = []
    maxtemp = []
    mintemp = []
    x05 = []
    x95 = []
    dateTime = []

    if timeinterv != None:
        startt = timeinterv[0]
        endt = timeinterv[1]

    if all == False:
        timeidx = 2
        avgidx = 3
        maxidx = 4
        minidx = 5
    else:
        timeidx = 1
        avgidx = 2
        maxidx = 3
        minidx = 4
        x05idx = 5
        x95idx = 6

    for row in reader:
        try:
            time = float(row[timeidx])
            if timeinterv != None:
                if time < startt or time > endt:
                    continue

            dateTime.append(time)
            avgtemp.append(float(row[avgidx]))
            maxtemp.append(float(row[maxidx]))
            mintemp.append(float(row[minidx]))
            if all:
                x05.append(float(row[x05idx]))
                x95.append(float(row[x95idx]))
            # end if
        except:
            pass
    if all:
        return [dateTime, avgtemp, maxtemp, mintemp, x05, x95]

    return [dateTime, avgtemp, maxtemp, mintemp]


def splinefit(x, y, degree):
    results = {}
    # print len(x), " ", len(y)
    s = UnivariateSpline(x, y, s = degree)

    # spline Coefficients
    results['spline'] = s.get_coeffs()

    # fit values, and mean
    yhat = s(x)
    # display2(x, y, yhat, 1)

    ybar = sum(y) / len(y)

    results['residual'] = rss = s.get_residual()

    # also can be calcualte below
    # for i in range(0, len(y)):
    #    rss += (y[i] - yhat[i]) ** 2

    sstot = sum([ (yi - ybar) ** 2 for yi in y])
    ssreg = sstot - rss
    results['determination'] = ssreg / sstot

    return results


# Polynomial Regression
def polyfit(x, y, degree):
    results = {}

    coeffs = numpy.polyfit(x, y, degree)

     # Polynomial Coefficients
    results['polynomial'] = coeffs.tolist()

    # r-squared
    p = numpy.poly1d(coeffs)


    # fit values, and mean
    yhat = [p(z) for z in x]
    # display2(x, y, yhat, 1)

    ybar = sum(y) / len(y)
    ssreg = sum([ (yihat - ybar) ** 2 for yihat in yhat])
    sstot = sum([ (yi - ybar) ** 2 for yi in y])
    results['determination'] = ssreg / sstot

    return results

def write_datefile(station, depth, residual, determination):
    idx = 0
    numdat = []
    prev = 0
    prevtxt = ''
    for row in depth:
        dt = datetime.strptime(dateTime[idx], "%m/%d/%y %I:%M:%S %p")
        dn = date2num(dt)

        if prev > dn:
            print "Next value lower!"
        writer.writerow([dn, row])
        prev = dn
        prevtxt = dateTime[idx]
        idx += 1
        numdat.append(dn)
    return numdat

#-----------------------------------------------------------
def analyze_data(pair, name, id, writer):


    for k, v in filelist.iteritems():

        if k in pair.keys():
            ifile = open(path + '/' + v, 'rb')
            reader = csv.reader(ifile, delimiter = ',', quotechar = '"')
            [dateTime, temp] = read_data(reader)
            # display(dateTime, temp, v, k)
            # results = polyfit(dateTime, temp, 50)
            # results = splinefit(dateTime, temp, 7000)
            span = window_day

            # check if span is correct
            dt = dateTime[2] - dateTime[1]  # usually days
            if span == "window_6hour":  # 30 * 6 for a 2 minute sampling
                nspan = 6. / (dt * 24)
            elif span == "window_hour":  # 30 for a 2 minute sampling
                nspan = 1. / (dt * 24)
            elif span == "window_day":  # 30 * 24 for a 2 minute sampling
                nspan = 24. / (dt * 24)
            elif span == "window_half_day":  # 30 * 12 for a 2 minute sampling
                nspan = 12. / (dt * 24)
            elif span == "window_3days":  # 3 * 30 * 24 for a 2 minute sampling
                nspan = 24. * 3 / (dt * 24)
            elif span == "window_7days":  # 7* 30 * 24 for a 2 minute sampling
                nspan = 24. * 7 / (dt * 24)

            results = smooth.smoothfit(dateTime, temp, nspan, windows[1])

            display_data.display2(dateTime, temp, results['smoothed'], k)

            print "Station:%s group:%s depth: %d residuals:%f determination:%f " % (k, name, pair[k], results['residual'], results['determination'])
            writer.writerow([k, name, id, pair[k], results['residual'], results['determination']])
            ifile.close()


def select_data():
    ofile = open(path_out + '/' + "variance_results.csv", "wb")
    writer = csv.writer(ofile, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
    writer.writerow(['Station', 'group', 'group id', 'depth', 'residual', 'determination'])


    analyze_data(channel_num, "channel", 1, writer)
    analyze_data(lake_num, "lake", 2, writer)
    analyze_data(cells_shelter_num, "cells_shelter", 3, writer)
    analyze_data(sheltered_shore_num, "sheltered_shore", 4, writer)
    analyze_data(embayments_num, "embayments", 5, writer)

    ofile.close()

def get_data_from_file(filename, span, window, timeinterv = None, rpath = None):
    if rpath != None:
        ppath = rpath
    else:
        ppath = path
    if os.path.isdir(ppath + "/" + filename) == False:
        ifile = open(ppath + '/' + filename, 'rb')
    else:
        return
    reader = csv.reader(ifile, delimiter = ',', quotechar = '"')
    [dateTime, temp] = read_data(reader, timeinterv)

    if span != None:
        # check if span is correct
        dt = dateTime[2] - dateTime[1]  # usually days
        if span == "window_6hour":  # 30 * 6 for a 2 minute sampling
            nspan = 6. / (dt * 24)
        elif span == "window_hour":  # 30 for a 2 minute sampling
            nspan = 1. / (dt * 24)
        elif span == "window_day":  # 30 * 24 for a 2 minute sampling
            nspan = 24. / (dt * 24)
        elif span == "window_half_day":  # 30 * 12 for a 2 minute sampling
            nspan = 12. / (dt * 24)
        elif span == "window_3days":  # 3 * 30 * 24 for a 2 minute sampling
            nspan = 24. * 3 / (dt * 24)
        elif span == "window_7days":  # 7* 30 * 24 for a 2 minute sampling
            nspan = 24. * 7 / (dt * 24)

        results = smooth.smoothfit(dateTime, temp, nspan, window)
    else:
        results = {}
        results['smoothed'] = temp

    # print "Station:%s group:%s depth: %d residuals:%f determination:%f " % (k, name, pair[k], results['residual'], results['determination'])
    # writer.writerow([k, name, id, pair[k], results['residual'], results['determination']])
    ifile.close()
    return [dateTime, temp, results['smoothed']]
    # return [dateTime, temp, temp]

def get_data_from_stats_file(fname, span, window, timeinterv, rpath, type, all = False):
    if rpath != None:
        ppath = rpath
    else:
        ppath = path
    if os.path.isdir(ppath + "/" + fname) == False:
        ifile = open(ppath + '/' + fname, 'rb')
    else:
        return
    reader = csv.reader(ifile, delimiter = ',', quotechar = '"')
    if all:
        [dateTime, avgtemp, maxtemp, mintemp, x05, x95] = read_stats_data(reader, timeinterv, all = all)
    else:
        [dateTime, avgtemp, maxtemp, mintemp] = read_stats_data(reader, timeinterv, all = all)

    if type == 'min':
        temp = mintemp
    elif type == 'max':
        temp = maxtemp
    elif type == 'avg':
        temp = avgtemp
    else:
        print "data type must be 'min', 'max' or 'avg'"

    if len(dateTime) != len(temp):
        pass
    else:
        print "len temp %d" % len(temp)

    # check if span is correct
#===============================================================================
#     dt = dateTime[2] - dateTime[1]  # usually days
#
#     if span == "window_6hour":  # 30 * 6 for a 2 minute sampling
#         nspan = 6. / (dt * 24)
#     elif span == "window_hour":  # 30 for a 2 minute sampling
#         nspan = 1. / (dt * 24)
#     elif span == "window_day":  # 30 * 24 for a 2 minute sampling
#         nspan = 24. / (dt * 24)
#     elif span == "window_half_day":  # 30 * 12 for a 2 minute sampling
#         nspan = 12. / (dt * 24
#     elif span == "window_3days":  # 3 * 30 * 24 for a 2 minute sampling
#         nspan = 24. * 3 / (dt * 24)
#     elif span == "window_7days":  # 7* 30 * 24 for a 2 minute sampling
#         nspan = 24. * 7 / (dt * 24)
#
#     results = smooth.smoothfit(dateTime, temp, nspan, window)
#===============================================================================

    # print "Station:%s group:%s depth: %d residuals:%f determination:%f " % (k, name, pair[k], results['residual'], results['determination'])
    # writer.writerow([k, name, id, pair[k], results['residual'], results['determination']])
    ifile.close()

    if all:
        return [dateTime, temp, temp, x05, x95]
    # return #[dateTime, temp, results['smoothed']]
    return [dateTime, temp, temp]


def read_files_and_display(rpath = None):
    if rpath != None:
        ppath = rpath
    else:
        ppath = path

    dirList = os.listdir(ppath)


    dateTimeArr = numpy.zeros(len(dirList), dtype = numpy.ndarray)
    tempArr = numpy.zeros(len(dirList), dtype = numpy.ndarray)
    resultsArr = numpy.zeros(len(dirList), dtype = numpy.ndarray)
    k = numpy.zeros(len(dirList), dtype = numpy.ndarray)
    i = 0
    for fname in dirList:
        dateTime, temp, results = get_data_from_file(fname, window_hour, windows[1], rpath = ppath)
        maxidx = 30000
        dateTimeArr[i] = numpy.append(dateTimeArr[i], dateTime[:maxidx])
        resultsArr[i] = numpy.append(resultsArr[i], results[:maxidx])
        tempArr[i] = numpy.append(tempArr[i], temp[:maxidx])
        k[i] = numpy.append(k[i], i)
        i += 1
    # end for

    # plot the temperature not the smoothed ones
    display_data.display_temperatures(dateTimeArr, tempArr, k, fnames = dirList, custom = "Temperature Toronto Waterfront Zones $^oC$")
    t11 = ['0', '3', '6', '9', '12', '15', '18', '21', '24', '27']
    t12 = [27, 24, 21, 18, 15, 12, 9, 6, 3, 0]
    tick = [t11, t12]
    maxdepth = 27
    firstlogdepth = 3
    maxtemp = 25
    display_data.display_img_temperatures(dateTimeArr, tempArr, resultsArr, k, tick, maxdepth, firstlogdepth, maxtemp, fontsize = 18)
    profiles = [1000, 3500, 4000, 5500, 10000, 15000, 20000, 25000]

    display_data.display_vertical_temperature_profiles(dateTimeArr, tempArr, resultsArr, k, firstlogdepth, profiles)

def read_files(span = None, window = windows[1], timeinterv = None, rpath = None):
    if rpath != None:
        ppath = rpath
    else:
        ppath = path

    dirList = os.listdir(ppath)

    # Separate directories from files
    base, dirs, files = iter(os.walk(ppath)).next()

    sorted_files = sorted(files, key = lambda x: x.split('.')[0])

    dateTimeArr = numpy.zeros(len(files), dtype = numpy.ndarray)
    tempArr = numpy.zeros(len(files), dtype = numpy.ndarray)
    resultsArr = numpy.zeros(len(files), dtype = numpy.ndarray)
    k = numpy.zeros(len(files), dtype = numpy.ndarray)
    fnames = numpy.zeros(len(files), dtype = numpy.chararray)
    i = 0
    for fname in sorted_files:  # dirList:
        print "Reading file %s" % fname
        if os.path.isdir(ppath + "/" + fname):
            continue

        dateTime, temp, results = get_data_from_file(fname, span, window, timeinterv, ppath)

        dateTimeArr[i] = numpy.append(dateTimeArr[i], dateTime)
        resultsArr[i] = numpy.append(resultsArr[i], results)
        tempArr[i] = numpy.append(tempArr[i], temp)
        k[i] = numpy.append(k[i], i)
        fnames[i] = fname
        i += 1
    # end for
    return [dateTimeArr, tempArr, resultsArr, k, fnames]

def read_stat_files(span, window, timeinterv, rpath, type, all = False):
    if rpath != None:
        ppath = rpath
    else:
        ppath = path

    dirList = os.listdir(ppath)

    # Separate directories from files
    base, dirs, files = iter(os.walk(ppath)).next()


    dateTimeArr = numpy.zeros(len(files), dtype = numpy.ndarray)
    tempArr = numpy.zeros(len(files), dtype = numpy.ndarray)
    resultsArr = numpy.zeros(len(files), dtype = numpy.ndarray)
    k = numpy.zeros(len(files), dtype = numpy.ndarray)
    fnames = numpy.zeros(len(files), dtype = numpy.chararray)
    i = 0
    if all:
        dateTime, temp, results, x05, x95 = get_data_from_stats_file('all_stations.csv', span, window, timeinterv, ppath, type, all = all)
    else:
        for fname in dirList:
            print "Reading file %s" % fname
            if os.path.isdir(ppath + "/" + fname):
                continue

            dateTime, temp, results = get_data_from_stats_file(fname, span, window, timeinterv, ppath, type, all = all)

            dateTimeArr[i] = numpy.append(dateTimeArr[i], dateTime)
            resultsArr[i] = numpy.append(resultsArr[i], results)
            tempArr[i] = numpy.append(tempArr[i], temp)
            k[i] = numpy.append(k[i], i)
            fnames[i] = fname
            i += 1
        # end for
    if all:
        return [dateTime, temp, results, k, fnames, x05, x95]
    return [dateTimeArr, tempArr, resultsArr, k, fnames]



def plot_upwelling_multiple_locations():



    file21 = '9678892_Stn_21_03-11-11.csv'
    file32 = '1020953_Stn_32_04-11-11.csv'
    file1 = '9678895_Stn_01_03-11-11.csv'
    dateTime1, temp1, results1 = get_data_from_file(file21, window_half_day, windows[1], rpath = path)
    dateTime2, temp2, results2 = get_data_from_file(file32, window_half_day, windows[1], rpath = path)
    dateTime3, temp3, results3 = get_data_from_file(file1, window_half_day, windows[1], rpath = path)

    '''
    results = [results1, results2, results3]
    dateTime = [dateTime1, dateTime2, dateTime3]
    temp = [temp1, temp2, temp3]
    k = [21, 32, 1]
    display_upwelling(dateTime, temp, results, k)
    '''
    file21 = '9678892_Stn_21_03-11-11.csv'
    file17 = '2393004_Stn_17_02-11-11.csv'
    file31 = '2395421_Stn_31_04-11-11.csv'
    file44 = '9674468_Stn_44_13-12-11.csv'
    dateTime1, temp1, results1 = get_data_from_file(file21, window_half_day, windows[1])
    dateTime2, temp2, results2 = get_data_from_file(file17, window_half_day, windows[1])
    dateTime3, temp3, results3 = get_data_from_file(file31, window_half_day, windows[1])
    dateTime4, temp4, results4 = get_data_from_file(file44, window_half_day, windows[1])
    results = [results1, results2, results3, results4]
    dateTime = [dateTime1, dateTime2, dateTime3, dateTime4]
    temp = [temp1, temp2, temp3, temp4]
    k = [21, 17, 31, 44]
    display_data.display_upwelling(dateTime, temp, results, k)



if __name__ == '__main__':
    # select_data()
    # plot_upwelling_multiple_locations()
    path = "/home/bogdan/Documents/UofT/PhD/Data_Files/Motivation"
    path = "/home/bogdan/Documents/UofT/PhD/Data_Files/MOE-Apr-May_2012-Thermistor_chain/csv_processed"
    read_files_and_display(path)
    print "Done!"

