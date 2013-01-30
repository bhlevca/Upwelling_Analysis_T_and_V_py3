from datetime import datetime
from datetime import timedelta
from matplotlib.dates import seconds
from matplotlib.dates import date2num, num2date
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates
import matplotlib.pyplot as plt
from datetime import datetime
import time

import csv
import numpy


years = matplotlib.dates.YearLocator()   # every year
months = matplotlib.dates.MonthLocator()  # every month
yearsFmt = matplotlib.dates.DateFormatter('%Y')
# every monday
mondays = matplotlib.dates.WeekdayLocator(MONDAY)

#path = '/software/software/scientific/Matlab_files/Helmoltz/Embayments-Exact/Toronto_Harbour'

'''
ifile1 = open(path + '/1115865-Station16-Gate-ML.csv', 'rb')
reader1 = csv.reader(ifile1, delimiter = ',', quotechar = '"')

ifile2 = open(path + '/1115861-Station14-EmbaymentA-ML.csv', "rb")
reader2 = csv.reader(ifile2, delimiter = ',', quotechar = '"')

ofile1 = open(path + '/1115865-Station16-Gate-date.csv', "wb")
writer1 = csv.writer(ofile1, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)

ofile2 = open(path + '/1115861-Station14-EmbaymentA-date.csv', "wb")
writer2 = csv.writer(ofile2, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
'''

'''
path = '/home/bogdan/Documents/UofT/PhD/Research-docs/Data_Files/Toberymory_tides'

#ifile1 = open(path + '/LL3_Harbour_Is_Logger.csv', 'rb')
ifile1 = open(path + '/LL1_Inner_Boat_Passage.csv', 'rb')
reader1 = csv.reader(ifile1, delimiter = ',', quotechar = '"')

#ifile2 = open(path + '/LL2_Outer_Boat_Passage.csv', "rb")
ifile2 = open(path + '/LL4_Cove_Is_Harbour_Logger.csv', "rb")
reader2 = csv.reader(ifile2, delimiter = ',', quotechar = '"')

#ofile1 = open(path + '/LL3.csv', "wb")
ofile1 = open(path + '/LL1.csv', "wb")
writer1 = csv.writer(ofile1, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)

#ofile2 = open(path + '/LL2.csv', "wb")
ofile2 = open(path + '/LL4.csv', "wb")
writer2 = csv.writer(ofile2, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
'''

'''
path = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files_Bogdan/Pressure_loggers_11_sept_2012_test'
ifile1 = open(path + '/1115681-test.csv', 'rb')
reader1 = csv.reader(ifile1, delimiter = '\t', quotechar = '"')
ifile2 = open(path + '/1115683-test.csv', "rb")
reader2 = csv.reader(ifile2, delimiter = '\t', quotechar = '"')
ifile3 = open(path + '/1115685-test.csv', "rb")
reader3 = csv.reader(ifile3, delimiter = '\t', quotechar = '"')

ofile1 = open(path + '/1115681-test_date.csv', "wb")
writer1 = csv.writer(ofile1, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
ofile2 = open(path + '/1115683-test_date.csv', "wb")
writer2 = csv.writer(ofile2, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
ofile3 = open(path + '/1115685-test_date.csv', "wb")
writer3 = csv.writer(ofile3, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
'''

path = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files_Bogdan/Pressure_loggers_11_sept_2012_test'
#ifile1 = open(path + '/1115681-Boat_Passage_Logger_3.csv', 'rb')
#reader1 = csv.reader(ifile1, delimiter = '\t', quotechar = '"')
#ifile2 = open(path + '/1115683-Boat_Passage_Logger_1.csv', "rb")
#reader2 = csv.reader(ifile2, delimiter = '\t', quotechar = '"')
ifile3 = open(path + '/1115685-Boat_Passage_Log.csv', "rb")
reader3 = csv.reader(ifile3, delimiter = '\t', quotechar = '"')

#ofile1 = open(path + '/1115681-Boat_Passage_Logger_3_date.csv', "wb")
#writer1 = csv.writer(ofile1, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
#ofile2 = open(path + '/1115683-Boat_Passage_Logger_1_date.csv', "wb")
#writer2 = csv.writer(ofile2, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
ofile3 = open(path + '/1115685-Boat_Passage_Log_date.csv', "wb")
writer3 = csv.writer(ofile3, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)

def display(title, xlable, ylabel, x, y, colour, legend = None, linewidth = 0.6):

    n = len(x)
    fig = plt.figure(facecolor = 'w', edgecolor = 'k')
    ax = fig.add_subplot(111)
    for i in range(0, n):
        ax.plot(x[i], y[i], linewidth = 0.6, color = colour[i])
    # format the ticks
    formatter = matplotlib.dates.DateFormatter('%Y-%m-%d')
    #formatter = matplotlib.dates.DateFormatter('`%y')
    #ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(formatter)
    #ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%d'))
    ax.xaxis.set_minor_locator(mondays)

    #ax.xaxis.grid(True, 'major')
    ax.xaxis.grid(True, 'minor')
    ax.grid(True)
    ylabel = ylabel
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)
    if legend != None:
        plt.legend(legend)

    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    fig.autofmt_xdate()

    plt.draw()
    return [fig, plt, ax]

def read_stringdatefile(reader):
    rownum = 0
    depth = []
    temp = []
    dateTime = []
    printHeaderVal = False

    for row in reader:
        #skip comment lines
        if len(row) == 0 or row[0][:1] == '#':
            continue

        # Save header row.
        if rownum == 0:
            header = row
        else:
            if printHeaderVal == True:
                colnum = 0

                for col in row:
                    print '%-8s: %s' % (header[colnum], col)
                    colnum += 1
                #end for
            else:
                colnum = 0
                for col in row:
                    #if header[colnum] == "Sensor Depth, meters":
                    if header[colnum] == "Abs Pres kPa":
                        depth.append(str(col))
                    if header[colnum][0:4] == "Temp":
                        temp.append(str(col))

                    #if header[colnum] == "Time, GMT-04:00":
                    if header[colnum] == "Date Time GMT-05:00":
                        dateTime.append(str(col))

                    colnum += 1
                #end for
            #end if/else
        #end if/else            
        rownum += 1

    return [depth, dateTime, temp]

#export to date file 
def write_datefile(writer, depth, dateTime):
    idx = 0
    numdat = []
    prevdt = 0
    prevdepth = depth[0]
    eps = 1.5
    prevtxt = ''
    for row in depth:
        dt = datetime.strptime(dateTime[idx], "%d/%m/%Y %I:%M:%S %p")
        #dt = datetime.strptime(dateTime[idx], "%m/%d/%Y %H:%M")
        dn = date2num(dt)
        if prevdt > dn:
            print "Next value lower!"
        #print  "prevdepth: %s, row: %s" % (prevdepth, row)
        if abs(float(prevdepth) - float(row)) > eps:
            row = prevdepth
        else:
            prevdepth = row
        writer.writerow([dn, row])
        prevdt = dn
        prevtxt = dateTime[idx]
        idx += 1
        numdat.append(dn)
    return numdat

'''
[depth, dateTime, temp] = read_stringdatefile(reader1)
nd = write_datefile(writer1, depth, dateTime)
#plt.plot(nd, linewidth = 0.3, color = 'r')
[depth2, dateTime2, temp2] = read_stringdatefile(reader2)
nd2 = write_datefile(writer2, depth2, dateTime2)
'''

[depth3, dateTime3, temp3] = read_stringdatefile(reader3)
nd3 = write_datefile(writer3, depth3, dateTime3)
legend = ['1115685']
colors = ['r', 'b']
title = '1115685 Pressure logger'
ylabel = "Pressure (kPa)"
xlabel = "Time (s)"
fig, plt3, ax = display(title, xlabel, ylabel, [nd3], [depth3], colors, legend)
ax.plot(nd3, temp3)#, nd3, temp3)
plt3.grid(True)
plt3.show()
'''
title = 'Pressure logger test for 2 depths'
legend = ['1115681', '1115683']  #, '1115685'])
colors = ['r', 'b']
ylabel = "Pressure (kPa)"
xlabel = "Time (s)"
fig, plt2, ax = display(title, xlabel, ylabel, [nd, nd2], [depth, depth2], colors, legend)
ax.plot(nd, temp, nd2, temp2)#, nd3, temp3)
plt2.grid(True)
plt2.show()
'''

print "Done!"