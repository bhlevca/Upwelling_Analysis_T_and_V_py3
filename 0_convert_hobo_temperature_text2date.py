from matplotlib.dates import date2num
import matplotlib.pyplot as plt
from datetime import datetime
import time, os, locale
import csv
import numpy

path = '/home/bogdan/Documents/UofT/PhD/Research-docs/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2011/csv'
path_out = '/home/bogdan/Documents/UofT/PhD/Research-docs/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2011/csv_processed'
path = '/home/bogdan/Documents'
path_out = '/home/bogdan/Documents'
path = '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE-Apr-May_2012-Thermistor_chain/csv'
path_out = '/home/bogdan/Documents/UofT/PhD/Data_Files/MOE-Apr-May_2012-Thermistor_chain/csv_processed'
path = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/Exports'
path_out = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Nov2012/csv_processed'
path = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Apr2012-Tor_Harb/Exports'
path_out = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo_Files-Nick_Lapointe/Hobo_Files-Apr2012-Tor_Harb/csv_processed'
path = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo-TRCA/2012'
path_out = '/home/bogdan/Documents/UofT/PhD/Data_Files/Hobo-TRCA/2012/csv_processed'
# export to date file
def write_datefile(writer, depth, dateTime):
    idx = 0
    numdat = []
    prev = 0
    prevtxt = ''
    # print "len(depth) :%d, len(dateTime):%d" % (len(depth), len(dateTime))
    for row in depth:
        strg = dateTime[idx]
        # strg = '20/04/2012 12:00:00 AM'
        # This settingis needed to deal with the loacale usingAM/PM Python bug
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        # dt = datetime.strptime(strg, "%d/%m/%Y %I:%M:%S %p")

        # Nick Lapointe Format
        # dt = datetime.strptime(strg, "%m/%d/%y %I:%M:%S %p")

        # dt = datetime.strptime(dateTime[idx], "%d/%m/%y %I:%M:%S %p")

        # dt = datetime.strptime(dateTime[idx], "%m/%d/%y %H:%M:%S")

        # TRCA Format
        try:
            dt = datetime.strptime(dateTime[idx], "%m/%d/%Y %H:%M")
        except :
            continue

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

        # skip firs line
        if rownum == 0:
            rownum += 1
            continue

        # skip comment lines
        if len(row) == 0 or row[0][:1] == '@' :
            continue

        # Save header row.
        strg = row[0]
        print "strg :%s" % strg
        # if rownum == 1 and strg[:4] != 'Plot') or rownum == 1:
        if strg == "":
            continue
        if rownum == 1 or strg[0] == '#':
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
                    if len(header[colnum]) > 4 and header[colnum][:4] == "Temp":
                    # if len(header[colnum]) > 4 and header[colnum][:4] == "Leve":
                        temp.append(str(col))

                    if header[colnum][:9] == "Date Time":
                        dateTime.append(str(col))

                    colnum += 1

        rownum += 1

    return [temp, dateTime]


def read_files():
    dirList = os.listdir(path)
    for fname in dirList:
        print "Fname %s" % fname
        if os.path.isdir(path + "/" + fname) == False:
            read_file(fname)

def read_file(fname, fout = None):
    ifile = open(path + '/' + fname, 'rb')
    reader = csv.reader(ifile, delimiter = ',', quotechar = '"')
    print "Converting file: %s" % fname
    [temp, dateTime] = read_stringdatefile(reader)

    if fout == None:
        fout = fname

    ofile = open(path_out + '/' + fout, "wb")
    writer = csv.writer(ofile, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
    write_datefile(writer, temp, dateTime)
    ifile.close()
    ofile.close()


if __name__ == '__main__':
    read_files()
    # read_file("LO_Burlington_may2012.csv", "LO_Burlington_may2012_date.csv")
    print "Done!"
