#! /usr/bin/env python
"""Try smoothing data with numpy.

This uses the idea that convolving data with a response function
is actually nothing else but smoothing data.


Date: December 7, 2008

Author: Bob Wimmer

"""
from numpy import *
from numpy.random import *
import Gnuplot, Gnuplot.funcutils
import numpy
from numpy.fft import *


def plot(x, y, desc = 'plot'):
    #x, y = tsc.fft()
    data = Gnuplot.Data(x, y, using = (1, 2)) #this ensures that t is used as x axis
    gg = Gnuplot.Gnuplot()
    string = 'set title "' + str(desc) + '"'
    gg(string)
    gg('set ylabel "y-axis [arb. units]"')
    gg('set xlabel "x-axis [arb. units]"')
    gg('set style data lines')
    gg.plot(data)



class timeseries(object):
    """Time series given by x vlaues (e.g. time) and y values (e.g. temperature).
    Perform various operations on time series wuc as:
    - treat/replace missing values
    - smoothing
    - FFT
    - and more to come (maybe)

    Note: requires numpy

    """
    def __init__(self, x, y):
        if len(x) < 2:
            print "this is not a time series, but a single point!"
        if len(y) != len(x):
            print "len(x) != len(y) -- this needs to be fixed!"

        self.x = x
        self.y = y
        self.beginning = x[0]
        self.end = x[-1]


    def max(self):
        """returns the maximum of x, y"""
        return self.x.max(), self.y.max()

    def min(self):
        """returns the minimum of x, y"""
        return self.x.min(), self.y.min()

    def cut_ind(self, lo, hi):
        """return subset of time series between lo and hi indices."""
        self.xci = self.x[lo:hi]
        self.yci = self.y[lo:hi]
        return self.xci, self.yci

    def cut_x(self, x_lo, x_hi):
        """return subset of time series between x_lo and x_hi values."""
        """find indices of x_lo and x_hi, then call cut_ind"""
        lo = self.x.searchsorted(x_lo)
        hi = self.x.searchsorted(x_hi)
        print lo, self.x[lo], self.x[lo - 1]
        self.xcx = self.x[lo:hi]
        self.ycx = self.y[lo:hi]
        return self.xcx, self.ycx

    def clean(self):
        """remove and/or linearly interpolate appropriately missing data values"""
        """This is not yet implemented"""

    def fft(self):
        self.foury = fft(self.y)
        N = len(self.y)
        timestep = self.x[1] - self.x[0]        # if unit=day -> freq unit=cycles/day
        self.fourx = fftfreq(N, d = timestep)
        self.fourx = fftshift(self.fourx)
        self.foury = fftshift(self.foury)
        return self.fourx, self.foury


    def smooth(self, x, window_len = 10, window = 'hanning'):
        #print "in smooth method"
        #print x, window_len, window
        self.s = numpy.r_[2 * x[0] - x[window_len:1:-1], x, 2 * x[-1] - x[-1:-window_len:-1]]
        print(len(self.s))
        if window == 'flat': #moving average
            w = ones(window_len, 'd')
        else:
            w = eval('numpy.' + window + '(window_len)')
        y = numpy.convolve(w / w.sum(), self.s, mode = 'same')
        dy = self.s.copy()
        dy[window_len - 1:-window_len + 1] = self.s[window_len - 1:-window_len + 1] - y[window_len - 1:-window_len + 1]
        return y[window_len - 1:-window_len + 1], dy[window_len - 1:-window_len + 1]


    def plot(self):
        """Plot the results with Gnuplot."""
        data = Gnuplot.Data(self.x, self.y, using = (1, 2)) #this ensures that t is used as x axis
        g = Gnuplot.Gnuplot()
        g('set ylabel "y-axis [arb. units]"')
        g('set xlabel "x-axis [arb. units]"')
        g('set style data lines')
        g.plot(data)



def demo():
    t = linspace(0, 10, 256)
    xp1 = sin(t)
    #add some random noise to the time series
    xn1 = xp1 + randn(len(t)) * 0.1
    ts = timeseries(t, xn1)
    #smooth the timeseries with a rectangular smoothing window of length 10
    y, dy = ts.smooth(xn1, 10, 'flat')
    #plot original and smoothed data
    data1 = Gnuplot.Data(t, xn1, using = (1, 2))
    data2 = Gnuplot.Data(t, y, using = (1, 2))
    g = Gnuplot.Gnuplot()
    g('set style data lines')
    g.plot(data1, data2)
    plot(t, dy, 'dy')
    #calculate FFTs just for fun (we'll look at that some more in power_spectral_density.py)
    ty = timeseries(t, y)
    ty_fft_k, ty_fft_y = ty.fft()
    plot (ty_fft_k, ty_fft_y, 'fft of y')
    tdy = timeseries(t, dy)
    tdy_fft_k, tdy_fft_dy = tdy.fft()
    plot (tdy_fft_k, tdy_fft_dy, 'fft of dy')


if __name__ == '__main__':
    demo()
    raw_input('Please press the return key to continue...\n')
