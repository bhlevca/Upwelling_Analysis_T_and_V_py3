import csv
import numpy

path = '/software/software/scientific/Matlab_files/Helmoltz/Embayments-Exact/Toronto_Harbour'

ifile = open(path + '/aug-sept_2011.csv', 'rb')
reader = csv.reader(ifile, delimiter = ',', quotechar = '"')

ofile = open(path + '/atmPress_august2011.csv', "wb")
writer = csv.writer(ofile, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)

ofile2 = open(path + '/atmPress_august2011_interp.csv', "wb")
writer2 = csv.writer(ofile2, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)

rownum = 0
atmPresHour = []
atmTempHour = []
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
        else:
            colnum = 0
            for col in row:
                if header[colnum] == "Date/Time":
                    dateTime.append(str(col))
                if header[colnum] == "Stn Press (kPa)":
                    atmPresHour.append(str(col))
                if len(header[colnum]) > 4 and header[colnum][:4] == "Temp":
                     atmTempHour.append(str(col))
                colnum += 1

    #write rows 
    rownum += 1
    idx = 0

    for row in atmPresHour:
        writer.writerow([dateTime[idx], row, atmTempHour[idx]])
        idx += 1

#interpolated pressure values        
atmPresInterp = numpy.interp(range(0, 30 * 724), range(0, 724 * 30, 30), atmPresHour)
atmTempInterp = numpy.interp(range(0, 30 * 724), range(0, 724 * 30, 30), atmTempHour)

idx = 0;
for row in atmPresInterp:
    rowformatted = "% .3f, %.3%" % (row, atmTempInterp)
    writer2.writerow([rowformatted])


print "Done!"
ifile.close()
ofile.close()
