import csv
import numpy
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import date2num, num2date
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates
import time, os, datetime, sys
import display_data
import smooth
import readTempHoboFiles

windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
window_6hour = "window_6hour"  # 30 * 6 for a 2 minute sampling
window_hour = "window_hour"  # 30
window_halfhour = "window_1/2hour"  # 30
window_day = "window_day"  # 30 * 24
window_half_day = "window_half_day"  # 30 * 12
window_3days = "window_3days"  # 3 * 30 * 24
window_7days = "window_7days"  # 7 * 30 * 24

class Read_Temp_Data_2013(object):

    def __init__(self, path, fnames, startdate, enddate):
       self.path = path
       self.fnames = fnames
       self.startDate = startdate
       self.endDate = enddate

    def readData(self):
        alldepths = numpy.zeros(len(self.fnames), dtype = numpy.ndarray)
        i = 0
        for fname in self.fnames:

            dateTime, temp, results = readTempHoboFiles.get_data_from_file(fname,
                                                                           window_hour, windows[1],
                                                                           timeinterv = [self.startDate, self.endDate],
                                                                           rpath = self.path)
            alldepths[i] = numpy.array(temp)
            i += 1

        # do the average
        temp = numpy.mean(alldepths, axis = 0)

        return [dateTime, temp]

class Read_ADCP_WrittenData(object):

    def __init__(self, path, fname, startdate, enddate, bin_no):
       self.path = path
       self.fname = fname
       self.startDate = startdate
       self.endDate = enddate
       self.binNo = bin_no


    def read_bin_data(self, reader, bin):
        rownum = 0
        temp = []
        dateTime = []

        data_row = bin + 1
        for row in reader:
            try:
                time = float(row[0])
                if self.startDate != None:
                    if time < self.startDate or time > self.endDate:
                        continue
                # end if
                dateTime.append(time)
                temp.append(float(row[data_row]))

            except:
                print "Error: read_bin_data"

        return [dateTime, temp]

    def get_data_from_file(self, span, window):

        for bin in self.binNo:
            if os.path.isdir(self.path + "/" + self.fname) == False:
                ifile = open(self.path + '/' + self.fname, 'rb')
            else:
                return
            # end if
            i = 0

            reader = csv.reader(ifile, delimiter = ',', quotechar = '"')
            allbins = numpy.zeros(len(self.binNo), dtype = numpy.ndarray)

            [dateTime, temp] = self.read_bin_data(reader, bin)
            allbins[i] = numpy.array(temp)
            i += 1
            ifile.close()
        # end for
        # do the average
        temp = numpy.mean(allbins, axis = 0)

        try:
            if span != None:
                # check if span is correct
                dt = dateTime[2] - dateTime[1]  # usually days
                if span == "window_6hour":  # 30 * 6 for a 2 minute sampling
                    nspan = 6. / (dt * 24)
                elif span == "window_hour":  # 30 for a 2 minute sampling
                    nspan = 1. / (dt * 24)
                elif span == "window_1/2hour":  # 30 for a 2 minute sampling
                    nspan = 0.5 / (dt * 24)
                elif span == "window_day":  # 30 * 24 for a 2 minute sampling
                    nspan = 24. / (dt * 24)
                elif span == "window_half_day":  # 30 * 12 for a 2 minute sampling
                    nspan = 12. / (dt * 24)
                elif span == "window_3days":  # 3 * 30 * 24 for a 2 minute sampling
                    nspan = 24. * 3 / (dt * 24)
                elif span == "window_7days":  # 7* 30 * 24 for a 2 minute sampling
                    nspan = 24. * 7 / (dt * 24)
                else:
                    print "Error, window span not defined"
                    return
                results = smooth.smoothfit(dateTime, temp, nspan, window)
            else:
                results = {}
                results['smoothed'] = temp
        except:
            print "Date not available"
            ifile.close()
            return [None, None, None]


        return [dateTime, temp, results['smoothed']]
    # end get_data_from_file

    def readData(self):
        # dateTime, temp, results = self.get_data_from_file(window_hour, windows[1])
        dateTime, temp, results = self.get_data_from_file(None, windows[1])
        return [dateTime, temp]
