import datetime
import matplotlib.dates as dates
import numpy, scipy
import rdradcp.writebins as writebins


from rdradcp.readRawBinADCP import readRawBinADCP
import rdradcp.plot_ADCP_velocity
from rdradcp.plot_ADCP_vel_FFT import plot_depth_averaged_analysis
from rdradcp.plot_ADCP_vel_FFT import plot_velocity_wavelet_spectrum,plot_rotary_wavelet_spectrum
from rdradcp.plot_ADCP_vel_FFT import plot_cross_spectogram_w_T
from rdradcp.plot_ADCP_vel_FFT import plot_FFT_twinx_W_T
from rdradcp.plot_ADCP_vel_FFT import plot_fft_analysis
import rdradcp.Timer
from rdradcp.writeAdcpTxtData import RdiDataWriter
import csv, sys, os
import utools.windows

from utools import readTempHoboFiles
from utools import smooth

print('--> Default read 2011 data File:2011_west_gap_DPLWG000.000) \n')
print('\n\n')



#===============================================================================
# try:
#     user_paths = os.environ['PYTHONPATH'].split(os.pathsep)
#     for i in user_paths: print i
# except KeyError:
#     user_paths = []
# sys.exit()
#===============================================================================


def write_datefile(writer, velocity, date):
    idx = 0
    numdat = []
    prev = 0
    prevtxt = ''
    bins = velocity.shape[0]
    newrow = ['date']
    for i in range(0, velocity.shape[0]):
        newrow.append('bin%d' % i)
    writer.writerow(newrow)

    for i in range(0, velocity.shape[1]):
        # for j in range(0, bins)\
        newrow = [date[0][i]]
        for j in range(0, velocity.shape[0]):
            newrow.append(velocity[j, i])
        # writer.writerow([date[0][i], velocity[:, i]])
        writer.writerow(newrow)

    print("Done writing file")

def writeBins(date, data, path_out, fname):

    ofile = open(path_out + '/' + fname, "wt")
    writer = csv.writer(ofile, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
    write_datefile(writer, data, date)
    ofile.close()


try:
    with rdradcp.Timer.Timer() as t:
        # [adcp, cfg, ens, hdr] = readRawBinADCP('/home/bogdan/Documents/UofT/PhD/Data_Files/RDADCP/TRCA/2011/2011_west_gap_DPLWG000.000', 1, [100, 7726], 'info', 'yes', 'baseyear', 2000, 'despike', 'yes');
        # [adcp, cfg, ens, hdr] = readRawBinADCP('/home/bogdan/Download/DPL3_000.000', 1, [1, 1387893], 'info', 'yes', 'baseyear', 2000, 'despike', 'yes')
        # [adcp, cfg, ens, hdr] = readRawBinADCP('/home/bogdan/Download/DPL3_000.000', 1, [1, 1100000], 'info', 'yes', 'baseyear', 2000, 'despike', 'yes')
        # [adcp, cfg, ens, hdr] = readRawBinADCP('/home/bogdan/Documents/UofT/PhD/Data_Files/MOE deployment 18-07-2012/Data/ADCP/ADCP-3rd-card/600NE008.000', 1, [1, 6938], 'info', 'yes', 'baseyear', 2000, 'despike', 'yes')
        # [adcp, cfg, ens, hdr] = readRawBinADCP('/home/bogdan/Documents/UofT/PhD/Data_Files/MOE deployment 18-07-2012/Data/ADCP/ADCP-3rd-card/600NE002.000', 1, [1, 6938], 'info', 'yes', 'baseyear', 2000, 'despike', 'yes')
        # [adcp, cfg, ens, hdr] = readRawBinADCP('/home/bogdan/Documents/UofT/PhD/Data_Files/MOE deployment 18-07-2012/Data/ADCP/ADCP-3rd-card/600NE003.000', 1, [1, 280086], 'info', 'yes', 'baseyear', 2000, 'despike', 'yes')
        # [adcp, cfg, ens, hdr] = readRawBinADCP('/home/bogdan/Documents/UofT/PhD/Data_Files/2012-MOE-L.Ontario-data/ADCP data/3169_Ajax S Outfall/3169J000.000', 1, [500, 10400], 'info', 'yes', 'baseyear', 2000, 'despike', 'yes', 'debug', 'no')



        #name = "Tor Harb 600 MHz"
        # for the WCT figure
        #[adcp, cfg, ens, hdr] = readRawBinADCP('/home/bogdan/Documents/UofT/PhD/Data_Files/2013/ADCP-TorHarb/600mhz-DPL_002.000', 1, [700, 239800], 'info', 'yes', 'baseyear', 2000, 'despike', 'yes', 'debug', 'no')

        #reduced set 
        #[adcp, cfg, ens, hdr] = readRawBinADCP('/home/bogdan/Documents/UofT/PhD/Data_Files/2013/ADCP-TorHarb/600mhz-DPL_002.000', 1, [10000, 19800], 'info', 'yes', 'baseyear', 2000, 'despike', 'yes', 'debug', 'no')

        #name = "E-Gap"
        #[adcp, cfg, ens, hdr] = readRawBinADCP('/home/bogdan/Documents/UofT/PhD/Data_Files/RDADCP/TRCA/2009/east_gap-DS09_000.000' , 1, [100, 5726], 'info', 'yes', 'baseyear', 2000, 'despike', 'yes');
        
        
        #[adcp, cfg, ens, hdr] = readRawBinADCP('/home/bogdan/Documents/UofT/PhD/Data_Files/2013/ADCP-TorHarb/1200mhz-EMBC_004.000', 1, [1, 262500], 'info', 'yes', 'baseyear', 2000, 'despike', 'yes', 'debug', 'no')

        #2016 data
        name = "Emb-C 1200 MHz"
        adcpPath2016 = "/home/bogdan/Documents/UofT/PhD/Data_Files/2016/ADCP2016_Data/ADCP-files/"

        fname = "EC01_000.000"
        ensno = 19911

        fname = "EG01_000.000"
        ensno = 68894

        #fname = "OH01_002.000"
        #ensno = 54578

        #fname = "TI01_000.000"
        #ensno = 68920

        #fname = "WG01_000.000"
        #ensno = 10448

        [adcp, cfg, ens, hdr] = readRawBinADCP(
            adcpPath2016 + '/' + fname, 1, [1, ensno], 'info',
            'yes', 'baseyear', 2000, 'despike', 'yes', 'debug', 'no')

        adcpTxt = RdiDataWriter(adcpPath2016, adcp)
        adcpTxt.writeAdcp(fname, adcp)
finally:
    print(('Read took %.03f sec.' % t.interval))

try:
    with rdradcp.Timer.Timer() as t:
        #verify
        adcpTxt2 = RdiDataWriter(adcpPath2016, None, n=ensno, fname=fname)
        adcp2 = adcpTxt2.readAdcp(fname)
finally:
    print(('Text read took %.03f sec.' % t.interval))


print('ADCP configuration')
print('----------------------')
print('no of bins :%d' % adcp.config.n_cells)
print('first bin distance :%f' % adcp.config.bin1_dist)
print('no of beams :%d' % adcp.config.n_beams)
print('system of coordinates :%s' % adcp.config.coord_sys)
print('time between pings :%f' % adcp.config.time_between_ping_groups)
print('no of pings per ensamble :%d' % adcp.config.pings_per_ensemble)

# This is done now in the main method
# adcp1.goodbins = numpy.round((adcp1.depth[0][1000] - adcp.config.bin1_dist)/adcp.config.cell_size)
print('no of bins that have full water:%d' % adcp.goodbins)
# IMPORTANT to know for depth bin calculations adcp.config.ranges
print('----------------------')

path_out = "/software/SAGEwork/rdrADCP"
exit(0)



traditional = True

if traditional:


    interp = True
    echo = False

    if True:
        #-------------------------------------------------------------------
        ylabel = 'E u [m/s]'
        data_args1 = [adcp.east_vel, ylabel]
        subplot = True
        bins = [0, 3, 5, 7]
        bins = [0, 1, 2, 3, 4]
        rdradcp.plot_ADCP_velocity.plot_ADCP_velocity(adcp, data_args1, 'Lake Ontario - East velocity profiles',
                                                      subplot, bins, doy = True)
        rdradcp.plot_ADCP_velocity.plot_ADCP_velocity_img(adcp, data_args1, 'Lake Ontario - East velocity profiles',
                                                          interp = interp, echo = echo, doy = True)
        writeBins(adcp.mtime, adcp.east_vel, path_out, "eastVel.csv")
        print("start FFT analysis ...East")
        bin = 1
        strg = '%s - E velocity bin:%d' % (name, bin)
        print(strg)
        plot_depth_averaged_analysis(adcp, data_args1, strg, bin = bin, avg = False)
        bin = 5
        strg = '%s - E velocity bin:%d' % (name, bin)
        print(strg)
        plot_depth_averaged_analysis(adcp, data_args1, strg, bin = bin, avg = False)

        #-------------------------------------------------------------------
        data_args2 = [adcp.north_vel, 'N velocity [m/s]']
        print("North vel")
        subplot = True
        bins = [0, 3, 5, 7]
        rdradcp.plot_ADCP_velocity.plot_ADCP_velocity(adcp, data_args2, 'Lake Ontario - North velocity profiles', subplot, bins, doy = True)
        print("North vel img")
        rdradcp.plot_ADCP_velocity.plot_ADCP_velocity_img(adcp, data_args2, 'Lake Ontario - North velocity profiles', \
                                                  interp = interp, echo = echo, doy = True)
        writebins.writeBins(adcp.mtime, adcp.north_vel, path_out, "northVel.csv")

        print("start FFT analysis ... North")
        bin = 1
        strg = '%s - N velocity bin:%d' % (name, bin)
        print(strg)
        plot_depth_averaged_analysis(adcp, data_args2, strg, bin = bin, avg = False, scale = 'loglog')
        bin = 5
        strg = '%s - N velocity bin:%d' % (name, bin)
        print(strg)
        plot_depth_averaged_analysis(adcp, data_args2, strg, bin = bin, avg = False, scale = 'loglog')
    # end if
    bin = 3
    counterclockwise = True
    plot_rotary_wavelet_spectrum(adcp, bin = bin, counterclockwise = counterclockwise)


    #-------------------------------------------------------------------

    #===============================================================================
    # data_args3 = [adcp.vert_vel, 'Vertical Velocity']
    # print "plot vert_vel"
    # plot_ADCP_velocity.plot_ADCP_velocity(adcp, data_args3, 'Lake Ontario - Vertical velocity profiles')
    # print "plot vert_vel img "
    # plot_ADCP_velocity.plot_ADCP_velocity_img(adcp, data_args3, 'Lake Ontario - Vertical velocity profiles', \
    #                                           interp = interp, echo = echo)
    # writeBins(adcp.vert_vel, path_out, "vertVel.csv")
    #
    # print "start FFT analysis ... Vertical"
    # bin = 0
    # strg = '%s - Vertical velocity bin:%d frequencies Spectrum' % (name, bin)
    # print strg
    # plot_depth_averaged_analysis(adcp, data_args3, strg, bin = bin, avg = False)
    # bin = 5
    # strg = '%s - Vertical velocity bin:%d frequencies Spectrum' % (name, bin)
    # print strg
    # plot_depth_averaged_analysis(adcp, data_args3, strg, bin = bin, avg = False)
    #===============================================================================

    #-------------------------------------------------------------------
    # data_args4 = [adcp.error_vel , 'Error Velocity']
    # # plot_ADCP_velocity(adcp, data_args4, 'Lake Opeongo - Error velocity profiles')
    # writeBins(adcp.error_vel, path_out, "errorVel.csv")
    #
    #
    # data = adcp.north_vel
    # ylabel = 'North velocity Singles side amplitude spectrum [m/s]';
    # data_args = [data, ylabel]
    # #plot_depth_averaged_analysis(adcp, data_args1, 'Toronto Harbour West gap - East velocity frequencies Spectrum')
    # print "start printing ..."
    # plot_depth_averaged_analysis(adcp, data_args, 'Whitby - North velocity frequencies Spectrum')
else:
    echo = False
    smooth = False
    showtest = False
    resample = True
    interp = True

    plotwavelet = True
    plotFFT = False
    plotvelimg = False
    plotUVT = False

    if plotvelimg:
        ylabel = 'E u [m/s]';
        data_args1 = [adcp.east_vel, ylabel]
        rdradcp.plot_ADCP_velocity.plot_ADCP_velocity_img(adcp, data_args1, 'Lake Ontario - East velocity profiles', \
                                                   interp = interp, echo = echo, doy = True)

    span_window = utools.windows.window_hour
    smooth_window = utools.windows.windows[1]

    # 1') read all harbour data (EG + Jarvis Dock

    # common deployment period good for WCT as well
    date = ['13/06/25 00:00:00', '13/10/27 00:00:00']

    # zoom in
    # date = ['13/07/18 00:00:00', '13/07/27 00:00:00']


    dt = datetime.datetime.strptime(date[0], "%y/%m/%d %H:%M:%S")
    start_num = dates.date2num(dt)
    dt = datetime.datetime.strptime(date[1], "%y/%m/%d %H:%M:%S")
    end_num = dates.date2num(dt)

    print("get temperature data")
    #harbour_path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/AllHarbour/csv_processed/EGap-JarvisDock'
    harbour_path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/corr_vel_temp'
    base, dirs, files = next(iter(os.walk(harbour_path)))
    sorted_files = sorted(files, key = lambda x: x.split('.')[0])

    TH_dateTimeArr = numpy.zeros(len(sorted_files), dtype = numpy.ndarray)
    TH_tempArr = numpy.zeros(len(sorted_files), dtype = numpy.ndarray)
    TH_resultsArr = numpy.zeros(len(sorted_files), dtype = numpy.ndarray)
    TH_k = numpy.zeros(len(sorted_files), dtype = numpy.ndarray)
    i = 0
    for fname in sorted_files:
        dateTime, temp, results = utools.readTempHoboFiles.get_data_from_file(fname, span_window, smooth_window, \
                                                                       timeinterv = [start_num, end_num], rpath = harbour_path)
        maxidx = 30000
        TH_dateTimeArr[i] = numpy.append(TH_dateTimeArr[i], dateTime[:maxidx])
        TH_resultsArr[i] = numpy.append(TH_resultsArr[i], results[:maxidx])
        TH_tempArr[i] = numpy.append(TH_tempArr[i], temp[:maxidx])
        TH_k[i] = numpy.append(TH_k[i], i)
        i += 1
    # end for

    print("smooth velocity data")
    time1, evel = rdradcp.plot_ADCP_velocity.select_dates(start_num, end_num, adcp.mtime[0, :], adcp.east_vel)
    time2, nvel = rdradcp.plot_ADCP_velocity.select_dates(start_num, end_num, adcp.mtime[0, :], adcp.north_vel)

    evel = numpy.array(evel)
    nvel = numpy.array(nvel)
    evel[numpy.isnan(evel)] = 0  # set to zero NAN values
    evel[numpy.isinf(evel)] = 0  # set to 0 infinite values
    nvel[numpy.isnan(nvel)] = 0  # set to zero NAN values
    nvel[numpy.isinf(nvel)] = 0  # set to 0 infinite values

    writebins.writeBins(time1, evel, path_out, "eastVel.csv")
    writebins.writeBins(time2, nvel, path_out, "northVel.csv")




    # smoothfit requires list so we need to convert velocities back to list

    if smooth:
        results_u = []
        results_v = []
        i = 0
        for ev in evel:
            results_u.append(smooth.smoothfit(time1[i], ev.tolist(), span_window, smooth_window)['smoothed'])
            i += 1
        # end for
        i = 0
        for nv in nvel:
            results_v.append(smooth.smoothfit(time2[i], nv.tolist(), span_window, smooth_window)['smoothed'])
            i += 1
        # end for
        results_u = numpy.array(results_u)
        results_v = numpy.array(results_v)
    else:
        results_u = evel
        results_v = nvel
    # end if

    bin = 0
    tlogno = 1

    if plotUVT:
        rdradcp.plot_ADCP_velocity.plot_temp_u_v(adcp, time1, results_u, time2, results_v, TH_dateTimeArr, TH_resultsArr, interp = interp)

    if plotFFT:
        print("two plots on the same figure of FFT splectrograms")
        
        drawslope = True
        # plot_FFT_twinx_W_T(time1[bin], results_u[bin] + 1j * results_v[bin], TH_dateTimeArr[tlogno], TH_resultsArr[tlogno], scale = 'log')
        plot_FFT_twinx_W_T(time1[bin], results_u[bin] + 1j * results_v[bin], TH_dateTimeArr[tlogno], TH_resultsArr[tlogno], scale = 'log', drawslope = drawslope)

        if showtest:
            plot_fft_analysis(numpy.array(time1[bin]), numpy.array(results_u[bin] + 1j * results_v[bin]), "title", 'w -velocity', subplot = False, scale = 'log', bin = bin, avg = False)
            plot_fft_analysis(numpy.array(TH_dateTimeArr[tlogno]), numpy.array(TH_resultsArr[tlogno]), "title", 'Temperature', subplot = False, scale = 'log', bin = bin, avg = False)


    if plotwavelet:
        scaleunit = 'day'

        # must down sample here
        if resample:
            if len(TH_dateTimeArr) != len(time1):
                res_time1 = scipy.ndimage.interpolation.zoom(time1[bin], float(len(TH_dateTimeArr[tlogno])) / float(len(time1[bin])))
                res_u = scipy.ndimage.interpolation.zoom(evel[bin], float(len(TH_dateTimeArr[tlogno])) / float(len(time1[bin])))
                res_v = scipy.ndimage.interpolation.zoom(nvel[bin], float(len(TH_dateTimeArr[tlogno])) / float(len(time1[bin])))

                print("plot vel wavelet")
                plot_velocity_wavelet_spectrum(res_time1, res_u, scaleunit = scaleunit)

                print("plot temp wavelet")
                plot_velocity_wavelet_spectrum(TH_dateTimeArr[tlogno][1:], TH_resultsArr[tlogno][1:], scaleunit = scaleunit)

                print("plot cross wavelet")
                plot_cross_spectogram_w_T(res_time1, res_u, res_v, res_time1, TH_resultsArr[tlogno], scaleunit = scaleunit)
        else:
            print("plot cross wavelet")
            plot_cross_spectogram_w_T(time1[bin], results_u[bin], results_v[bin], TH_dateTimeArr[tlogno], TH_resultsArr[tlogno], scaleunit = scaleunit)
        # endif

print("Done")
