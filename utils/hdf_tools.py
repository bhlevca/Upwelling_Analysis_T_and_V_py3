from scipy.io import netcdf
from pyhdf import SD  # HDF4
import h5py  # HDF5
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import date2num, num2date
from matplotlib.dates import MONDAY, SATURDAY
import matplotlib.dates
import time, os
import sys

printf = sys.stdout.write

typeTab = {
            SD.SDC.CHAR:    'CHAR',
            SD.SDC.CHAR8:   'CHAR8',
            SD.SDC.UCHAR8:  'UCHAR8',
            SD.SDC.INT8:    'INT8',
            SD.SDC.UINT8:   'UINT8',
            SD.SDC.INT16:   'INT16',
            SD.SDC.UINT16:  'UINT16',
            SD.SDC.INT32:   'INT32',
            SD.SDC.UINT32:  'UINT32',
            SD.SDC.FLOAT32: 'FLOAT32',
            SD.SDC.FLOAT64: 'FLOAT64'
        }


'''
http://disc.sci.gsfc.nasa.gov/daac-bin/FTPSubset.pl => IAU 2d surfacea and TOA radiation fluxes (tavg1_2d_rad_Nx)

EMIS = Surface emissivity
TS = Surface temperature
ALBEDO = Surface albedo
ALBNIRDF = Diffuse beam NIR surface albedo
ALBNIRDR = Direct beam NIR surface albedo
ALBVISDF = Diffuse beam VIS-UV surface albedo
ALBVISDR = Direct beam VIS-UV surface albedo
LWGEM = Emitted longwave at the surface
LWGAB = Absorbed longwave at the surface
LWGABCLR = Absorbed longwave at the surface with no clouds
LWGABCLRCLN = Absorbed longwave at the surface with no clouds or aerosol
LWGNT = Net downward longwave flux at the surface
LWGNTCLR = Net downward longwave flux at the surface for cloud-free sky
LWGNTCLRCLN = Net downward longwave flux at the surface for clear sky
LWTUP = Upward longwave flux at top of atmosphere (TOA)
LWTUPCLR = Upward longwave flux at TOA assuming clear sky
LWTUPCLRCLN = Upward longwave flux at TOA assuming clear clean sky
SWTDN = TOA incident shortwave flux
SWGDN = Surface incident shortwave flux
SWGDNCLR = Surface incident shortwave flux assuming clear sky
SWGNT = Surface net downward shortwave flux
SWGNTCLR = Surface net downward shortwave flux assuming clear sky
SWGNTCLN = Surface net downward shortwave flux assuming clean sky
SWGNTCLRCLN = Surface net downward shortwave flux assuming clear clean sky
SWTNT = TOA net downward shortwave flux
SWTNTCLR = TOA net downward shortwave flux assuming clear sky
SWTNTCLN = TOA net downward shortwave flux assuming clean sky
SWTNTCLRCLN = TOA net downward shortwave flux assuming clear clean sky
TAUHGH = Optical thickness of high clouds
TAULOW = Optical thickness of low clouds
TAUMID = Optical thickness of mid-level clouds
TAUTOT = Optical thickness of all clouds
CLDHGH = High-level (above 400 hPa) cloud fraction
CLDLOW = Low-level (1000-700 hPa) cloud fraction
CLDMID = Mid-level (700-400 hPa) cloud fraction
CLDTOT = Total cloud fraction
'''

def read_netcdf(filename):
    f = netcdf.netcdf_file(filename, 'r')
    for v in f.variables:
        print v
    # print f.history
    print "----------------------\n"

    time = f.variables['time'][:]

    for v in f.variables:
            print v ,
    print


    cldtot = f.variables['cldtot'][:]
    x = range(0, len(cldtot))
    plt.plot(x, cldtot)
    plt.show()
    print
    print "----------------------\n"
    print time.units
    print time.shape
    print time[:]
    f.close()


def eol(n = 1):
    printf("%s" % chr(10) * n)

def read_hdf_datasets_info(filename):
    try:
        f = SD.SD(filename, SD.SDC.READ)


        # At this point, Dataset1 is an instance of the SD class
        print "Dataset's type: ", type(f)
        # output: <class 'SD.SD'>

        # Dataset1.attributes() is a dictionary
        print "Type of Dataset's attributes: ", type(f.attributes())
        attr = f.attributes(full = 1)
        # output: <type 'dict'>

        # So is Dataset.datasets()
        print "Type of Dataset's datasets: ", type(f.datasets())
        print f.datasets()
        dsets = f.datasets()
        # output: <type 'dict'>


        print "Dataset.attributes' keys: ", f.attributes().keys()
        attNames = attr.keys()
        # output: ['HDFEOSVersion', 'act_specific', 'StructMetadata.0',...

        print "Dataset.attributes' values: ", f.attributes().values()
        attValues = attr.values()
        # output: ['HDFEOSVersion', 'act_specific', 'StructMetadata.0',...
    except SD.HDF4Error, msg:
        print "HDF4Error", msg

    return [f, dsets, attr]



def read_hdf_datasets(f, dsets, attr):
    try:
        # Dataset
        if len(dsets) > 0:
            printf("Datasets (idx:index #, na:# attributes, cv:coord var)"); eol(2)
            printf("  name                 idx type    na cv dimension(s)"); eol()
            printf("  -------------------- --- ------- -- -- ------------"); eol()
            # Get list of dataset names and sort them lexically
            dsNames = dsets.keys()
            dsNames.sort()
            for name in dsNames:
                # Get dataset instance
                ds = f.select(name)
                # Retrieve the dictionary of dataset attributes so as
                # to display their number
                vAttr = ds.attributes()
                t = dsets[name]
                # t[0] is a tuple of dimension names
                # t[1] is a tuple of dimension lengths
                # t[2] is the dataset type
                # t[3] is the dataset index number
                printf("  %-20s %3d %-7s %2d %-2s " %
                       (name, t[3], typeTab[t[2]], len(vAttr),
                        ds.iscoordvar() and 'X' or ''))
                # Display dimension info.
                n = 0
                for d in t[0]:
                    printf("%s%s(%d)" % (n > 0 and ', ' or '', d, t[1][n]))
                    n += 1
                    eol()
            eol()

        # Dataset info.
        dsNames = []  # in case len(dsets) == 0
        if len(dsNames) > 0:
            printf("DATASET INFO"); eol()
            printf("-------------"); eol(2)
            for name in dsNames:
                # Access the dataset
                dsObj = f.select(name)
                # Get dataset attribute dictionnary
                dsAttr = dsObj.attributes(full = 1)
                if len(dsAttr) > 0:
                    printf("%s attributes" % name); eol(2)
                    printf("  name                 idx type    len value"); eol()
                    printf("  -------------------- --- ------- --- -----"); eol()
                    # Get the list of attribute names and sort them alphabetically.
                    attNames = dsAttr.keys()
                    attNames.sort()
                    for nm in attNames:
                        t = dsAttr[nm]
                        # t[0] is the attribute value
                        # t[1] is the attribute index number
                        # t[2] is the attribute type
                        # t[3] is the attribute length
                        printf("  %-20s %3d %-7s %3d %s" %
                               (nm, t[1], typeTab[t[2]], t[3], t[0])); eol()
                    eol()

                # Get dataset dimension dictionnary
                dsDim = dsObj.dimensions(full = 1)
                if len(dsDim) > 0:
                    printf ("%s dimensions" % name); eol(2)
                    printf("  name                 idx len   unl type    natt");eol()
                    printf("  -------------------- --- ----- --- ------- ----");eol()
                    # Get the list of dimension names and sort them alphabetically.
                    dimNames = dsDim.keys()
                    dimNames.sort()
                    for nm in dimNames:
                        t = dsDim[nm]
                        # t[0] is the dimension length
                        # t[1] is the dimension index number
                        # t[2] is 1 if the dimension is unlimited, 0 if not
                        # t[3] is the the dimension scale type, 0 if no scale
                        # t[4] is the number of attributes
                        printf("  %-20s %3d %5d  %s  %-7s %4d" %
                               (nm, t[1], t[0], t[2] and "X" or " ", t[3] and typeTab[t[3]] or "", t[4])); eol()
                    eol()


        # Global attribute table.
        if len(attr) > 0:
            printf("File attributes"); eol(2)
            printf("  name                 idx type    len value"); eol()
            printf("  -------------------- --- ------- --- -----"); eol()
            # Get list of attribute names and sort them lexically
            attNames = attr.keys()
            attNames.sort()
            for name in attNames:
                t = attr[name]
                # t[0] is the attribute value
                # t[1] is the attribute index number
                # t[2] is the attribute type
                # t[3] is the attribute length
                printf("  %-20s %3d %-7s %3d %s" % (name, t[1], typeTab[t[2]], t[3], t[0])); eol()
            eol()

    except SD.HDF4Error, msg:
        print "HDF4Error", msg

def read_hdf_variable(filename, varname, ix, iy, timeidx):
    try:
        f = SD.SD(filename, SD.SDC.READ)
        dsets = f.datasets()
        var = f.select(varname)
        l = timeidx[1] - timeidx[0] + 1
        vararr = np.zeros(l)

        for t in range(0, l):
            vararr[t] = var[t, ix, iy]
        return vararr

    except SD.HDF4Error, msg:
        print "HDF4Error", msg

def convert_to_filename(startdate, enddate):
    filename_1 = "MERRA300.prod.assim.tavg1_2d_rad_Nx."
    filename_2 = ".SUB.hdf"

    st_year = "20" + startdate[:2] + startdate[3:5] + startdate[6:8]
    end_year = "20" + enddate[:2] + enddate[3:5] + enddate[6:8]
    stfilenm = filename_1 + st_year + filename_2
    endfilenm = filename_1 + end_year + filename_2
    return [stfilenm, endfilenm]

def read_hdf_dir(dirname, var, ix, iy, timeidx, startdate, enddate):


    # try this
    # dirList = os.listdir(dirname)
    # or
    # Separate directories from files
    base, dirs, files = iter(os.walk(dirname)).next()
    sorted_files = sorted(files, key = lambda x: x.split('.')[4])  # the fourth group after the 3rd dot

    dt = datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
    start_num = date2num(dt)
    dt = datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
    end_num = date2num(dt)
    [startfn, endfn] = convert_to_filename(startdate, enddate)
    l = timeidx[1] - timeidx[0] + 1

    dateTimeArr = np.zeros(0, dtype = np.ndarray)
    resultsArr = np.zeros(0, dtype = np.ndarray)

    loop = False
    end = False
    days = 0
    for fname in sorted_files :
        if fname != startfn and loop == False:
            continue
        else:
            loop = True
            days += 1

        if fname == endfn:
            end = True

        res = read_hdf_variable(dirname + "/" + fname, var, ix, iy, timeidx)
        resultsArr = np.append(resultsArr, res)
        sttm = start_num + days - 1
        entm = start_num + days
        timearr = np.linspace(sttm, entm, num = 24)
        dateTimeArr = np.append(dateTimeArr, timearr)
        if end == True:
            return dateTimeArr, resultsArr

if __name__ == '__main__':
    path = "/home/bogdan/Documents/UofT/PhD/Data_Files/CloudData/Toronto-Jan-Dec-2012/HDF"
    # read_netcdf('/home/bogdan/Documents/UofT/PhD/Data_Files/CloudData/Toronto-Mar-Nov-2012/MERRA300.prod.assim.tavgM_2d_rad_Nx.201203.SUB.nc')
    fn = '/home/bogdan/Documents/UofT/PhD/Data_Files/CloudData/Toronto-Jan-Dec-2012/HDF/MERRA300.prod.assim.tavg1_2d_rad_Nx.20120101.SUB.hdf'
    [f, dsets, attr] = read_hdf_datasets_info(fn)
    read_hdf_datasets(f, dsets, attr)
    arr = read_hdf_variable(fn, 'cldtot', 0, 1, [0, 23])
    print arr

    startdate = '12/07/19 00:00:00'
    enddate = '12/10/24 00:00:00'
    var = 'lwgnt'
    ix = 0
    iy = 1
    timeidx = [0, 23]
    dateTime, results = read_hdf_dir(path, var, ix, iy, timeidx, startdate, enddate)

