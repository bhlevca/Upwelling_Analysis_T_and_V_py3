
import matplotlib.pyplot as plt
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates
import time, os, datetime, math, sys


years = matplotlib.dates.YearLocator()  # every year
months = matplotlib.dates.MonthLocator()  # every month
yearsFmt = matplotlib.dates.DateFormatter('%Y')
mondays = matplotlib.dates.WeekdayLocator(MONDAY)
hour = matplotlib.dates.HourLocator(byhour = None, interval = 2, tz = None)

def display_temperature(dateTimes, coeffs):
    fig = plt.figure(facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)
    i = 0
    ls = ['-', '--', ':', '-.', '-', '--', ':', '-.']
    for dateTime in dateTimes:
        coef = coeffs[i]
        ax.plot(dateTime, coef, linestyle = ls[i], linewidth = 1.2 + 0.2 * i)
        i += 1

    # format the ticks
    formatter = matplotlib.dates.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_minor_locator(hour)

    ax.xaxis.grid(True, 'minor')
    fig.autofmt_xdate()
    plt.show()

if __name__ == '__main__':

    show_bug = True
    if show_bug:
        dates = ['01/02/1991', '02/01/1991', '03/01/1991']
    else:
        dates = ['01/02/1991', '01/20/1991', '01/30/1991']

    x = [datetime.datetime.strptime(d, '%m/%d/%Y').date() for d in dates]
    y = range(len(x))

    display_temperature(x, y)

