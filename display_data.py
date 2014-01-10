import numpy
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates
import time, os, datetime, math, sys

sys.path.insert(0, '/software/SAGEwork/Seiches')
import fft.filters as filters
import fft.fft_utils as fft_utils

years = matplotlib.dates.YearLocator()  # every year
months = matplotlib.dates.MonthLocator()  # every month
yearsFmt = matplotlib.dates.DateFormatter('%Y')
# every monday
mondays = matplotlib.dates.WeekdayLocator(MONDAY)

hour = matplotlib.dates.HourLocator(byhour = None, interval = 4, tz = None)


def display(dateTime, temp, label, k):
    fig = plt.figure(num = k, facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)
    ax.plot(dateTime, temp, linewidth = 1.6, color = 'r')
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
    plt.ylabel(ylabel).set_fontsize(20)
    plt.title(title).set_fontsize(22)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()
    plt.show()


def display2(dateTime, temp, coeff, k):
    fig = plt.figure(num = k, facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)
    ax.plot(dateTime, temp, 'r', dateTime, coeff, 'b', linewidth = 1.4)
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
    plt.ylabel(ylabel).set_fontsize(20)
    plt.title(title).set_fontsize(22)
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
        ax.plot(dateTime, coef, linestyle = ls[i], linewidth = 1.2 + 0.2 * i)
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
    plt.ylabel(ylabel).set_fontsize(20)
    title = ' Upwelling advancement'

    plt.title(title).set_fontsize(22)
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
        ax.plot(dateTime, coef, linestyle = ls[i], linewidth = 1.2 + 0.2 * i)
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
    plt.ylabel(ylabel).set_fontsize(20)
    title = ' Temperature Profiles'

    plt.title(title)
    plt.legend(legend)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()
    plt.show()

def display_temperatures_and_peaks(dateTimes, temps, maxpeaks, minpeaks, k, fnames = None, revert = False, difflines = False, \
                                      custom = None, maxdepth = None, tick = None, firstlog = None, fontsize = 20, ylim = None, fill = False, show = True):
    '''
    '''

    ax = display_temperatures(dateTimes, temps, k, fnames = fnames, revert = revert, difflines = difflines, custom = custom, \
                          maxdepth = maxdepth, tick = tick, firstlog = firstlog, fontsize = fontsize, ylim = ylim, fill = fill, show = False)

    for i in range(len(maxpeaks)):
        xm = [p[0] for p in maxpeaks[i]]
        ym = [p[1] for p in maxpeaks[i]]
        xn = [p[0] for p in minpeaks[i]]
        yn = [p[1] for p in minpeaks[i]]

        # plot local min and max
        ax.plot(xm, ym, 'ro')
        ax.plot(xn, yn, 'bo')

    if show:
        plt.show()
# end display_temperatures_peaks

def display_temperatures(dateTimes, temps, k, fnames = None, revert = False, difflines = False, custom = None, \
                          maxdepth = None, tick = None, firstlog = None, fontsize = 20, ylim = None, fill = False, \
                          show = True, datetype = 'date'):
    fig = plt.figure(facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)
    i = 0
    legend = []
    title = None


    ls = ['-', '--', ':', '-.', '-', '--', ':', '-.', '-', '--', ':', '-.', '-', '--', ':', '-.']
    colour_list = ['g', 'r', 'y', 'b', 'c', 'm', 'k', (0.976, 0.333, 0.518), (0.643, 0.416, 0.994), (0.863, 0.267, 0.447), \
                                                (0.576, 0.533, 0.318), (0.343, 0.516, 0.394), (0.563, 0.567, 0.347),
                                                (0.176, 0.733, 0.118), (0.943, 0.616, 0.694), (0.263, 0.967, 0.247)]
    for dT in dateTimes:
        temp = temps[i]
        if revert == True:
            reversed_temp = temp[::-1]
        else:
            reversed_temp = temp

        if datetype == 'dayofyear':
            dateTime = fft_utils.timestamp2doy(dT[1:])
        else:
            dateTime = dT[1:]
        if difflines:
            ax.plot(dateTime, reversed_temp[1:], linestyle = ls[i], linewidth = 1.6 + 0.1 * i, color = colour_list[i])
        else:
            try:
                if len(dateTime) > 0:
                    ax.plot(dateTime, reversed_temp[1:], linewidth = 1.8)
            except Exception as e:
                print "Error %s" % e
                continue

        if fnames == None:
            lg = 'Sensor %s' % k[i][1]
        else:
            if fnames[i].rfind('.') == -1:
                lg = "%s" % (fnames[i])
            else:
                fileName, fileExtension = os.path.splitext(fnames[i])
                if fileName[0:3] == "zz_":
                    fileName = fileName[3:]
                lg = '%s' % fileName

        legend.append(lg)
        ax.set_xlim(xmax = dateTime[len(dateTime) - 1])

        i += 1
    # end for
    if fill == True and len(dateTimes) == 2 and len(dateTimes[1]) == len(dateTimes[0]):
        sd = 0.5
        ax.fill_between(dateTimes[0], temps[1], temps[0], where = temps[1] <= temps[0], facecolor = [sd, sd, sd], interpolate = True)

    # format the ticks
    if datetype == 'date':
        formatter = matplotlib.dates.DateFormatter('%Y-%m-%d')
        # formatter = matplotlib.dates.DateFormatter('`%y')
        # ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(formatter)
        # ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d'))

        # ax.xaxis.set_minor_locator(hour)
        fig.autofmt_xdate()
    else:
        plt.xticks(fontsize = fontsize)
        plt.xlabel("Julian Day").set_fontsize(fontsize)

    ax.xaxis.set_minor_locator(mondays)

    # ax.xaxis.grid(True, 'major')
    ax.xaxis.grid(True, 'minor')
    ax.grid(True)

    if tick != None:
       ax.set_yticks(tick[1])
       ax.set_yticklabels(tick[0])

    if custom == None:
        ylabel = ' Temp. ($^\circ$C)'
        title = ' Temperature Profiles'

    else:
        # title = ' Profiles: %s' % custom
        title = ' %s' % custom
        ylabel = ' Temp. ($^\circ$C)'

    if ylim != None:
         ax.set_ylim(ylim[0], ylim[1])


    plt.ylabel(ylabel).set_fontsize(fontsize)

    labels = ax.get_xticklabels()
    plt.setp(labels, rotation = 0, fontsize = fontsize - 2)


    plt.title(title).set_fontsize(fontsize + 2)
    plt.legend(legend)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    if show:
        plt.show()
    return ax


def display_temperatures_subplot(dateTimes, temps, coeffs, k, fnames = None, revert = False, custom = None, \
                                 maxdepth = None, tick = None, firstlog = None, yday = None, delay = None):
    fig = plt.figure(facecolor = 'w', edgecolor = 'k')
    format = 100 * len(dateTimes) + 10
    matplotlib.rcParams['legend.fancybox'] = True

    # if delay != None and yday == None:
    #    raise BasicException("delay needs yday=True")



    # ls = ['-', '--', ':', '-.', '-', '--', ':', '-.']

    if yday != None and delay != None:
        minx = 10000000.
        maxx = 0.

        # find maxx and minX of the X axis
        for k in range(0, len(dateTimes)):
            d = dateTimes[k]
            dmax = num2date(d[len(d) - 1])
            maxx = max(maxx, (dmax.timetuple().tm_yday + dmax.timetuple().tm_hour / 24. + dmax.timetuple().tm_min / (24. * 60) + dmax.timetuple().tm_sec / (24. * 3600)))

            dmin = num2date(d[1])
            minx = min(minx, (dmin.timetuple().tm_yday + dmin.timetuple().tm_hour / 24. + dmin.timetuple().tm_min / (24. * 60) + dmin.timetuple().tm_sec / (24. * 3600) - delay[k]))


    i = 0
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
            lg = "Sensor %s" % k[i][1]
        else:
            if fnames[i].rfind('.') == -1:
                lg = "%s" % (fnames[i])
            else:
                fileName, fileExtension = os.path.splitext(fnames[i])
                lg = '%s' % fileName


        if yday == None:
            lplt = ax[i].plot(dateTime[1:], reversed_temp[1:], linewidth = 1.4, label = lg)
        else:
            dofy = numpy.zeros(len(dateTime))
            # dates = [datetime.fromordinal(d) for d in dataTime]
            # dofy = [d.tordinal() - datetime.date(d.year, 1, 1).toordinal() + 1 for d in dates]
            for j in range(1, len(dateTime)) :
                d = num2date(dateTime[j])

                dely = delay[i] if delay != None else 0.0

                dofy[j] = d.timetuple().tm_yday + d.timetuple().tm_hour / 24. + d.timetuple().tm_min / (24. * 60) + d.timetuple().tm_sec / (24. * 3600) - dely

            lplt = ax[i].plot(dofy[1:], reversed_temp[1:], linewidth = 1.4, label = lg)

        # LEGEND
        # blue_proxy = plt.Rectangle((0, 0), 1, 1, fc = "b")
        # ax[i].legend([blue_proxy], ['cars'])
        ax[i].legend(shadow = True, fancybox = True)


        # X-AXIS -Time
        # format the ticks
        if yday == None:
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
            ax[i].set_ylabel(ylabel).set_fontsize(20)
            title = ' Temperature Profiles - %s' % lg
        else:
            title = ' Profile: %s' % custom[i]
            ax[i].set_ylabel(custom[i])

        ax[i].set_title(title).set_fontsize(22)
        if yday == None:
            ax[i].set_xlim(xmax = dateTime[len(dateTime) - 1])
            ax[i].set_xlabel("Time").set_fontsize(20)
        else:
            if delay != None:
                ax[i].set_xlim(xmin = minx, xmax = maxx)
                # ax[i].set_xlim(xmin = 150 , xmax = 400)

            ax[i].set_xlabel("day of the year").set_fontsize(20)

        if maxdepth != None:
            if firstlog != None:
                mindepth = firstlog
            else:
                mindepth = 0
            ax[i].set_ylim(mindepth, maxdepth[i])

        # ax[i].legend(lplt, title = lg, shadow = True, fancybox = True)
        if tick != None:
           ax[i].set_yticks(tick[i][1])
           ax[i].set_yticklabels(tick[i][0])

        # set labels visibility
        plt.setp(ax[i].get_xticklabels(), visible = True)

        i += 1

    # end for

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()

    # new seting to make room for labels
    plt.tight_layout()

    plt.draw()
    plt.show()


def display_depths_subplot(dateTimes, depths, maxdepth, fnames = None, yday = None, revert = True, tick = None, custom = None, firstlog = None):
    fig = plt.figure(facecolor = 'w', edgecolor = 'k')
    format = 100 * len(dateTimes) + 10
    matplotlib.rcParams['legend.fancybox'] = True


    if yday != None:
        minx = 10000000.
        maxx = 0.

        # find maxx and minX of the X axis
        for k in range(0, len(dateTimes)):
            d = dateTimes[k]
            dmax = num2date(d[len(d) - 1])
            maxx = max(maxx, (dmax.timetuple().tm_yday + dmax.timetuple().tm_hour / 24. + dmax.timetuple().tm_min / (24. * 60) + dmax.timetuple().tm_sec / (24. * 3600)))

            dmin = num2date(d[0])
            minx = min(minx, (dmin.timetuple().tm_yday + dmin.timetuple().tm_hour / 24. + dmin.timetuple().tm_min / (24. * 60) + dmin.timetuple().tm_sec / (24. * 3600)))


    i = 0
    # ls = ['-', '--', ':', '-.', '-', '--', ':', '-.']
    ax = numpy.zeros(len(dateTimes), dtype = matplotlib.axes.Subplot)
    for dateTime in dateTimes:
        ax[i] = fig.add_subplot(format + i + 1)
        depth = depths[i]
        # ax.plot(dateTime[1:], coef[1:])
        if (revert == True and tick == None) or (revert == None and tick != None):
            raise IOError('Both revert and tick must be defined')

        if revert == True:
            reversed_depth = maxdepth[i] - depth
        else:
            reversed_depth = depth

        if fnames == None:
            lg = "Sensor %s" % k[i][1]
        else:
            if fnames[i].rfind('.') == -1:
                lg = "%s" % (fnames[i])
            else:
                fileName, fileExtension = os.path.splitext(fnames[i])
                lg = '%s' % fileName

        if yday == None:
            lplt = ax[i].plot(dateTime[1:], reversed_depth[1:], linewidth = 1.4, label = lg)
        else:
            dofy = numpy.zeros(len(dateTime))
            # dates = [datetime.fromordinal(d) for d in dataTime]
            # dofy = [d.tordinal() - datetime.date(d.year, 1, 1).toordinal() + 1 for d in dates]
            for j in range(0, len(dateTime)) :
                d = num2date(dateTime[j])
                dofy[j] = d.timetuple().tm_yday + d.timetuple().tm_hour / 24. + d.timetuple().tm_min / (24. * 60) + d.timetuple().tm_sec / (24. * 3600)

            lplt = ax[i].plot(dofy[1:], reversed_depth[1:], linewidth = 1.4, label = lg)




        # LEGEND
        # blue_proxy = plt.Rectangle((0, 0), 1, 1, fc = "b")
        # ax[i].legend([blue_proxy], ['cars'])
        ax[i].legend(shadow = True, fancybox = True)


        # X-AXIS -Time
        # format the ticks
        if yday == None:
            formatter = matplotlib.dates.DateFormatter('%Y-%m-%d')
            # formatter = matplotlib.dates.DateFormatter('`%y')

            ax[i].xaxis.set_major_formatter(formatter)
            # ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d'))
            ax[i].xaxis.set_minor_locator(mondays)


        # ax.xaxis.grid(True, 'major')
        ax[i].xaxis.grid(True, 'minor')
        ax[i].grid(True)
        if custom == None:
            ylabel = ' Depth. (m)'
            ax[i].set_ylabel(ylabel).set_fontsize(20)
            title = '  Profiles - %s' % lg
        else:
            title = ' Profile: %s' % custom[i]
            ax[i].set_ylabel(custom[i])

        ax[i].set_title(title).set_fontsize(22)
        if yday == None:
            ax[i].set_xlim(xmax = dateTime[len(dateTime) - 1])
            ax[i].set_xlabel("Time").set_fontsize(20)
        else:
            ax[i].set_xlim(xmin = minx, xmax = maxx)
            ax[i].set_xlabel("day of the year").set_fontsize(20)

        if maxdepth != None:
            if firstlog != None:
                mindepth = firstlog
            else:
                mindepth = 0
            ax[i].set_ylim(mindepth, maxdepth[i])

        # ax[i].legend(lplt, title = lg, shadow = True, fancybox = True)
        if tick != None:
           ax[i].set_yticks(tick[i][1])
           ax[i].set_yticklabels(tick[i][0])


        i += 1

    # end for

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them


    fig.autofmt_xdate()
    plt.draw()
    plt.show()


def display_img_temperatures(dateTimes, temps, coeffs, k, tick, maxdepth, firstlog, maxtemp, revert = False, \
                             fontsize = 20, datetype = 'date'):
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

    if datetype == 'dayofyear':
        dateTime = fft_utils.timestamp2doy(dateTimes[0][1:])
    else:
        dateTime = dateTimes[0][1:]
    X, Y = numpy.meshgrid(dateTime, yrev)

    # HERE = > interpolation, speedup, what is wrong at the ned is red

    im = ax.pcolormesh(X, Y, Temp)  # , cmap = 'gray', norm = LogNorm())

    cb = fig.colorbar(im)
    cb.set_clim(0, maxtemp)
    labels = cb.ax.get_yticklabels()
    plt.setp(labels, rotation = 0, fontsize = fontsize)

    ylabel = ' Depth (m)'
    plt.ylabel(ylabel).set_fontsize(fontsize + 2)
    title = ' Temperature Profiles'
    ax.set_ylim(0, maxdepth)
    # reverse
    # ax.set_ylim(ax.get_ylim()[::-1])

    # THIS works only for the T-CHAIN April2012
    ax.set_yticks(tick[1])
    ax.set_yticklabels(tick[0])
    labels = ax.get_yticklabels()
    plt.setp(labels, rotation = 0, fontsize = fontsize)

    # format the ticks
    if datetype == "date":
        formatter = matplotlib.dates.DateFormatter('%Y-%m-%d')
        # formatter = matplotlib.dates.DateFormatter('`%y')
        # ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(formatter)
        # ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d'))
        plt.setp(labels, rotation = 0, fontsize = fontsize)
        fig.autofmt_xdate()
    else:
        plt.xticks(fontsize = fontsize)
        plt.xlabel("Julian Day").set_fontsize(fontsize)

    ax.xaxis.set_minor_locator(hour)

    labels = ax.get_xticklabels()

    # draw the thermocline
    levels = [13]
    colors = ['k']
    linewidths = [1]
    ax.contour(X, Y, Temp, levels, colors = colors, linewidths = linewidths, fontsize = fontsize)
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
        ax.plot(reversed_temp, depth, linestyle = ls[lidx], linewidth = 1.6)
        lidx += 1
        lg = '%s' % datetime.date.fromordinal(int(dateTimes[0][j]))
        legend.append(lg)

    ax.grid(True)

    xlabel = ' Temperature ($^\circ$C)'
    plt.xlabel(xlabel).set_fontsize(20)
    ylabel = ' Depth (m)'
    plt.ylabel(ylabel).set_fontsize(20)
    title = ' Temperature Profiles'
    # reverse

    ax.set_ylim(ax.get_ylim()[::-1])  # [::1] reverses the array


    plt.title(title).set_fontsize(22)
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
