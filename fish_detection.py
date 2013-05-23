import csv
import numpy
import scipy
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import date2num, num2date
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates
import time, os, sys, inspect, locale, math
import utils.read_csv as read_csv
import utils.autovivification as ndict

def fish_detection(filepath, timeint):
    dict = sort_detections(filepath, timeint)

    # detailed statistics
    values = dict.values()
    keys = dict.keys()
    for i in range(0, len(keys)):
        value = values[i]
        key = value.keys()
        vals = value.values()
        for j in range (0, len(value)):
            print "%s: (%s =  %d)" % (keys[i], key[j], vals[j])

    # print the number of distinct fish that roamed in the receiver area
    print "\n-------------------------------------------------------"
    print " Number of individual fish detections at each stations"
    print "-------------------------------------------------------"

    for i in range(0, len(keys)):
        value = values[i]
        key = value.keys()
        vals = value.values()
        print "%s: #det= %d)" % (keys[i], len(value))


#===============================================================================
#     [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, temp)
#     print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)
#
#     stat.plot_regression(uia, temp, slope = slope, intercept = intercept, point_labels = data[0], \
#                           x_label = "UIA ($^oC$ day)", y_label = "Bottom Mean Temperature ($^oC$)", title = "Temperature vs. Upwelling Integrated Anomaly Index", \
#                           r_value = r_value, p_value = p_value)
#===============================================================================

def sort_detections(filepath, timeint):
    ########################################################
    #
    ########################################################
    startdate = timeint[0]
    enddate = timeint[1]
    dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
    start_num = date2num(dt)
    dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
    end_num = date2num(dt)

    ifname = "/home/bogdan/Documents/UofT/PhD/Data_Files/Fish-data-Apr-Dec-2012/NumDate-May-Nov2012.csv"

    [dateTime, TransmitterName, SensorValue, SensorUnit, StationName] = read_csv.read_fish_data(ifname, [start_num, end_num])

    locdict = ndict.AutoVivification()

    for i in range(0, len(dateTime)):
        #
        # Parse the name of the transmitter, usually FishType Number (SensorType)
        # Should be converted to FishTypeNumber
        # Some do not have Sensor Type, some have one ans some have both.
        #
        # To make it count only one fish we will suse as a dictionary name only FishType+Number

        # split the string
        strarr = TransmitterName[i].split(" ", 3)
        Tn = strarr[0] + strarr[1]

        try:
            locdict[StationName[i]][Tn] = locdict[StationName[i]][Tn] + 1
        except:
            locdict[StationName[i]][Tn] = 1
            print "Added station : %s, Fish: %s]" % (StationName[i], Tn)


    return locdict
