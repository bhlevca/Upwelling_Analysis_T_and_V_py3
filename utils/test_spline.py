from numpy import linspace, exp
from numpy.random import randn
from scipy.interpolate import UnivariateSpline

import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import date2num, num2date
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates

years = matplotlib.dates.YearLocator()   # every year
months = matplotlib.dates.MonthLocator()  # every month
yearsFmt = matplotlib.dates.DateFormatter('%Y')
# every monday
mondays = matplotlib.dates.WeekdayLocator(MONDAY)

def display2(dateTime, temp, coeff, label, k):
    fig = plt.figure(num = k, facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)
    ax.plot(dateTime, temp, 'r', dateTime, coeff, linewidth = 0.3, color = 'b')
    ax.xaxis.grid(True, 'minor')
    ax.grid(True)


    plt.show()

x = linspace(-3, 3, 100)
y = exp(-x ** 2) + randn(100) / 10
s = UnivariateSpline(x, y, s = 0.1)
xs = linspace(-3, 3, 100)
ys = s(xs)

display2(x, y, ys, "test", 1)
