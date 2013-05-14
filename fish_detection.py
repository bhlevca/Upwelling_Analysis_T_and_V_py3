import csv
import numpy
import scipy
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import date2num, num2date
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates
import time, os, sys, inspect, locale, math

def fish_setection(filepath):
    sort_Detections(filepath)

def sort_detections(filepath):
    ########################################################
    #
    ########################################################
    startdate = timeint[0]
    enddate = timeint[1]
    dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
    start_num = date2num(dt)
    dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
    end_num = date2num(dt)



    data = read_csv.read_fish_data(filepath)


    [r2, slope, intercept, r_value, p_value, std_err] = stat.rsquared(uia, temp)
    print "R squared = %f, r_value=%f, p_value =%f std_err=%f" % (r2, r_value, p_value, std_err)

    stat.plot_regression(uia, temp, slope = slope, intercept = intercept, point_labels = data[0], \
                          x_label = "UIA ($^oC$ day)", y_label = "Bottom Mean Temperature ($^oC$)", title = "Temperature vs. Upwelling Integrated Anomaly Index", \
                          r_value = r_value, p_value = p_value)

