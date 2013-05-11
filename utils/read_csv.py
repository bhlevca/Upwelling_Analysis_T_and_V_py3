import csv
import numpy as np

def read_csv(fname, startrow, columns):

    ifile = open(fname, 'rb')
    reader = csv.reader(ifile, delimiter = ',', quotechar = '"')
    rownum = 0

    data = np.zeros(len(columns), dtype = np.ndarray)
    for i in range(0, len(data)):
        data[i] = []

    for row in reader:
        cidx = 0
        i = 0
        try:
            if rownum >= startrow:
                for col in row:
                    if i in columns:
                        data[cidx].append(float(col))
                        cidx += 1
                    i += 1
        except Exception as e:
            print "Error %s" % e

        rownum += 1
    # end for row

    ifile.close()
    for i in range(0, len(data)):
        data[i] = np.array(data[i])
    return data
