'''
Created on Sept 03, 2014

@author: bogdan
'''
# numerical imports
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, num2date

# system imports
import time, os
import csv
import math
from datetime import datetime

# specific tasks and 3rd party
from pandas import *


class LimnologyTimesSeries(object):
    '''
    classdocs
    '''

    def __init__(self, reader_obj, window):
        ''' LimnologyTimesSeries Constructor
        :param reader_obj location the data files
        :param window: None, '5Min', '60Min' etc

        '''
        self.timenum = None
        self.time = None
        self.data = None
        self.ts = None

        # load the data
        [self.timenum, self.data] = reader_obj.readData()
        self.time = self.convert_to_date(self.timenum)

        # create the timeseries
        ts_res = pandas.Series(self.data, index = self.time)

        # resample so that all series are the same
        if window == None:
            self.ts = ts_res
        else:
            self.ts = ts_res.resample(window, how = 'mean')

        self.data = self.ts.values

    # end

    def convert_to_date(self, timenum):

        dat = []
        i = 0
        for t in timenum:
            if t < 695056:
                t += 695056
            datet = num2date(t)
            dat.append(datet)
            i += 1
        return dat

    def reindex(self, ts2, method = 'ffill'):
        '''Reindex the series based on another time series.

        :param ts2: model time series
        :param method: ffil or pad, default pad
        :rtype: None
        '''
        self.ts.reindex(ts2.ts.index, method = method)
    # end

    @staticmethod
    def cross_corr(ts1, ts2, lag = None):
        '''Calculate the cross- correlation function between series
           based on pairwise complete observations.

           In signal processing, cross-correlation is a measure of similarity
           of two waveforms as a function of a time-lag applied to one of them.

        :param ts1: original time series
        :param ts2: times series to be correlated with
        :param lag: int -- number of time units shifted ( can be negative)
        :returns: float -- the correlation coefficient
        '''
        # The reindex function enables you to align data while filling forward values
        # (getting the "as of" value)
        ts1.reindex(ts2, 'ffill')

        ra = []
        for l in range(0, lag):
            sum = 0
            for i in range (0, len(ts1.ts) - l):
                sum += ts1.data[i] * ts2.data[i + l]

            # R is the correlation coefficient at "delay"
            R = 1. / (len(ts1.ts) - l) * sum
            ra.append(R)

        # end
        LimnologyTimesSeries.display(range(0, lag), ra, "lag", "r coeff")
        if np.max(ra) < 0 :
            return np.min(ra)
        else:
            return np.max(ra)

    @staticmethod
    def pearson_corr_coeff(ts1, ts2, lag = None):
        '''Calculate the correlation between series
           based on pairwise complete observations.

        :param ts1: original time series
        :param ts2: times series to be correlated with
        :param lag: int -- number of time units shifted ( can be negative)
        :returns: float -- the correlation coefficient
        '''
        # The reindex function enables you to align data while filling forward values
        # (getting the "as of" value)
        ts1.reindex(ts2, 'ffill')

        sum = 0
        std1 = np.std(ts1.data)
        std2 = np.std(ts2.data)
        mean1 = np.mean(ts1.data)
        mean2 = np.mean(ts2.data)

        for i in range (0, len(ts1.ts) - lag):
            sum += (ts1.data[i] - mean1) * (ts2.data[i + lag] - mean2)
            # sum += (ts1.data[i] - mean1) * (ts2.data[i] - mean2)

        R = sum / ((len(ts1.ts) - lag) * std1 * std2)
        return R


    @staticmethod
    def normalized_cross_corr_coeff(ts1, ts2, lag = 100):
        '''Calculate the normalized cross correlation between series
           based on pairwise complete observations.

        :param ts1: original time series
        :param ts2: times series to be correlated with
        :param lag: int -- number of time units shifted ( can be negative)
        :returns: float -- the correlation coefficient
        '''
        # The reindex function enables you to align data while filling forward values
        # (getting the "as of" value)
        ts1.reindex(ts2, 'ffill')
        ra = []

        # Calculate the mean of the two series x[], y[]
        mx = 0
        my = 0
        for i in range(0, len(ts1.data)) :
            mx += ts1.data[i]
            my += ts2.data[i]

        mx /= len(ts1.ts)
        my /= len(ts2.ts)

        # Calculate the denominator
        sx = 0
        sy = 0
        for i in range(0, len(ts1.data)) :
           sx += (ts1.data[i] - mx) * (ts1.data[i] - mx)
           sy += (ts2.data[i] - my) * (ts2.data[i] - my)

        denom = np.sqrt(sx * sy)

        # Calculate the correlation series
        for delay in range(0, lag):
           sxy = 0
           for i in range(0, len(ts1.data) - lag) :
              j = i + delay
              sxy += (ts1.data[i] - mx) * (ts2.data[j] - my)

           r = sxy / denom
           # print "r(%d) = %f" % (delay, r)
           ra.append(r)
           # r is the correlation coefficient at "delay"
        # end
        LimnologyTimesSeries.display(range(0, lag), ra, "lag", "r coeff")

        if np.max(ra) < 0 :
            return np.min(ra)
        else:
            return np.max(ra)

    @staticmethod
    def display(x, y, xlabel, ylabel):
        fig = plt.figure(facecolor = 'w', edgecolor = 'k')
        ax = fig.add_subplot(111)
        ax.plot(x, y, linewidth = 1.6, color = 'r')
        plt.ylabel(ylabel).set_fontsize(20)
        plt.xlabel(xlabel).set_fontsize(20)
        plt.show()


    @staticmethod
    def corr(ts1, ts2, method = 'pearson', lag = None, average_int = None):
        '''Calculate the correlation between series
           based on pairwise complete observations.

           Uses the Pandas corr function

        :param ts1: original time series
        :param ts2: times series to be correlated with
        :param method: correlation method -- one of
            * pearson -- Standard correlation coefficient
            * kendall -- Kendall Tau correlation coefficient
            * spearman -- Spearman rank correlation coefficient
        :param lag: int -- number of time units shifted ( can be negative)
        :parms average_int: interval to average the data on -- one of
            * day
            * hour
            * minute
            * second
        :returns: float -- the correlation coefficient
        '''
        # The reindex function enables you to align data while filling forward values
        # (getting the "as of" value)
        ts1.reindex(ts2, 'ffill')
        if lag != None:
            ts1.ts = ts1.ts.shift(lag)

        if average_int != None :
            if average_int == 'day':
                ts1.ts = ts1.ts.groupby(lambda date: date.replace(day = 1)).mean()
                ts2.ts = ts2.ts.groupby(lambda date: date.replace(day = 1)).mean()
            if average_int == 'hour':
                ts1.ts = ts1.ts.groupby(lambda date: date.replace(hour = 0)).mean()
                ts2.ts = ts2.ts.groupby(lambda date: date.replace(hour = 0)).mean()
            if average_int == 'minute':
                ts1.ts = ts1.ts.groupby(lambda date: date.replace(minute = 0)).mean()
                ts2.ts = ts2.ts.groupby(lambda date: date.replace(minute = 0)).mean()
            if average_int == 'second':
                ts1.ts = ts1.ts.groupby(lambda date: date.replace(second = 0)).mean()
                ts2.ts = ts2.ts.groupby(lambda date: date.replace(second = 0)).mean()


        return ts1.ts.corr(ts2.ts, method)

    @staticmethod
    def cov(ts1, ts2, lag = None, min_periods = None):
        '''Calculate the correlation between series
           based on pairwise complete observations.

           Uses the Pandas corr function

        :param ts1: original time series
        :param ts2: times series to be correlated with
        :param lag: int -- number of time units shifted ( can be negative)
        :parms min_periods: int -- Minimum number of observations needed to have a valid result
        :returns: float -- the correlation coefficient
        '''
        # The reindex function enables you to align data while filling forward values
        # (getting the "as of" value)
        ts1.reindex(ts2, 'ffill')
        if lag != None:
            ts2.ts = ts2.ts.shift(lag)


        return ts1.ts.cov(ts2.ts, min_periods)


    @staticmethod
    def rolling_correlate(ts1, ts2, window = None, min_periods = None, freq = None, center = False, pairwise = None, how = None):
        '''Calculate the correlation between series
           based on pairwise complete observations.

        :param ts1: original time series
        :param ts2: times series to be correlated with
        :param method: one of
            * pearson -- Standard correlation coefficient
            * kendall -- Kendall Tau correlation coefficient
            * spearman -- Spearman rank correlation coefficient
        :returns: float -- the correlation coefficient
        '''
        # The reindex function enables you to align data while filling forward values
        # (getting the "as of" value)
        ts1.reindex(ts2, 'pad')
        return ts1.ts.rolling_corr(ts2.ts, min_periods, freq, center, pairwise, how)
