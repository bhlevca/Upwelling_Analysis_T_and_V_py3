import csv
import numpy as np
import time, os, locale
from matplotlib.dates import date2num
import matplotlib.pyplot as plt
from datetime import datetime
import time, os, locale

def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

def read_instr_fish_data(reader):
    rownum = 0
    dateTime = []
    TransmitterName = []
    SensorValue = []
    SensorUnit = []
    StationName = []

    printHeaderVal = False

    for row in reader:
        # skip first line
        if rownum == 0:
            header = row
            rownum += 1
            continue

        # skip comment lines
        if len(row) == 0 or row[0][:1] == '@' :
            continue


        if printHeaderVal == True:
            colnum = 0

            for col in row:
                print '%-8s: %s' % (header[colnum], col)
                colnum += 1
        else:
            colnum = 0
            # Date and Time (UTC),Receiver,Transmitter,Transmitter Name,Transmitter Serial,Sensor Value,Sensor Unit,Station Name,Latitude,Longitude
            for col in row:
                if "Date" in header[colnum]:
                    dateTime.append(str(col))
                    print "date: %s" % col
                elif header[colnum] == "Transmitter Name":
                    TransmitterName.append(str(col))
                elif header[colnum] == "Sensor Value":
                    SensorValue.append(str(col))
                elif header[colnum] == "Sensor Unit":
                    SensorUnit.append(str(col))
                elif header[colnum] == "Station Name":
                    StationName.append(str(col))

                colnum += 1

        rownum += 1

    print "Reading End!"
    return [dateTime, TransmitterName, SensorValue, SensorUnit, StationName]

def write_converted_date_fish_data(writer, dateTime, TransmitterName, SensorValue, SensorUnit, StationName):
    idx = 0
    numdat = []
    prev = 0
    prevtxt = ''
    # print "len(depth) :%d, len(dateTime):%d" % (len(depth), len(dateTime))
    for row in dateTime:

        # print "strg :%s" % row
        # strg = '20/04/2012 12:00:00 AM'
        # This settingis needed to deal with the loacale usingAM/PM Python bug
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        # dt = datetime.strptime(strg, "%d/%m/%Y %I:%M:%S %p")
        # Nick Lapointe Format
        # dt = datetime.strptime(strg, "%m/%d/%y %I:%M:%S %p")
        # dt = datetime.strptime(dateTime[idx], "%d/%m/%y %I:%M:%S %p")
        # dt = datetime.strptime(dateTime[idx], "%m/%d/%y %H:%M:%S")
        # TRCA Format
        # dt = datetime.strptime(dateTime[idx], "%m/%d/%Y %H:%M")
        try:
            # 2012-04-16 17:27:40
            dt = datetime.strptime(dateTime[idx], "%Y-%m-%d %H:%M:%S")
        except :
            continue

        dn = date2num(dt)
        if prev > dn:
            print "Next value lower!"
        print "Write: %s, %f %s %s %s %s " % (dateTime[idx], dn, TransmitterName[idx], SensorValue[idx], SensorUnit[idx], StationName[idx])
        writer.writerow([dateTime[idx], dn, TransmitterName[idx], SensorValue[idx], SensorUnit[idx], StationName[idx]])
        prev = dn
        prevtxt = dateTime[idx]
        idx += 1
    print "Writing End!"

def convert_to_numeric_date (ifname, ofname):
    ifile = open(ifname, 'rb')
    reader = csv.reader(ifile, delimiter = ',', quotechar = '"')
    print "reading file: %s" % ifname
    [dateTime, TransmitterName, SensorValue, SensorUnit, StationName] = read_instr_fish_data(reader)

    print "writing file: %s" % ofname

    ofile = open(ofname, "wb")
    writer = csv.writer(ofile, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
    write_converted_date_fish_data(writer, dateTime, TransmitterName, SensorValue, SensorUnit, StationName)
    ifile.close()
    ofile.close()



def read_fish_data(reader, timeinterv = None):
    rownum = 0

    dateTime = []
    TransmitterName = []
    SensorValue = []
    SensorUnit = []
    StationName = []

    printHeaderVal = False

    if timeinterv != None:
        startt = timeinterv[0]
        endt = timeinterv[1]


    for row in reader:
        try:
            time = float(row[1])
            if timeinterv != None:
                if time < startt or time > endt:
                    continue

            dateTime.append(time)
            if (row[2] == ''):
                temp.append(float(1))
            else:
                temp.append(float(row[2]))
            # end if
        except:
            pass
    return [dateTime, temp]

def read_csv(fname, startrow, columns):

    ifile = open(fname, 'rb')
    reader = csv.reader(ifile, delimiter = ',', quotechar = '"')
    rownum = 0

    data = np.zeros(len(columns), dtype = np.ndarray)
    for i in range(0, len(data)):
        data[i] = []

    for row in reader:
        # cidx = 0
        i = 0
        try:
            if rownum >= startrow:
                tempdata = []
                for col in row:
                    if i in columns:
                        tempdata.append(col)
                        # data[cidx].append(col)
                        # cidx += 1
                    i += 1
                to_add = True
                for j in range(0, len(tempdata)):
                    if not tempdata[j]:
                        to_add = False
                # end for
                if to_add:
                    for cidx in range(0, len(tempdata)):
                        data[cidx].append(tempdata[cidx])

                # if all are full then push it to the data array
        except Exception as e:
            print "Error %s" % e

        rownum += 1
    # end for row

    ifile.close()
    for i in range(0, len(data)):
        data[i] = np.array(data[i])
        if isfloat(data[i][0]):
            data[i] = data[i].astype(np.float)

    return data


if __name__ == "__main__":
    strg = "2012-04-16 17:27:40"
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    dt = datetime.strptime(strg, "%Y-%m-%d %H:%M:%S")
    print dt

    ifname = "/home/bogdan/Documents/UofT/PhD/Data_Files/Fish-data-Apr-Dec-2012/April-Dec2012.csv"
    ofname = "/home/bogdan/Documents/UofT/PhD/Data_Files/Fish-data-Apr-Dec-2012/NumDate-May-Nov2012.csv"
    convert_to_numeric_date (ifname, ofname)
