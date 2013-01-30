from matplotlib.dates import date2num
import matplotlib.pyplot as plt
from datetime import datetime
import time, os
import csv
import numpy


path = '/home/bogdan/Documents'
path_out = '/home/bogdan/Documents'
path = '/software/software/scientific/Matlab_files/Helmoltz/Embayments-Exact/LakeOntario-data'
path_out = '/software/software/scientific/Matlab_files/Helmoltz/Embayments-Exact/LakeOntario-data'

#export to date file 
def write_datefile(writer, depth, dateTime):
    idx = 0
    numdat = []
    prev = 0
    prevtxt = ''
    for row in depth:
        #dt = datetime.strptime(dateTime[idx], "%m/%d/%y %I:%M:%S %p")
        #dt = datetime.strptime(dateTime[idx], "%m/%d/%Y %H:%M:%S")
        dt = datetime.strptime(dateTime[idx], "%Y/%m/%d %H:%M")
        dn = date2num(dt)
        if prev > dn:
            print "Next value lower!"
        writer.writerow([dateTime[idx], dn, row])
        prev = dn
        prevtxt = dateTime[idx]
        idx += 1
        numdat.append(dn)
    return numdat

def read_stringdatefile(reader):
    rownum = 0
    temp = []
    dateTime = []
    printHeaderVal = False

    for row in reader:
        #skip comment lines
        if len(row) == 0 or row[0][:1] == '@':
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
            else:
                colnum = 0
                for col in row:
                    #if len(header[colnum]) > 4 and header[colnum][:4] == "Temp":
                    if len(header[colnum]) > 4 and header[colnum][:4] == "Leve":
                        temp.append(str(col))

                    if header[colnum] == "Date Time, GMT-04:00":
                        dateTime.append(str(col))

                    colnum += 1

        rownum += 1

    return [temp, dateTime]


def read_files():
    dirList = os.listdir(path)
    for fname in dirList:
        read_file(fname)

def read_file(fname, fout = None):
    ifile = open(path + '/' + fname, 'rb')
    reader = csv.reader(ifile, delimiter = ',', quotechar = '"')
    [temp, dateTime] = read_stringdatefile(reader)

    if fout == None:
        fout = fname

    ofile = open(path_out + '/' + fout, "wb")
    writer = csv.writer(ofile, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
    write_datefile(writer, temp, dateTime)
    ifile.close()
    ofile.close()


#read_files()
#read_file("LO_Burlington_may2012.csv", "LO_Burlington_may2012_date.csv")
read_file("LO_Burlington-JAN-DEC-2011_slev.csv", "LO_Burlington-JAN-DEC-2011_date.csv")

print "Done!"
