import numpy
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates as dates
import time, os, datetime, math, sys
import matplotlib.gridspec as gridspec

sys.path.insert(0, '/software/SAGEwork/Seiches')
import fft.filters as filters
import fft.fft_utils as fft_utils

years = dates.YearLocator()  # every year
months = dates.MonthLocator()  # every month
yearsFmt = dates.DateFormatter('%Y')
# every monday
mondays = dates.WeekdayLocator(MONDAY)

hour = dates.HourLocator(byhour = None, interval = 6, tz = None)


def display(dateTime, temp, label, k):
    fig = plt.figure(num = k, facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)
    ax.plot(dateTime, temp, linewidth = 1.6, color = 'r')
    # format the ticks
    formatter = dates.DateFormatter('%Y-%m')
    # formatter = dates.DateFormatter('`%y')
    # ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(formatter)
    # ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
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
    formatter = dates.DateFormatter('%Y-%m-%d')
    # formatter = dates.DateFormatter('`%y')
    # ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(formatter)
    # ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
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
    formatter = dates.DateFormatter('%Y-%m-%d')
    # formatter = dates.DateFormatter('`%y')
    # ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(formatter)
    # ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
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
    formatter = dates.DateFormatter('%Y-%m-%d')
    # formatter = dates.DateFormatter('`%y')
    # ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(formatter)
    # ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
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
                                      custom = None, maxdepth = None, tick = None, firstlog = None, fontsize = 20, ylim = None, \
                                      fill = False, show = True, minorgrid = None, datetype = 'date'):
    '''
    '''

    ax = display_temperatures(dateTimes, temps, k, fnames = fnames, revert = revert, difflines = difflines, custom = custom, \
                          maxdepth = maxdepth, tick = tick, firstlog = firstlog, fontsize = fontsize, ylim = ylim, fill = fill, \
                           show = False, minorgrid = minorgrid, datetype = datetype)

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
                          show = True, datetype = 'date', minorgrid = None, grid = None, ylab = None, settitle = False):

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
            if isinstance(fnames, str):
                if fnames.rfind('.') == -1:
                    lg = "%s" % (fnames)
                else:
                    fileName, fileExtension = os.path.splitext(fnames)
                    if fileName[0:3] == "zz_":
                        fileName = fileName[3:]
                    lg = '%s' % fileName
            elif isinstance(fnames, list) or isinstance(fnames, numpy.ndarray):
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
        formatter = dates.DateFormatter('%Y-%m-%d')
        # formatter = dates.DateFormatter('`%y')
        # ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(formatter)
        # ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))

        if minorgrid != None and grid != None:
            if minorgrid == 'hour':
                mgrid = hour
            elif minorgrid == 'mondays':
                mgrid = mondays
            else:
                mgrid = None
            if mgrid != None:
                ax.xaxis.set_minor_locator(mgrid)
        fig.autofmt_xdate()
    else:
        plt.xticks(fontsize = fontsize)
        plt.xlabel("Day of year").set_fontsize(fontsize)

    # ax.xaxis.set_minor_locator(mondays)

    # ax.xaxis.grid(True, 'major')
    if grid != None:
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
        if ylab == None:
            ylabel = title
        else:
            ylabel = ylab

    if ylim != None:
         ax.set_ylim(ylim[0], ylim[1])


    plt.ylabel(ylabel).set_fontsize(fontsize)

    labels = ax.get_xticklabels()
    plt.setp(labels, rotation = 0, fontsize = fontsize - 2)

    if settitle:
        plt.title(title).set_fontsize(fontsize + 2)
    plt.legend(legend)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    if show:
        plt.show()
    return ax

def display_marker_histogram(x, y, fnames, xlabel, ylabel, title = None, log = False, grid = True, fontsize = 22):
    '''
    Display the array as histogram with markers.
    '''

    params = {'legend.fontsize': fontsize - 4}
    plt.rcParams.update(params)

    marker = ['o', '*', '^', 'd', 's', 'p', 'o']
    colour = ['MediumTurquoise', 'Chartreuse', 'Yellow', 'Fuchsia', 'Red', 'b', 'aqua', 'r', 'g', 'k', 'm', 'c', 'y']
    legend = []
    for i in range(0, len(x)):
        if log:
            plt.yscale('log')

        # plt.plot(x[i], y[i])
        plt.plot(x[i], y[i], marker = marker[i], markersize = 9, lw = 2.2, color = colour[i],
                 markerfacecolor = 'None', markeredgecolor = colour[i])

        # Plot legend
        if fnames == None:
            legend.append("Sensor %s" % k[i][1])
        else:
            if fnames[i].rfind('.') == -1:
                legend.append("%s" % (fnames[i]))
            else:
                fileName, fileExtension = os.path.splitext(fnames[i])
                legend.append('%s' % fileName)

    plt.legend(legend)
    # Set the fontsize
    # for label in plt.legend().get_texts():
    #    label.set_fontsize('large')

    if title != None:
        plt.title(title).set_fontsize(fontsize + 2)
    plt.xlabel(xlabel).set_fontsize(fontsize + 18)
    plt.ylabel(ylabel).set_fontsize(fontsize + 18)
    plt.xticks(fontsize = fontsize - 4)
    plt.yticks(fontsize = fontsize - 4)
    plt.grid(grid, axis = 'both')
    plt.show()


def display_temperatures_subplot(dateTimes, temps, coeffs, k, fnames = None, revert = False, custom = None, maxdepth = None, tick = None, \
                                 firstlog = None, yday = None, delay = None, group = None, title = False, grid = False, processed = False, \
                                 limits = None, sharex = False):
    fig = plt.figure(facecolor = 'w', edgecolor = 'k')

    if group != None:
        format = 100 * (len(dateTimes) / 2) + 10
    else:
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
            dmax = dates.num2date(d[len(d) - 1])
            maxx = max(maxx, (dmax.timetuple().tm_yday + dmax.timetuple().tm_hour / 24. + dmax.timetuple().tm_min / (24. * 60) + dmax.timetuple().tm_sec / (24. * 3600)))

            dmin = dates.num2date(d[1])
            minx = min(minx, (dmin.timetuple().tm_yday + dmin.timetuple().tm_hour / 24. + dmin.timetuple().tm_min / (24. * 60) + dmin.timetuple().tm_sec / (24. * 3600) - delay[k]))


    i = 0
    if group != None:
        lenght = len(dateTimes) / 2
    else:
        lenght = len(dateTimes)
    ax = numpy.zeros(lenght, dtype = matplotlib.axes.Subplot)

    for j in range(0, lenght):
        if (sharex and j == 0) or not sharex:
            ax[j] = fig.add_subplot(format + j + 1)
        else:
            ax[j] = fig.add_subplot(format + j + 1, sharex = ax[0])

        if group != None:
            temp = [temps[i][1:], temps[i + 1][1:]]
            coef = [coeffs[i][1:], coeffs[i + 1][1:]]
            dateTime = [dateTimes[i][1:], dateTimes[i + 1][1:]]
        else:
            temp = temps[i][1:]
            coef = coeffs[i][1:]
            dateTime = dateTimes[i][1:]

        # ax.plot(dateTime[1:], coef[1:])
        if revert == True:
            if group != None:
                reversed_temp = [temps[i][::-1], temps[i + 1][::-1]]
                reversed_coef = [coeffs[i][::-1], coeffs[i + 1][::-1]]
            else:
                reversed_temp = temps[i][::-1]\

                reversed_coef = coeffs[i][::-1]
        else:
            reversed_temp = temp
            reversed_coef = coef

        lone = ""
        ltwo = ""
        if fnames == None:
            lg = "Sensor %s" % k[i][1]
        else:
            if fnames[i].rfind('.') == -1:
                if group != None:
                    lone = "%s" % (fnames[i])
                    ltwo = "%s" % (fnames[i + 1])
                else:
                    lone = "%s" % (fnames[i])
            else:
                if group != None:
                    fileName1, fileExtension1 = os.path.splitext(fnames[i])
                    fileName2, fileExtension2 = os.path.splitext(fnames[i + 1])
                    lone = '%s' % fileName1
                    ltwo = '%s' % fileName2
                else:
                    fileName, fileExtension = os.path.splitext(fnames[i])
                    lone = '%s' % fileName

        if processed:
            pdata = reversed_coef
        else:
            pdata = reversed_temp


        if yday == None:
            if group != None:
                lplt1 = ax[j].plot(dateTime[0], pdata[0], linewidth = 1.2, color = 'r', label = lone)
                lplt2 = ax[j].plot(dateTime[1], pdata[1], linewidth = 1.2, color = 'b', label = ltwo)

            else:
                lplt = ax[j].plot(dateTime, pdata, linewidth = 1.2, label = lone)
            # end if group


        else:

            dely = delay[i] if delay != None else 0.0

            # dates = [datetime.fromordinal(d) for d in dataTime]
            # dofy = [d.tordinal() - datetime.date(d.year, 1, 1).toordinal() + 1 for d in dates]
            if group != None:
                dtime1 = dateTime[0]
                dtime2 = dateTime[1]
                dofy1 = numpy.zeros(len(dtime1))
                for k in range(0, len(dtime1)):
                    d1 = dates.num2date(dtime1[k])
                    dofy1[k] = d1.timetuple().tm_yday + d1.timetuple().tm_hour / 24. + d1.timetuple().tm_min / (24. * 60) + d1.timetuple().tm_sec / (24. * 3600) - dely
                # end for
                dofy2 = numpy.zeros(len(dtime2))
                for k in range(0, len(dtime2)):
                    d2 = dates.num2date(dtime2[k])
                    dofy2[k] = d2.timetuple().tm_yday + d2.timetuple().tm_hour / 24. + d2.timetuple().tm_min / (24. * 60) + d2.timetuple().tm_sec / (24. * 3600) - dely
                # end for
                d2 = dates.num2date(dtime2)
            else:
                dtime1 = dateTime
                dofy1 = numpy.zeros(len(dtime1))
                for k in range(0, len(dtime1)):
                    d1 = dates.num2date(dtime1[k])
                    dofy1[k] = d1.timetuple().tm_yday + d1.timetuple().tm_hour / 24. + d1.timetuple().tm_min / (24. * 60) + d1.timetuple().tm_sec / (24. * 3600) - dely
                # end for
            # end if

            if group != None:
                lplt1 = ax[j].plot(dofy1, pdata[0], linewidth = 1.2, color = 'r', label = lone)
                lplt2 = ax[j].plot(dofy2, pdata[1], linewidth = 1.2, color = 'b', label = ltwo)
            else:
                lplt = ax[j].plot(dofy1, pdata, linewidth = 1.2, label = lone)

        # LEGEND
        # blue_proxy = plt.Rectangle((0, 0), 1, 1, fc = "b")
        # ax[i].legend([blue_proxy], ['cars'])
        # ax[j].legend(shadow = True, fancybox = True)
        handles, labels = ax[j].get_legend_handles_labels()
        ax[j].legend(handles, labels)

        # X-AXIS -Time
        # format the ticks
        if yday == None:
            formatter = dates.DateFormatter('%Y-%m-%d')
            # formatter = dates.DateFormatter('`%y')

            ax[j].xaxis.set_major_formatter(formatter)
            # ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
            ax[j].xaxis.set_minor_locator(mondays)
            fig.autofmt_xdate()

        if grid:
            # ax.xaxis.grid(True, 'major')
            ax[j].yaxis.grid(True, 'minor')
        else:
            ax[j].yaxis.grid(False),
        ax[j].xaxis.grid(True, 'major')

        if custom == None:
            ylabel = ' T [$^\circ$C]'
            ax[j].set_ylabel(ylabel).set_fontsize(18)
            if title:
                title = ' Temperature Profiles - %s' % lone
        else:
            if title:
                title = ' Profile: %s' % custom[i]
                ax[j].set_ylabel(custom[i])
        if title:
            ax[j].set_title(title).set_fontsize(20)

        if yday == None:
            if group != None:
                ax[j].set_xlim(xmax = dateTime[0][len(dateTime) - 1])
                if j == lenght - 1:
                    ax[j].set_xlabel("Time").set_fontsize(20)
            else:
                ax[j].set_xlim(xmax = dateTime[len(dateTime) - 1])
                if j == lenght - 1:
                    ax[j].set_xlabel("Time").set_fontsize(20)
        else:
            if delay != None:
                ax[j].set_xlim(xmin = minx, xmax = maxx)

            if j == lenght - 1:
                ax[j].set_xlabel("day of the year").set_fontsize(20)

        # limits
        if limits != None:
            ax[j].set_ylim(ymin = limits[0] , ymax = limits[1])


        if maxdepth != None:
            if firstlog != None:
                mindepth = firstlog
            else:
                mindepth = 0
            ax[j].set_ylim(mindepth, maxdepth[i])

        # ax[j].legend(lplt, title = lg, shadow = True, fancybox = True)
        if tick != None:
           ax[j].set_yticks(tick[i][1])
           ax[j].set_yticklabels(tick[i][0])

        # set labels visibility
        plt.setp(ax[j].get_xticklabels(), visible = True)

        if group != None:
            i += 2
        else:
            i += 1

        if sharex and j < lenght - 1:
            plt.setp(ax[j].get_xticklabels(), visible = False)
        elif sharex and j == lenght - 1:
            plt.setp(ax[j].get_xticklabels(), visible = True)
    # end for

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    # fig.autofmt_xdate()

    # new seting to make room for labels
    # plt.tight_layout()

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
            dmax = dates.num2date(d[len(d) - 1])
            maxx = max(maxx, (dmax.timetuple().tm_yday + dmax.timetuple().tm_hour / 24. + dmax.timetuple().tm_min / (24. * 60) + dmax.timetuple().tm_sec / (24. * 3600)))

            dmin = dates.num2date(d[0])
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
                d = dates.num2date(dateTime[j])
                dofy[j] = d.timetuple().tm_yday + d.timetuple().tm_hour / 24. + d.timetuple().tm_min / (24. * 60) + d.timetuple().tm_sec / (24. * 3600)

            lplt = ax[i].plot(dofy[1:], reversed_depth[1:], linewidth = 1.4, label = lg)




        # LEGEND
        # blue_proxy = plt.Rectangle((0, 0), 1, 1, fc = "b")
        # ax[i].legend([blue_proxy], ['cars'])
        ax[i].legend(shadow = True, fancybox = True)


        # X-AXIS -Time
        # format the ticks
        if yday == None:
            formatter = dates.DateFormatter('%Y-%m-%d')
            # formatter = dates.DateFormatter('`%y')

            ax[i].xaxis.set_major_formatter(formatter)
            # ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
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


def display_mixed_subplot(dateTimes1 = [], data = [] , varnames = [], ylabels1 = [], \
                          dateTimes2 = [], groups = [], groupnames = [], ylabels2 = [], \
                          dateTimes3 = [], imgs = [], ylabels3 = [], ticks = [], maxdepths = [], firstlogs = [], maxtemps = [], mindepths = [], mintemps = [], \
                          interp = None, fnames = None, revert = False, custom = None, maxdepth = None, tick = None, firstlog = None, yday = None, \
                          title = False, grid = False, limits = None, sharex = False, fontsize = 18):
    fig = plt.figure(facecolor = 'w', edgecolor = 'k')

    len1 = len(dateTimes1)
    len2 = len(dateTimes2) / 2
    len3 = len(dateTimes3)
    length = len1 + len2 + len3
    format = 100 * length + 10
    matplotlib.rcParams['legend.fancybox'] = True
    if yday != None:
        datetype = 'dayofyear'
        minx = 10000000.
        maxx = 0.

        # find maxx and minX of the X axis
        for k in range(0, len(dateTimes1)):
            d = dateTimes1[k]
            dmax = dates.num2date(d[len(d) - 1])
            maxx = max(maxx, (dmax.timetuple().tm_yday + dmax.timetuple().tm_hour / 24. + dmax.timetuple().tm_min / (24. * 60) + dmax.timetuple().tm_sec / (24. * 3600)))

            dmin = dates.num2date(d[1])
            minx = min(minx, (dmin.timetuple().tm_yday + dmin.timetuple().tm_hour / 24. + dmin.timetuple().tm_min / (24. * 60) + dmin.timetuple().tm_sec / (24. * 3600)))
    else:
        datetype = 'date'
    # end if

    i = 0

    ax = numpy.zeros(length, dtype = matplotlib.axes.Subplot)
    axb = numpy.zeros(len3, dtype = matplotlib.axes.Subplot)
    il = 0  # index one line
    ig = 0  # index group
    ii = 0  # index img

    gs1 = gridspec.GridSpec(length, 1)

    for j in range(0, length):
        ax[j] = fig.add_subplot(gs1[j])
        if j < len1 and il < len1:
            if revert != True:
                temp = data[il][:]
                dateTime = dateTimes1[il][:]
            else:
                temp = data[il][::-1]
                dateTime = dateTimes1[il][::-1]

            if yday == None:
                lplt = ax[j].plot(dateTime, temp, linewidth = 1.2, color = 'k', label = varnames[il - 1])
                pass
            else:
                dtime1 = dateTime
                dofy1 = numpy.zeros(len(dtime1))
                for k in range(0, len(dtime1)):
                    d1 = dates.num2date(dtime1[k])
                    dofy1[k] = d1.timetuple().tm_yday + d1.timetuple().tm_hour / 24. + d1.timetuple().tm_min / (24. * 60) + d1.timetuple().tm_sec / (24. * 3600)
                # end for
                lplt = ax[j].plot(dofy1, temp, linewidth = 1.2, color = 'k', label = varnames[il - 1])

            # endif
            il += 1
            ax[j].locator_params(nbins = 4, axis = 'y')
        # groups
        elif j > len1 - 1 and j < len1 + len2 and ig < len(groups):
            if revert != True:
                temp = [groups[ig][1:], groups[ig + 1][:]]
                dateTime = [dateTimes2[ig][1:], dateTimes2[ig + 1][:]]
            else:
                temp = [groups[ig][::-1], groups[ig + 1][::-1]]
                dateTime = [dateTimes2[ig][::-1], dateTimes2[ig + 1][::-1]]
            if yday == None:
                lplt1 = ax[j].plot(dateTime[0], temp[0], linewidth = 1.2, color = 'r', label = groupnames[ig])
                lplt2 = ax[j].plot(dateTime[1], temp[1], linewidth = 1.2, color = 'b', label = groupnames[ig + 1])
                pass
            else:
                dtime1 = dateTime[0]
                dtime2 = dateTime[1]
                dofy1 = numpy.zeros(len(dtime1))
                for k in range(0, len(dtime1)):
                    d1 = dates.num2date(dtime1[k])
                    dofy1[k] = d1.timetuple().tm_yday + d1.timetuple().tm_hour / 24. + d1.timetuple().tm_min / (24. * 60) + d1.timetuple().tm_sec / (24. * 3600)
                # end for
                dofy2 = numpy.zeros(len(dtime2))
                for k in range(0, len(dtime2)):
                    d2 = dates.num2date(dtime2[k])
                    dofy2[k] = d2.timetuple().tm_yday + d2.timetuple().tm_hour / 24. + d2.timetuple().tm_min / (24. * 60) + d2.timetuple().tm_sec / (24. * 3600)
                # end for
                d2 = dates.num2date(dtime2)
                lplt1 = ax[j].plot(dofy1, temp[0], linewidth = 1.2, color = 'r', label = groupnames[ig])
                lplt2 = ax[j].plot(dofy2, temp[1], linewidth = 1.2, color = 'b', label = groupnames[ig + 1])

            ig += 2
            ax[j].locator_params(nbins = 4, axis = 'y')
        # images
        elif j > len1 + len2 - 1 and j < length and ii < len3:
            # Make some room for the colorbar
            fig.subplots_adjust(left = 0.07, right = 0.87)

            # Add the colorbar outside...
            box = ax[j].get_position()
            pad, width = 0.02, 0.014
            axb[ii] = fig.add_axes([box.xmax + pad, box.ymin, width, box.height])
            display_img_temperatures_sub(fig, ax[j], axb[ii], dateTimes3[ii], imgs[ii], ticks[ii], maxdepths[ii], firstlogs[ii], maxtemps[ii], \
                                     mindepths[ii], mintemps[ii], \
                                     revert = revert, fontsize = fontsize, datetype = datetype, thermocline = True, \
                                     interp = interp, ycustom = None, sharex = sharex, colorbar = True)

            ii += 1
        # end if


        # LEGEND
        # blue_proxy = plt.Rectangle((0, 0), 1, 1, fc = "b")
        # ax[i].legend([blue_proxy], ['cars'])
        # ax[j].legend(shadow = True, fancybox = True)
        handles, labels = ax[j].get_legend_handles_labels()
        if (j < len1 and il - 1 < len1) or (j > len1 - 1 and j < len1 + len2 and ig - 2 < len(groups)):
            ax[j].legend(handles, labels)

        # X-AXIS -Time
        # format the ticks
        if yday == None:
            formatter = dates.DateFormatter('%Y-%m-%d')
            # formatter = dates.DateFormatter('`%y')

            ax[j].xaxis.set_major_formatter(formatter)
            # ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
            ax[j].xaxis.set_minor_locator(mondays)
            fig.autofmt_xdate()

        if grid:
            # ax.xaxis.grid(True, 'major')
            ax[j].yaxis.grid(True, 'minor')
        else:
            ax[j].yaxis.grid(False),
        ax[j].xaxis.grid(True, 'major')


        if j < len1 and il - 1 < len1:
            ylabel = ylabels1[il - 1]
        # groups
        elif j > len1 - 1 and j < len1 + len2 and ig - 2 < len(groups):
            ylabel = ylabels2[ig - 2]
        elif j > len1 + len2 - 1 and j < length and ii - 1 < len3:
            ylabel = ylabels3[ii - 1]
        # end if
        ax[j].set_ylabel(ylabel).set_fontsize(fontsize + 4)

        if  custom and title:
            title = ' Profile: %s' % custom[i]
            ax[j].set_ylabel(custom[i])
            ax[j].set_title(title).set_fontsize(fontsize)

        if yday == None:
            if j > len1 - 1 and j < len1 + len2:
                ax[j].set_xlim(xmax = dateTime[0][len(dateTime) - 1])
                if j == length - 1:
                    ax[j].set_xlabel("Time").set_fontsize(fontsize)
            elif j < len1:
                ax[j].set_xlim(xmax = dateTime[len(dateTime) - 1])
                if j == length - 1:
                    ax[j].set_xlabel("Time").set_fontsize(frontsize)
        else:
            if j == length - 1:
                ax[j].set_xlabel("Day of the year").set_fontsize(fontsize + 4)
            # end
            ax[j].set_xlim(xmin = dofy1[0], xmax = dofy1[len(dofy1) - 1])

        # limits
        if limits != None:
            ax[j].set_ylim(ymin = limits[0] , ymax = limits[1])

        if maxdepth != None:
            if firstlog != None:
                mindepth = firstlog
            else:
                mindepth = 0
            ax[j].set_ylim(mindepth, maxdepth[i])

        # ax[j].legend(lplt, title = lg, shadow = True, fancybox = True)
        if tick != None:
           ax[j].set_yticks(tick[i][1])
           ax[j].set_yticklabels(tick[i][0])

        i += 1

        if sharex and j < length - 1:
            plt.setp(ax[j].get_xticklabels(), visible = False, fontsize = fontsize)
        elif sharex and j == length - 1:
            plt.setp(ax[j].get_xticklabels(), visible = True, fontsize = fontsize)

        plt.setp(ax[j].get_yticklabels(), visible = True, fontsize = fontsize)



    # end for
    # set labels visibility

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    # fig.autofmt_xdate()

    # new seting to make room for labels
    # plt.tight_layout()

    plt.draw()
    plt.show()


def display_img_temperatures_sub(fig, ax, axb, dateTimes, temps, tick, maxdepth, firstlog, maxtemp, mindepth, mintemp, revert = False, \
                             fontsize = 20, datetype = 'date', thermocline = True, interp = None, \
                             ycustom = None, sharex = False, colorbar = False):
    n = len(dateTimes[0]) - 1
    m = len(dateTimes)

    if numpy.ndim(temps) == 2:
        Temp = temps[:, 1:]
    else:
        Temp = numpy.zeros((m, n))
        i = 0
        for dateTime in dateTimes:
            j = 0
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

            # Loop for shorter series (sensor malfunction) that need interpolation
            # Conditions:
            #    1- the  first and time series must be good
            #    2 - The bad time series can not be last or first (actually is implied from 1.
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

    if datetype == 'dayofyear':
        dateTime = fft_utils.timestamp2doy(dateTimes[0][1:])
    else:
        dateTime = dateTimes[0][1:]


    y = numpy.linspace(mindepth, maxdepth - firstlog, m)
    if interp != None:
        from scipy.interpolate import interp1d
        new_y = numpy.linspace(mindepth, maxdepth - firstlog, m * interp)
        fint = interp1d(y, Temp.T, kind = 'cubic')
        newTemp = fint(new_y).T
        if revert == True:
            yrev = new_y[::-1]
        else:
            yrev = new_y

    else:
        if revert == True:
            yrev = y[::-1]
        else:
            yrev = y
        # if
        newTemp = Temp
    # end if interp

    X, Y = numpy.meshgrid(dateTime, yrev)
    if maxtemp != None and mintemp != None:
        im = ax.pcolormesh(X, Y, newTemp, shading = 'gouraud', vmin = mintemp, vmax = maxtemp)  # , cmap = 'gray', norm = LogNorm())
    else:
        im = ax.pcolormesh(X, Y, newTemp, shading = 'gouraud')  # , cmap = 'gray', norm = LogNorm())

    if colorbar:
        cb = fig.colorbar(im, cax = axb)
        cb.set_clim(mintemp, maxtemp)
        labels = cb.ax.get_yticklabels()
        for t in labels:
            t.set_fontsize(fontsize - 2)
        from matplotlib import ticker
        tick_locator = ticker.MaxNLocator(nbins = 5)
        cb.locator = tick_locator
        cb.update_ticks()
    # end if

    if ycustom != None:
        ylabel = ycustom
        plt.ylabel(ylabel).set_fontsize(fontsize)
    # end if


    # reverse
    # ax.set_ylim(ax.get_ylim()[::-1])

    ax.set_ylim(0, maxdepth)
    ax.set_yticks(tick[1])
    ax.set_yticklabels(tick[0])
    labels = ax.get_yticklabels()
    ax.tick_params(labelsize = fontsize)

    # plt.setp(labels, rotation = 0, fontsize = fontsize)

    # format the ticks
    if sharex == False:
        if datetype == "date" :
            formatter = dates.DateFormatter('%Y-%m-%d')
            # formatter = dates.DateFormatter('`%y')
            # ax.xaxis.set_major_locator(years)
            ax.xaxis.set_major_formatter(formatter)
            # ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
            plt.setp(labels, rotation = 0, fontsize = fontsize)
            fig.autofmt_xdate()
        else:
            plt.xticks(fontsize = fontsize)
            # plt.xlabel("day of year").set_fontsize(fontsize)

        ax.xaxis.set_minor_locator(hour)

        labels = ax.get_xticklabels()
    # end if sharex

    # draw the thermocline
    if thermocline:
        levels = [13]
        colors = ['k']
        linewidths = [1]
        ax.contour(X, Y, newTemp, levels, colors = colors, linewidths = linewidths, fontsize = fontsize)

# end display_img_temperatures_sub

def display_img_temperatures(dateTimes, temps, coeffs, k, tick, maxdepth, firstlog, maxtemp, revert = False, \
                             fontsize = 20, datetype = 'date', thermocline = True, interp = None, ycustom = None):
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

        # Loop for shorter series (sensor malfunction) that need interpolation
        # Conditions:
        #    1- the  first and time series must be good
        #    2 - The bad time series can not be last or first (actually is implied from 1.
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

    if datetype == 'dayofyear':
        dateTime = fft_utils.timestamp2doy(dateTimes[0][1:])
    else:
        dateTime = dateTimes[0][1:]

    y = numpy.linspace(0, maxdepth - firstlog, m)

    if interp != None:
        from scipy.interpolate import interp1d
        print "Interpolating on the vertical axis : n=%d" % interp
        new_y = numpy.linspace(0, maxdepth - firstlog, m * interp)
        fint = interp1d(y, Temp.T, kind = 'cubic')
        newTemp = fint(new_y).T
        if revert == True:
            yrev = new_y[::-1]
        else:
            yrev = new_y
        X, Y = numpy.meshgrid(dateTime, yrev)
        im = ax.pcolormesh(X, Y, newTemp, shading = 'gouraud')  # , cmap = 'gray', norm = LogNorm())
    else:
        if revert == True:
            yrev = y[::-1]
        else:
            yrev = y
        X, Y = numpy.meshgrid(dateTime, yrev)
        im = ax.pcolormesh(X, Y, Temp, shading = 'gouraud')  # , cmap = 'gray', norm = LogNorm())


    # HERE = > interpolation, speedup, what is wrong at the ned is red
#===============================================================================
#     from matplotlib.image import NonUniformImage
#     from matplotlib import cm
#     interp = 'bilinear'
#
#     im = NonUniformImage(ax, interpolation = interp, extent = (dateTime[0], dateTime[len(dateTime) - 1], 0, maxdepth - firstlog + 5),
#                      cmap = cm.jet)
#     im.set_data(dateTime, yrev, Temp)
#     ax.images.append(im)
#===============================================================================

    cb = fig.colorbar(im)
    cb.set_clim(0, maxtemp)
    labels = cb.ax.get_yticklabels()
    plt.setp(labels, rotation = 0, fontsize = fontsize)

    if ycustom == None:
        ylabel = ' Depth (m)'
    else:
        ylabel = ycustom
    print "fontsize: %d" % fontsize
    plt.ylabel(ylabel).set_fontsize(fontsize + 4)
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
        formatter = dates.DateFormatter('%Y-%m-%d')
        # formatter = dates.DateFormatter('`%y')
        # ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(formatter)
        # ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
        plt.setp(labels, rotation = 0, fontsize = fontsize)
        fig.autofmt_xdate()
    else:
        plt.xticks(fontsize = fontsize)
        plt.xlabel("Day of year").set_fontsize(fontsize + 4)

    ax.xaxis.set_minor_locator(hour)

    labels = ax.get_xticklabels()

    # draw the thermocline
    if thermocline:
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

def display_avg_vertical_temperature_profiles_err_bar_range(dateTimes, temps, startdepth, revert = False, profiledates = None, \
                                                            legendloc = 4, grid = False, title = None):

    temp = numpy.zeros(len(dateTimes))
    depth = numpy.linspace(startdepth, len(dateTimes) + startdepth, len(dateTimes))
    fig = plt.figure(facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)

    legend = []
    ls = ['-', '--', ':', '-.', '-', '--', ':', '-.']

    lidx = 0
    avg_temp_arr = []
    avg_temp_arr_range_min = []
    avg_temp_arr_range_max = []
    avg_temp_arr_std = []

    for j in range(0, len(dateTimes)):  # depth
        if j != 18:
            temp_at_depth_j = temps[j][1:]
        else:
            temp_at_depth_j = (temps[j - 1][1:] + temps[j + 1][1:]) / 2.
        avg_temp = numpy.mean(temp_at_depth_j, axis = 0)
        avg_temp_std = numpy.std(temp_at_depth_j, axis = 0)
        avg_temp_min = numpy.min(temp_at_depth_j, axis = 0)
        avg_temp_max = numpy.max(temp_at_depth_j, axis = 0)

        avg_temp_arr.append(avg_temp)
        avg_temp_arr_std.append(avg_temp_std)
        avg_temp_arr_range_min.append(avg_temp - avg_temp_min)
        avg_temp_arr_range_max.append(avg_temp_max - avg_temp)
        print "depth %d,  max:%f min:%f" % (j, avg_temp_max, avg_temp_min)

    if revert == True:
        reversed_temp = avg_temp_arr[::-1]
    else:
        reversed_temp = avg_temp_arr

    ax.plot(reversed_temp, depth, linestyle = ls[lidx], linewidth = 3.2)
    ax.errorbar(reversed_temp, depth, xerr = avg_temp_arr_std, linewidth = 2.8, color = 'r', capthick = 3)  # , fmt = 'o')
    ax.errorbar(reversed_temp, depth, xerr = [avg_temp_arr_range_min, avg_temp_arr_range_max], color = 'k', linewidth = 1.2, capthick = 2)  # , fmt = 'd')
    lidx += 1
    # lg = '%s' % datetime.date.fromordinal(int(dateTimes[0][j]))
    # legend.append(lg)

    if profiledates != None:
        dt = dateTimes[0][2] - dateTimes[0][1]
        # get indices

        occurence = []
        for k in profiledates:
            occurence.append(numpy.where(abs(dateTimes[0] - k) < dt))

        temp1 = []
        temp2 = []
        for tm in temps:  # depth
            temp1.append(tm[occurence[0][0][0]])
            temp2.append(tm[occurence[1][0][0]])

        ax.plot(temp1, depth, linestyle = ':', linewidth = 1.8, color = 'r')
        ax.plot(temp2, depth, linestyle = ':', linewidth = 1.8, color = 'b')

    ax.grid(grid)

    xlabel = ' Temperature ($^\circ$C)'
    plt.xlabel(xlabel).set_fontsize(20)
    ylabel = ' Depth (m)'
    plt.ylabel(ylabel).set_fontsize(20)
    if title != None:
        plt.title(title).set_fontsize(22)
    # reverse

    ax.set_ylim(ax.get_ylim()[::-1])  # [::1] reverses the array



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
    # plt.legend(legend, loc = legendloc, prop = {'size':12})

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    # fig.autofmt_xdate()
    plt.show()
