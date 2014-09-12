import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
from matplotlib.dates import seconds
from matplotlib.dates import date2num, num2date
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates
import time, os
import csv
import numpy
from utils import smooth
import tor_harb_windrose

weather_path = '/home/bogdan/Documents/UofT/PhD/Research-docs/Data_Files/Hobo_Files_Bogdan'
path_in = '/home/bogdan/Documents/UofT/PhD/Research-docs/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2011/csv_processed'
path_out = '/home/bogdan/Documents/UofT/PhD/Research-docs/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2011/csv_interpolated'

weather_path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2012/MOE deployment 18-07-2012/Data/ClimateData'
path_in = '/home/bogdan/Documents/UofT/PhD/Data_Files/2012/MOE deployment 18-07-2012/Data/ClimateData/in'
path_out = '/home/bogdan/Documents/UofT/PhD/Data_Files/2012/MOE deployment 18-07-2012/Data/ClimateData/out'

years = matplotlib.dates.YearLocator()  # every year
months = matplotlib.dates.MonthLocator()  # every month
yearsFmt = matplotlib.dates.DateFormatter('%Y')
# every monday
mondays = matplotlib.dates.WeekdayLocator(MONDAY)


def display(title, label, x, y, colour, legend = None, linewidth = 0.6):

    n = len(x)
    fig = plt.figure(facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)
    for i in range(0, n):
        ax.plot(x[i], y[i], linewidth = 0.6, color = colour[i])
    # format the ticks
    formatter = matplotlib.dates.DateFormatter('%Y-%m-%d')
    # formatter = matplotlib.dates.DateFormatter('`%y')
    # ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(formatter)
    # ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d'))
    ax.xaxis.set_minor_locator(mondays)

    # ax.xaxis.grid(True, 'major')
    ax.xaxis.grid(True, 'minor')
    ax.grid(True)
    title = title
    ylabel = label
    plt.ylabel(ylabel)
    plt.title(title)
    if legend != None:
        plt.legend(legend);

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()

    plt.draw()
    return plt

def display_twinx(title, label1, label2, x1, y1, x2, y2, colour1, colour2, \
                  legend = None, linewidth1 = 1.0, linewidth2 = .0):

    n = len(x1)
    fig = plt.figure(facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)
    for i in range(0, n):
        ax.plot(x1[i], y1[i], linewidth = linewidth1[i], color = colour1[i])
    # format the ticks
    formatter = matplotlib.dates.DateFormatter('%Y-%m-%d')
    # formatter = matplotlib.dates.DateFormatter('`%y')
    # ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(formatter)
    # ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d'))
    ax.xaxis.set_minor_locator(mondays)

    # ax.xaxis.grid(True, 'major')
    ax.xaxis.grid(True, 'minor')
    ax.grid(True)
    title = title

    # plt.ylabel(ylabel)

    ax.set_ylabel(label1).set_fontsize(16)
    plt.title(title).set_fontsize(18)

    ax2 = ax.twinx()
    n = len(x2)
    for i in range(0, n):
        ax2.plot(x2[i], y2[i], colour2[i], linewidth = linewidth2[i])

    ax2.set_ylabel(label2, color = colour2[i]).set_fontsize(16)
    for tl in ax2.get_yticklabels():
        tl.set_color(colour2[i])

    ax2.xaxis.set_major_formatter(formatter)
    ax2.xaxis.set_minor_locator(mondays)
    ax2.xaxis.grid(True, 'minor')
    ax2.grid(True)

    if legend != None:
        plt.legend(legend);


    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()

    plt.draw()
    plt.show()

    return plt



def display2(dateTime, temp, time, data, title, label, k):
    fig = plt.figure(num = k, facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)
    ax.plot(dateTime, temp, 'r', time, data, 'b', linewidth = 0.6)

    # format the ticks
    formatter = matplotlib.dates.DateFormatter('%Y-%m-%d')
    # formatter = matplotlib.dates.DateFormatter('`%y')
    # ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(formatter)
    # ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d'))
    ax.xaxis.set_minor_locator(mondays)

    # ax.xaxis.grid(True, 'major')
    ax.xaxis.grid(True, 'minor')
    ax.grid(True)
    title = title + ' %d' % k
    ylabel = label
    plt.ylabel(ylabel)
    plt.title(title)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()
    plt.show()

def select_dates(fbegin, fend, dateTime, temp, windDir = None, windSpd = None, press = None):
    '''
        Select only records matching time from "begin" to "end"
        string dates are also converted

    '''
    idx = 0;
    stemp = []
    sdateTime = []
    swindDir = []
    swindSpd = []
    spress = []
    lastpress = 0
    for row in temp:
        fdate = float(dateTime[idx])
        try:
            fpress = float(press[idx])
            lastpress = fpress
        except:
            fpress = lastpress
        try:
            fwinddir = float(windDir[idx])
        except:
            fwinddir = 0
        try:
            fwindspd = float(windSpd[idx])
        except:
            fwindspd = 0

        if fdate >= fbegin and fdate <= fend:
            try:
                frow = float(row)
                stemp.append(frow)
                sdateTime.append(fdate)
                if windDir != 0:
                    swindDir.append(fwinddir)
                    swindSpd.append(fwindspd)
                    spress.append(fpress)
            except:
               pass
        idx += 1

    if windDir == None:
        return [stemp, sdateTime]
    else:
        return [stemp, sdateTime, swindDir, swindSpd, spress]


def select_dates_string(fbegin, fend, dateTime, temp, windDir = None, windSpd = None, press = None):
    '''
        Select only records matching time from "begin" to "end"
        string dates are also converted
    '''
    # convert date to float
    idx = 0
    prev = 0
    fdate = []
    prevtxt = ''
    for row in temp:
        dt = datetime.strptime(dateTime[idx], "%Y-%m-%d %H:%M")
        dn = date2num(dt)
        if prev > dn:
            print "Next value lower!"
        prev = dn
        idx += 1
        fdate.append(dn)

    [stemp, sdateTime, swindDir, swindSpd, spress] = select_dates(fbegin, fend, fdate, temp, windDir, windSpd, press)

    if windDir == None:
        return [stemp, sdateTime]
    else :
        return [stemp, sdateTime, swindDir, swindSpd, spress]


# export to date file
def write_datefile(writer, temp, dateTime, windDir = None, windSpd = None, press = None):
    idx = 0
    if windDir != None:
        writer.writerow(['#Date-Time', 'Temperature', 'Wind Dir', 'Wind Spd', ' Pressure'])
    else:
        writer.writerow(['#Date-Time', 'Temperature'])

    for row in temp:
        towritestr = 'dateTime[idx], row'
        if windDir != None:
            towritestr += ' , windDir[idx], windSpd[idx], press[idx]'
        towrite = ' writer.writerow([' + towritestr + '])'
        # writer.writerow([dateTime[idx], row ])
        eval(towrite)
        idx += 1


def read_processed_file(reader):
    rownum = 0
    temp = []
    dateTime = []
    printHeaderVal = False

    for row in reader:
        try:
            temp.append(row[2])
            dateTime.append(row[1])
        except:
            pass
    return [temp, dateTime]

def read_stringdatefile(reader):
    rownum = 0
    temp = []
    dateTime = []
    windDir = []
    windSpd = []
    press = []
    printHeaderVal = False

    for row in reader:
        # skip comment lines
        if len(row) == 0 or row[0][:1] == '#' or row[0][:1] == '@':
            continue

        # Save header row.
        if rownum == 0:
            header = row
        else:
            if printHeaderVal == True:
                colnum = 0

                for col in row:
                    print '%-8s: %s' % (header[colnum], col)
                    colnum += 1
            else:
                colnum = 0
                for col in row:
                    # print "colnum: %d, rownum: %d" % (colnum, rownum)
                    if len(header[colnum]) > 4 and header[colnum][:6] == "Temp (":
                        try:
                            fcol = float(col)
                        except:
                            pass
                        temp.append(fcol)

                    if header[colnum] == "Date/Time":
                        dateTime.append(str(col))

                    if len(header[colnum]) > 10 and header[colnum][:10] == "Wind Dir (":
                        windDir.append(str(col))
                    if len(header[colnum]) > 10 and header[colnum][:10] == "Wind Spd (":
                        windSpd.append(str(col))
                    if len(header[colnum]) > 10 and header[colnum][:11] == "Stn Press (":
                        press.append(str(col))

                    colnum += 1

        rownum += 1

    return [temp, dateTime, windDir, windSpd, press]


def find_upwelling(x, y, deg):
    '''
    data - an array of x-y pairs of timeseries
    '''
    import scipy.ndimage.measurements as mm
    from scipy.interpolate import UnivariateSpline
    # smooth
    s = UnivariateSpline(x, y, s = deg)
    yhat = s(x)
    # find the min
    xm = mm.minimum_position(yhat)
    # derivatives = s.derivatives(xm[0])
    return xm[0]

def read_interp_temp_files(dt_begin, dt_end, data, legend):
    dirList = os.listdir(path_in)
    idx = 0
    upw_time = {}

    for fname in dirList:
        filename = path_in + '/' + fname
        if os.path.isdir(filename) == True:
            continue

        ifile = open(filename, 'rb')
        reader = csv.reader(ifile, delimiter = ',', quotechar = '"')
        [temp, dateTime] = read_processed_file(reader)
        print "Station: %s" % fname ,

        interval = timedelta(float(dateTime[200]) - float(dateTime[199]))
        intv_sec = interval.total_seconds()
        print "Interval %d [s]" % intv_sec

        [stemp, sdateTime] = select_dates(dt_begin, dt_end, dateTime, temp)

        x = [sdateTime]
        y = [stemp]
        c = ['r', 'b', 'k', 'y', 'g', 'p']
        l = ['watertemp']

        for j in range(0, len(legend)):
            l.append(legend[j])

        for i in range(0, len(data) - 1, 2):
            x.append(data[i])
            y.append(data[i + 1])

        plt = display(fname, "Temperature deg C", x, y, c, l)
        # [itemp, iDataTime] = intepolateData(date_in, date_out, stemp, sdataTime)
        ofile = open(path_out + '/' + fname, "wb")
        writer = csv.writer(ofile, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)
        write_datefile(writer, stemp, sdateTime)
        ofile.close()
        ifile.close()
        idx += 1

        # correlate with wind /temp from the weather file
        #  1. Find the minimum of the graph and where its derivative is zero => upwelling point ->
        #  2. Get the time (position in the array) for a few stations use only the first 5000 elemenst

        # xm = find_upwelling(sdateTime[:5000], stemp[:5000], 7000)

        xm = find_upwelling(sdateTime, stemp, 7000)

        name = fname[8:14]
        upw_time[name] = xm
        if name == 'Stn_53':
            upw_idx = xm;
            dt = num2date(sdateTime[xm])
            print "\n Upwelling at:" + dt.strftime("%Y-%m-%d %H:%M:%S")
            print " "

    # end for
    # ensure that window does not close
    plt.show()

    #  3. Calculate the speed of the upwelling wave
    speed = {}
    for name in upw_time:
        if name == 'Stn_53':
            time_org = upw_time[name]

    print "----------------------"
    print " Upwelling delay [s] [days] [hours]"

    for name in upw_time:
        delta = (upw_time[name] - time_org) * intv_sec
        dt = num2date(sdateTime[upw_time[name]])
        days = seconds(delta)
        hours = delta / 3600 - int(days) * 24

        print "%s: date:%s delta:%f [s] ( days:%d, hours:%.2f )" % (name, dt.strftime("%Y-%m-%d %H:%M:%S"), delta, days, hours)

    return [intv_sec, upw_idx]



def interpolateData(interval, temp, dateTime, windDir = 0, windSpd = 0, press = 0):
    '''
    Interpolate the data from hourly to "interval"
    '''
    ratio = 60 / interval
    atmPressInterp = windSpeedInterp = windDirInterp = 0
    # interpolated pressure values
    atmTempInterp = numpy.interp(range(0, ratio * len(temp)), range(0, ratio * len(temp), ratio), temp)
    dateTimeInterp = numpy.interp(range(0, ratio * len(temp)), range(0, ratio * len(temp), ratio), dateTime)
    if windDir != 0:
        windDirInterp = numpy.interp(range(0, ratio * len(temp)), range(0, ratio * len(temp), ratio), windDir)
    if windSpd != 0:
        windSpeedInterp = numpy.interp(range(0, ratio * len(temp)), range(0, ratio * len(temp), ratio), windSpd)
    if press != 0:
        atmPressInterp = numpy.interp(range(0, ratio * len(temp)), range(0, ratio * len(temp), ratio), press)

    return [atmTempInterp, dateTimeInterp, windDirInterp, windSpeedInterp, atmPressInterp]





def main ():

    error = 10 ** (-5)

    # upwelling
    # date_start = "2011/08/18 00:00:00"
    # date_end = "2011/09/03 00:00:00"
    date_start = '2012/07/19 00:00:00'
    date_end = '2012/10/24 00:00:00'
    # date_end = "2011/11/03 00:00:00"
    # 1) read the weather file

    # no upwelling
    # date_start = "2011/09/03 00:00:00"
    # date_end = "2011/09/12 00:00:00"


    dt_begin = date2num(datetime.strptime(date_start, "%Y/%m/%d %H:%M:%S"))
    dt_end = date2num(datetime.strptime(date_end, "%Y/%m/%d %H:%M:%S"))

    # wfile = open(weather_path + '/eng-hourly-aug_nov_2011.csv', 'rb')
    wfile = open(weather_path + '/all/eng-hourly-07012012-11302012-all.csv', 'rb')

    wreader = csv.reader(wfile, delimiter = ',', quotechar = '"')
    [temp, dateTime, windDir, windSpd, press] = read_stringdatefile(wreader)
    # 2) select the dates
    [wtemp, wdateTime, windDir, windSpd, press] = select_dates_string(dt_begin, dt_end, dateTime, temp, windDir, windSpd, press)
    display("temperature", ' temperature ($^\circ$C)', [wdateTime], [wtemp], ['r'])
    display("wind direction & speed", ' wind dir deg*10/wind speed Km/h', [wdateTime, wdateTime], [windDir, windSpd], ['r', 'b'])
    # display("wind speed", ' wind speed km/h', [wdateTime], [windSpd], ['r'])
    plt = display("pressure", ' air pressure  kPa', [wdateTime], [press], ['r'])
    # call show() so that the window does not disappear.
    plt.show()
    # 3) interplate every 10 minutes
    # dirList = os.listdir(path_in)
    idx = 0
    upw_time = {}

    [iwtemp, iwdateTime, iwindDir, iwindSpd, iPress] = interpolateData(10, wtemp, wdateTime, windDir, windSpd, press)
    owfile = open(path_in + '/jul_nov_2012_interp.csv', "wb")

    writer = csv.writer(owfile, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)
    write_datefile(writer, iwtemp, iwdateTime, iwindDir, iwindSpd, iPress)
    display("interp", "Temperature ($^\circ$C)", [iwdateTime], [iwtemp], ['r'])
    plt.show()
    # 4) interpolate all the files in a loop and add the temp/pressure/wind etc from the weather file
    legend = ['airtemp', 'windDir', 'windSpd']
    # read_interp_temp_files(date_start, date_end, [iwdateTime, iwtemp, iwdateTime, iwindDir, iwdateTime, iwindSpd], legend)

    # same as before but smoothed
    windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']

    window_6hour = 6
    window_12hour = 12
    window_day = 24
    results_temp = utils.smooth.smoothfit(iwdateTime, iwtemp, window_day, windows[1])
    results_winddir = utils.smooth.smoothfit(iwdateTime, iwindDir, window_day, windows[1])
    results_windspd = utils.smooth.smoothfit(iwdateTime, iwindSpd, window_day, windows[1])

    print iwtemp
    print results_winddir['smoothed']
    print results_windspd['smoothed']

    # uncomment the followinf to estimate upwelling in a crude raw manner ( sould be cross spectra)
    [intv_sec, upw_idx] = read_interp_temp_files(dt_begin, dt_end, [iwdateTime, results_temp['smoothed'], iwdateTime, results_winddir['smoothed'], iwdateTime, results_windspd['smoothed']], legend)

    # 6) find the wind patterns that cause upwelling
    # 1. select 4-5 days before upwelling
    # 2. select 4-5 days before a stable temperature
    # 3. Make the difference to figure out the patterns that produce upwelling in Tor Harbour.


    # Remove the following to get the desired date represented in the wind rose
    diff_days = 8  # from last in the serias to the estimated uwelling
    upw_idx = len(iwdateTime) - (diff_days * 24 * 3600 / intv_sec)  # select the last idx to estimate wind before that date of no upwelling

    winddir = numpy.multiply(results_winddir['smoothed'], 10)
    days_before_start = 6  # number of days  to be counted before the upwelling start
    days_before_end = 0  # number of days  to be counted before the upwelling start
    intv_idx_st = days_before_start * 24 * 3600 / intv_sec
    intv_idx_end = days_before_end * 24 * 3600 / intv_sec
    beg_intv = int(upw_idx - intv_idx_st)
    end_intv = int(upw_idx - intv_idx_end)

    wd = numpy.zeros((end_intv - beg_intv), numpy.float)
    ws = numpy.zeros((end_intv - beg_intv), numpy.float)

    idx = 0
    for i in range(beg_intv, end_intv):
        d = results_winddir['smoothed'][i] * 10
        wd.put(idx, d)
        s = results_windspd['smoothed'][i]
        ws.put(idx, s)
        idx += 1
        print "%d) direction: %f,  speed: %f " % (idx, d, s)

    tor_harb_windrose.draw_windrose(wd, ws, 'bar')
    tor_harb_windrose.draw_windrose(wd, ws, 'contour')
    plt = tor_harb_windrose.draw_windrose(wd, ws, 'hist')
    plt.show()



if __name__ == '__main__':
    main()
