import numpy
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import date2num, num2date
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates
import time, os, datetime

years = matplotlib.dates.YearLocator()  # every year
months = matplotlib.dates.MonthLocator()  # every month
yearsFmt = matplotlib.dates.DateFormatter('%Y')
# every monday
mondays = matplotlib.dates.WeekdayLocator(MONDAY)

hour = matplotlib.dates.HourLocator(byhour = None, interval = 4, tz = None)


def display(dateTime, temp, label, k):
    fig = plt.figure(num = k, facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)
    ax.plot(dateTime, temp, linewidth = 0.6, color = 'r')
    # format the ticks
    formatter = matplotlib.dates.DateFormatter('%Y-%m')
    # formatter = matplotlib.dates.DateFormatter('`%y')
    # ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(formatter)
    # ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d'))
    ax.xaxis.set_minor_locator(mondays)

    # ax.xaxis.grid(True, 'major')
    ax.xaxis.grid(True, 'minor')
    ax.grid(True)
    title = ' Station %d' % k
    ylabel = ' temperature ($^\circ$C)'
    plt.ylabel(ylabel).set_fontsize(16)
    plt.title(title).set_fontsize(20)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()
    plt.show()


def display2(dateTime, temp, coeff, k):
    fig = plt.figure(num = k, facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)
    ax.plot(dateTime, temp, 'r', dateTime, coeff, 'b', linewidth = 0.6)
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
    title = ' Station %d' % k
    ylabel = ' Temperature ($^\circ$C)'
    plt.ylabel(ylabel).set_fontsize(16)
    plt.title(title).set_fontsize(20)
    plt.show()

def display_upwelling(dateTimes, temps, coeffs, k):
    fig = plt.figure(facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)
    i = 0
    legend = []
    ls = ['-', '--', ':', '-.', '-', '--', ':', '-.']
    for dateTime in dateTimes:
        temp = temps[i]
        coef = coeffs[i]
        ax.plot(dateTime, coef, linestyle = ls[i], linewidth = 1.6 + 0.2 * i)
        # ax.plot(dateTime, temp, linewidth = 0.6)
        lg = 'Station %d' % k[i]
        legend.append(lg)
        i += 1

    # format the ticks
    formatter = matplotlib.dates.DateFormatter('%Y-%m-%d')
    # formatter = matplotlib.dates.DateFormatter('`%y')
    # ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(formatter)
    # ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d'))
    ax.xaxis.set_minor_locator(hour)

    # ax.xaxis.grid(True, 'major')
    ax.xaxis.grid(True, 'minor')
    ax.grid(True)
    ylabel = ' Temperature ($^\circ$C)'
    plt.ylabel(ylabel).set_fontsize(16)
    title = ' Upwelling advancement'

    plt.title(title).set_fontsize(20)
    plt.legend(legend)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()
    plt.show()

def display_temperature(dateTimes, temps, coeffs, k, fnames = None):
    fig = plt.figure(facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)
    i = 0
    legend = []
    ls = ['-', '--', ':', '-.', '-', '--', ':', '-.']
    for dateTime in dateTimes:
        temp = temps[i]
        coef = coeffs[i]
        ax.plot(dateTime, coef, linestyle = ls[i], linewidth = 1.6 + 0.2 * i)
        # ax.plot(dateTime, temp, linewidth = 0.6)
        if fnames == None:
            lg = 'Sensor %s' % k[i][1]
        else:
            lg = 'Sensor %s' % fnames[i]
        legend.append(lg)
        i += 1

    # format the ticks
    formatter = matplotlib.dates.DateFormatter('%Y-%m-%d')
    # formatter = matplotlib.dates.DateFormatter('`%y')
    # ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(formatter)
    # ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d'))
    ax.xaxis.set_minor_locator(hour)

    # ax.xaxis.grid(True, 'major')
    ax.xaxis.grid(True, 'minor')
    ax.grid(True)
    ylabel = ' Temperature (deg C)'
    plt.ylabel(ylabel).set_fontsize(16)
    title = ' Temperature Profiles'

    plt.title(title)
    plt.legend(legend)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()
    plt.show()

def display_temperatures(dateTimes, temps, coeffs, k, fnames = None, revert = False, difflines = False, custom = None):
    fig = plt.figure(facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)
    i = 0
    legend = []
    ls = ['-', '--', ':', '-.', '-', '--', ':', '-.', '-', '--', ':', '-.']
    for dateTime in dateTimes:
        temp = temps[i]
        coef = coeffs[i]
        # ax.plot(dateTime[1:], coef[1:])
        if revert == True:
            reversed_temp = temp[::-1]
            reversed_coef = coef[::-1]
        else:
            reversed_temp = temp
            reversed_coef = coef
        if difflines:
            ax.plot(dateTime[1:], reversed_temp[1:], linestyle = ls[i], linewidth = 1.0 + 0.2 * i)
        else:
            ax.plot(dateTime[1:], reversed_temp[1:], linewidth = 0.8)
        if fnames == None:
            lg = 'Sensor %s' % k[i][1]
        else:
            fileName, fileExtension = os.path.splitext(fnames[i])
            lg = '%s' % fileName

        legend.append(lg)
        ax.set_xlim(xmax = dateTime[len(dateTime) - 1])

        i += 1

    # format the ticks
    formatter = matplotlib.dates.DateFormatter('%Y-%m-%d')
    # formatter = matplotlib.dates.DateFormatter('`%y')
    # ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(formatter)
    # ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d'))
    ax.xaxis.set_minor_locator(hour)
    # ax.xaxis.set_minor_locator(mondays)

    # ax.xaxis.grid(True, 'major')
    ax.xaxis.grid(True, 'minor')
    ax.grid(True)
    if custom == None:
        ylabel = ' Temp. ($^\circ$C)'
        title = ' Temperature Profiles'

    else:
        title = 'Data Profiles'
        ylabel = ' Sensor Data Values - Normalized'

    plt.ylabel(ylabel).set_fontsize(16)


    plt.title(title).set_fontsize(20)
    plt.legend(legend)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()
    plt.show()


def display_temperatures_subplot(dateTimes, temps, coeffs, k, fnames = None, revert = False, custom = None):
    fig = plt.figure(facecolor = 'w', edgecolor = 'k')
    format = 100 * len(dateTimes) + 10
    matplotlib.rcParams['legend.fancybox'] = True

    i = 0
    # ls = ['-', '--', ':', '-.', '-', '--', ':', '-.']
    ax = numpy.zeros(len(dateTimes), dtype = matplotlib.axes.Subplot)
    for dateTime in dateTimes:
        ax[i] = fig.add_subplot(format + i + 1)
        temp = temps[i]
        coef = coeffs[i]
        # ax.plot(dateTime[1:], coef[1:])
        if revert == True:
            reversed_temp = temp[::-1]
            reversed_coef = coef[::-1]
        else:
            reversed_temp = temp
            reversed_coef = coef

        if fnames == None:
            lg = 'Sensor %s' % k[i][1]
        else:
            fileName, fileExtension = os.path.splitext(fnames[i])
            lg = '%s' % fileName

        lplt = ax[i].plot(dateTime[1:], reversed_temp[1:], linewidth = 0.6, label = lg)

        # LEGEND
        # blue_proxy = plt.Rectangle((0, 0), 1, 1, fc = "b")
        # ax[i].legend([blue_proxy], ['cars'])
        ax[i].legend(shadow = True, fancybox = True)


        # X-AXIS -Time
        # format the ticks
        formatter = matplotlib.dates.DateFormatter('%Y-%m-%d')
        # formatter = matplotlib.dates.DateFormatter('`%y')

        ax[i].xaxis.set_major_formatter(formatter)
        # ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d'))
        ax[i].xaxis.set_minor_locator(mondays)

        # ax.xaxis.grid(True, 'major')
        ax[i].xaxis.grid(True, 'minor')
        ax[i].grid(True)
        if custom == None:
            ylabel = ' Temp. ($^\circ$C)'
            ax[i].set_ylabel(ylabel).set_fontsize(16)
            title = ' Temperature Profiles - %s' % lg
        else:
            title = ' %s Profiles' % custom[i]
            ax[i].set_ylabel(custom[i])

        ax[i].set_title(title).set_fontsize(18)
        ax[i].set_xlim(xmax = dateTime[len(dateTime) - 1])
        # ax[i].legend(lplt, title = lg, shadow = True, fancybox = True)
        i += 1

    # end for

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them


    fig.autofmt_xdate()
    plt.draw()
    plt.show()


def display_img_temperatures(dateTimes, temps, coeffs, k, tick, maxdepth, firstlog, maxtemp, revert = False):
    n = len(dateTimes[0])
    m = len(dateTimes)
    Temp = numpy.zeros((m, n - 1))

    i = 0
    for dateTime in dateTimes:
        j = 0
        # c = coeffs[i]
        c = temps[i]
        for t in c:
            # skip the first value because it is ZERO
            if j == 0:
                j += 1
                continue

            Temp[m - 1 - i, j] = t
            j += 1
            # print "%d , I=%d" % (j, i)
            if j > n - 2:
                break
        # end for

        # Loop for shorter series (sensor malfuction) that need interpolation
        # Conditions:
        #    1- the  first and timeseries must be good
        #    2 - The bad timeseries can not be last or first (actually is implied from 1.
        if j < n - 3 :
            prev = temps[i - 1]
            next = temps[i + 1]
            for jj in range(j, n - 1):
                # average the missing values
                Temp[m - 1 - i, jj] = (prev[jj] + next[jj]) / 2.0
                jj += 1
                # print "%d , I=%d" % (j, i)
            # end for
         # end  j < n - 3 :

        i += 1
        if i > m - 1 :
            break
    # end for dateTime in dateTimes:


    fig = plt.figure()
    ax = fig.add_subplot(111)
    y = numpy.linspace(0, maxdepth - firstlog, m)
    if revert == True:
        yrev = y[::-1]
    else:
        yrev = y

    X, Y = numpy.meshgrid(dateTimes[0][1:], yrev)

    # HERE = > interpolation, speedup, what is wrong at the ned is red

    im = ax.pcolormesh(X, Y, Temp)  # , cmap = 'gray', norm = LogNorm())

    cb = fig.colorbar(im)
    cb.set_clim(0, maxtemp)

    ylabel = ' Depth (m)'
    plt.ylabel(ylabel).set_fontsize(16)
    title = ' Temperature Profiles'
    ax.set_ylim(0, maxdepth)
    # reverse
    # ax.set_ylim(ax.get_ylim()[::-1])

    # THIS works only for the T-CHAIN April2012
    ax.set_yticks(tick[1])
    ax.set_yticklabels(tick[0])

    # format the ticks
    formatter = matplotlib.dates.DateFormatter('%Y-%m-%d')
    # formatter = matplotlib.dates.DateFormatter('`%y')
    # ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(formatter)
    # ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d'))
    ax.xaxis.set_minor_locator(hour)

    fig.autofmt_xdate()

    # draw the thermocline
    levels = [13]
    colors = ['k']
    linewidths = [1]
    ax.contour(X, Y, Temp, levels, colors = colors, linewidths = linewidths)
    plt.show()

def display_vertical_temperature_profiles(dateTimes, temps, coeffs, k, startdepth, profiles, revert = False, legendloc = 4):

    temp = numpy.zeros(len(dateTimes))
    depth = numpy.linspace(startdepth, len(dateTimes) + startdepth, len(dateTimes))
    fig = plt.figure(facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)

    legend = []
    ls = ['-', '--', ':', '-.', '-', '--', ':', '-.']

    lidx = 0
    for j in profiles :
        for i in range(0, len(dateTimes)):
            temp[i] = coeffs[i][j]
        if revert == True:
            reversed_temp = temp[::-1]
        else:
            reversed_temp = temp
        ax.plot(reversed_temp, depth, linestyle = ls[lidx], linewidth = 1.7)
        lidx += 1
        lg = '%s' % datetime.date.fromordinal(int(dateTimes[0][j]))
        legend.append(lg)

    ax.grid(True)

    xlabel = ' Temperature ($^\circ$C)'
    plt.xlabel(xlabel).set_fontsize(16)
    ylabel = ' Depth (m)'
    plt.ylabel(ylabel).set_fontsize(16)
    title = ' Temperature Profiles'
    # reverse

    ax.set_ylim(ax.get_ylim()[::-1])  # [::1] reverses the array


    plt.title(title).set_fontsize(20)
    # loc=4      position lower right
    #---------------------------------------------------------- upper right    1
    #---------------------------------------------------------- upper left    2
    #---------------------------------------------------------- lower left    3
    #---------------------------------------------------------- lower right    4
    #---------------------------------------------------------- right    5
    #------------------------------------------------------ --- center left    6
    #---------------------------------------------------------- center right    7
    #---------------------------------------------------------- lower center    8
    #---------------------------------------------------------- upper center    9
#-------------------------------------------------------------- center    10
    # prop={'size':14} font size  =14
    plt.legend(legend, loc = legendloc, prop = {'size':12})

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    # fig.autofmt_xdate()
    plt.show()