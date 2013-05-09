# from __future__ import division
import numpy as np
from scipy.integrate import simps, trapz
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import date2num, num2date
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates
import time, os, datetime, math

years = matplotlib.dates.YearLocator()  # every year
months = matplotlib.dates.MonthLocator()  # every month
yearsFmt = matplotlib.dates.DateFormatter('%Y')
# every monday
mondays = matplotlib.dates.WeekdayLocator(MONDAY)

hour = matplotlib.dates.HourLocator(byhour = None, interval = 4, tz = None)

def simpson(f, a, b, n):
    """Approximates the definite integral of f from a to b by
    the composite Simpson's rule, using n subintervals"""
    h = (b - a) / n
    s = f(a) + f(b)

    for i in range(1, n, 2):
        s += 4 * f(a + i * h)
    for i in range(2, n - 1, 2):
        s += 2 * f(a + i * h)

    return s * h / 3


def trapezoidal_rule(f, a, b, n):
    """Approximates the definite integral of f from a to b by
    the composite trapezoidal rule, using n subintervals"""
    h = (b - a) / n
    s = f(a) + f(b)
    for i in xrange(1, n):
        s += 2 * f(a + i * h)
    return s * h / 2

def integrate(y_vals, h):
    i = 1
    total = y_vals[0] + y_vals[-1]
    for y in y_vals[1:-1]:
        if i % 2 == 0:
            total += 2 * y
        else:
            total += 4 * y
        i += 1
    return total * (h / 3.0)

def integrate_simpson(x, y):

    b = x[len(x) - 1]
    a = x[0]
    n = len(x)
    h = (b - a) / len(x)
    s = y[0] + y[-1]

    for i in range(1, n , 2):
        s += 4 * y[i]
    for i in range(2, n - 1, 2):
        s += 2 * y[i]

    return s * h / 3.0


if __name__ == '__main__':
    print simpson(lambda x:x ** 9, 0.0, 10.0, 100000)
    print trapezoidal_rule(lambda x:x ** 9, 0.0, 10.0, 100000)
    # displays 1000000000.75

    x = np.linspace(-10, 10, 100000, endpoint = True)
    y = x ** 2
    print integrate_simpson(x, y)
    # print simps(y, dx = x[2] - x[1])
    print simps(y, x)
    fig = plt.figure(facecolor = 'w', edgecolor = 'k')
    plt.plot(x, y)
    y2 = [40  for i in range(len(x))]
    plt.plot(x, y2)
    ay = np.array(y)
    ay2 = np.array(y2)
    ax = np.array(x)
    minarr = [ min(ay[i], ay2[i]) for i in range(len(x)) ]
    area_min = simps(minarr, ax)
    area_line = simps(ay2, ax)
    A = area_line - area_min
    print "Upwellin Area=%f, Under line=%f Min line area=%f" % (A, area_line, area_min)
    plt.show()

