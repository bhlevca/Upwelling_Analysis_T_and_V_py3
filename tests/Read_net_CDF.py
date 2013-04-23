from scipy.io import netcdf
from pyhdf import SD  # HDF4
import h5py  # HDF5
import numpy as np
import matplotlib.pyplot as plt
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
    except HDF4Error, msg:
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



        cldtot = f.select('cldtot')
        print cldtot[:]
        time = f.select('time')
        print time[:]
        lat = f.select('latitude')
        print lat[:]
        lon = f.select('longitude')
        print lon[:]
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


def print_hdf5_file_structure(file_name) :
    """Prints the HDF5 file structure"""
    file = h5py.File(file_name, 'r')  # open read-only
    item = file  # ["/Configure:0000/Run:0000"]
    print_hdf5_item_structure(item)
    file.close()

def print_hdf5_item_structure(g, offset = '    ') :
    """Prints the input file/group/dataset (g) name and begin iterations on its content"""
    if   isinstance(g, h5py.File) :
        print g.file, '(File)', g.name

    elif isinstance(g, h5py.Dataset) :
        print '(Dataset)', g.name, '    len =', g.shape  # , g.dtype

    elif isinstance(g, h5py.Group) :
        print '(Group)', g.name

    else :
        print 'WORNING: UNKNOWN ITEM IN HDF5 FILE', g.name
        sys.exit ("EXECUTION IS TERMINATED")

    if isinstance(g, h5py.File) or isinstance(g, h5py.Group) :
        for key, val in dict(g).iteritems() :
            subg = val
            print offset, key,  # ,"   ", subg.name #, val, subg.len(), type(subg),
            print_hdf5_item_structure(subg, offset + '    ')


def read_hdf5(FILE_NAME):
    '''
    item.id      # for example: <GroupID [1] (U) 33554473>
    item.ref     # for example: <HDF5 object reference>
    item.parent  # for example: <HDF5 group "/Configure:0000/Run:0000/CalibCycle:0000" (5 members)>
    item.file    # for example: <HDF5 file "cxi80410-r0587.h5" (mode r, 3.5G)>
    item.name    # for example: /Configure:0000/Run:0000/CalibCycle:0000/Camera::FrameV1

    For Dataset
    ds.dtype     # for example: ('seconds', '<u4'), ('nanoseconds', '<u4')]
    ds.shape     # for example: (1186,)
    ds.value     # for example: (1297610252L, 482193420L)
    '''

    file = h5py.File(hdf5_file_name, 'r')
    item = file[item_name]

    isFile = isinstance(item, h5py.File)
    isGroup = isinstance(item, h5py.Group)
    isDataset = isinstance(item, h5py.Dataset)


if __name__ == '__main__':
    path = "/home/bogdan/Documents/UofT/PhD/Data_Files/CloudData/Toronto-Jan-Dec-2012/HDF"
    # read_netcdf('/home/bogdan/Documents/UofT/PhD/Data_Files/CloudData/Toronto-Mar-Nov-2012/MERRA300.prod.assim.tavgM_2d_rad_Nx.201203.SUB.nc')
    fn = '/home/bogdan/Documents/UofT/PhD/Data_Files/CloudData/Toronto-Jan-Dec-2012/HDF/MERRA300.prod.assim.tavg1_2d_rad_Nx.20120101.SUB.hdf'
    [f, dsets, attr] = read_hdf_datasets_info(fn)
    read_hdf_datasets(f, dsets, attr)
    arr = read_hdf_variable(fn, 'cldtot', 0, 1, [0, 23])
    print arr
    # read_hdf('/home/bogdan/Documents/UofT/PhD/Data_Files/CloudData/Toronto-Jan-Dec-2012/HDF/MERRA300.prod.assim.tavg1_2d_rad_Nx.20120101.SUB.hdf', 'cldtot')
