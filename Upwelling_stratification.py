'''
Created on Dec 21, 2013

@author: bogdan
This Script calulated adn draws figures for JGLR paper:
    "Extreme temperature variability within a harbour connected to a large lake"
'''

# libraries
import numpy as np
import scipy as sp
import csv
import os, locale
import datetime
import matplotlib.dates as dates

# local
import upwelling
from utools import readTempHoboFiles
from utools import display_data
import ufft.spectral_analysis
import utools.timeseries_correlation
import utools.custom_csv_readers
import gsw


class Upwelling(object):
    '''
    classdocs
    '''
    windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
    window_6hour = "window_6hour"  # 30 * 6 for a 2 minute sampling
    window_hour = "window_hour"  # 30
    window_halfhour = "window_1/2hour"  # 30
    window_day = "window_day"  # 30 * 24
    window_half_day = "window_half_day"  # 30 * 12
    window_3days = "window_3days"  # 3 * 30 * 24
    window_7days = "window_7days"  # 7 * 30 * 24

    filter = {'h0.5_1.5' : {  # hours 0.5-1.5 hours
                       'lowcut' :1.0 / (1.5) / 3600,
                       'highcut' :1.0 / (0.5) / 3600
              },
              'h2_10' : {  # hours 2-10 hours
                       'lowcut' :1.0 / (10) / 3600,
                       'highcut' :1.0 / (2.0) / 3600
              },
              'semidiurnal': {  # 12 hours
                              'lowcut' : 1.0 / (12.1) / 3600,
                              'highcut' : 1.0 / (11.9) / 3600
              },
              'h10_16' : {  # hours 10-16 hours
                       'lowcut' :1.0 / (16) / 3600,
                       'highcut' :1.0 / (10) / 3600
              },
              'poincare': {  # poincare
                            'lowcut': 1.0 / (17.3) / 3600,
                            'highcut' :1.0 / (16.6) / 3600
              },
              'h18_30' : {  # hours 18-30 hours
                       'lowcut' :1.0 / (30) / 3600,
                       'highcut' :1.0 / (18) / 3600
              },
              'diurnal' : {  # diurnal
                           'lowcut' : 1.0 / (24.2) / 3600,
                           'highcut' : 1.0 / (23.8) / 3600
              },
              'k3_7' : {  # Kelvin 3-7 days
                       'lowcut' :1.0 / (24 * 10) / 3600,
                       'highcut' :1.0 / (24 * 3) / 3600
              },
              'k10_15' :{  # Kelvin 10-15 days
                          'lowcut' :1.0 / (24 * 15) / 3600,
                          'highcut' : 1.0 / (24 * 10) / 3600
              }
     }

    def __init__(self, params):
        '''
        Constructor
        '''

    def Nsquared(self, data):
        sal, CT, pres, lat = data
        N2, p_mid = gsw.Nsquared(sal, CT, pres, lat = lat)

    def Burger(self, data, H, L):
        '''
        Bu = NH/fL   in which
               N is the buoyancy frequency,
               f is the Coriolis parameter
               H characteristic vertical length scale
               L characteristic horizontal length scale
        '''
        sal, CT, pres, lat = data
        N2 = gsw.Nsquared(sal, CT, pres, lat = lat)
        f = gsw.f(lat)
        Bu = (np.sqrt(N2) * H) / (f * L)
        return Bu


    def get_timeseries_data(self, path, date, moving_avg, window):

        dateTime, temp, results, k , fnames = utools.readTempHoboFiles.read_files(moving_avg, window, [date[0], date[1]], path)

        return dateTime, temp, results, k, fnames


    def draw_isotherms(self, path, timeint, tick, maxdepth, firstlogdepth, maxtemp, title = None,
                       thermocline = True, interpolate = None, draw_lines = False, line_divisor = 2):
        # dirlist needs to be sorted in ascending order
        # Separate directories from files
        base, dirs, files = next(iter(os.walk(path)))

        sorted_files = sorted(files, key = lambda x: x.split('.')[0])


        # dateTimeArr = np.zeros(len(sorted_files), dtype = np.ndarray)
        # tempArr = np.zeros(len(sorted_files), dtype = np.ndarray)
        # resultsArr = np.zeros(len(sorted_files), dtype = np.ndarray)
        # k = np.zeros(len(sorted_files), dtype = np.ndarray)

        dateTimeArr = []
        tempArr = []
        resultsArr = []
        k = []

        j = i = 0
        nsorted_files = sorted_files[:]
        for fname in sorted_files:
            print("Filename = %s" % fname)
            dateTime, temp, results = utools.readTempHoboFiles.get_data_from_file(fname, self.window_6hour, self.windows[1], timeinterv = timeint, rpath = path)

            dateTimeArr.append(dateTime)
            resultsArr.append(results)
            tempArr.append(temp)
            k.append(j)

#===============================================================================
#             if interpolate != None:
#                 if (i - 1) % 2 == 0 and i != 0 :  # interpolate & insert
#                     dateTimeArr.insert(j, dateTimeArr[j])
#                     k.insert(j, j)
#                     k[j + 1] = j + 1
#                     minlen = min(len(resultsArr[j]), len(resultsArr[j - 1]))
#                     resval = (np.array(resultsArr[j][:minlen]) + np.array(resultsArr[j - 1][:minlen])) / 2.0
#                     resultsArr.insert(j, resval)
#
#                     tempval = (np.array(tempArr[j][:minlen]) + np.array(tempArr[j - 1][:minlen])) / 2.0
#                     tempArr.insert(j, tempval)
#
#                     nsorted_files.insert(j, "mid")
#                     # increment j
#                     j += 1
#                 # end if
#             # end if
#===============================================================================
            i += 1
            j += 1
        # end for

        # plot the temperature not the smoothed ones
        datetype = 'dayofyear'
        if title != None:
            custom = title
        else:
            custom = "Temperature Toronto Waterfront Zones"
        ndateTimeArr = np.array(dateTimeArr)
        ntempArr = np.array(tempArr)
        nresultsArr = np.array(resultsArr)
        nk = np.array(k)
        utools.display_data.display_temperatures(ndateTimeArr, ntempArr, nk, fnames = nsorted_files, custom = custom, \
                                      datetype = datetype, ylab = "Temperature [$^\circ$C]")

        diffarr = np.array(ntempArr[1]) - np.array(ntempArr[0]) # Tc4
        diffarr = np.array(ntempArr[11]) - np.array(ntempArr[10]) # CB
        # for TC4 ylim
        ylim=[-0.5, 10]
        #fnames = ["$\Delta$T ($\Delta$H = 1m)"]
        utools.display_data.display_temperatures(np.array([ndateTimeArr[1]]), np.array([diffarr]), nk, ylim=ylim, custom = custom, \
                                      datetype = datetype, ylab = "$\Delta$ Temperature [$^\circ$C]", draw_xaxis = True, fontsize = 22)


        # 3) Mixed water, air ,img data
        custom = np.array(["$\Delta$ T [$^\circ$C]", "$\Delta$ T [$^\circ$C]"])
        # ToDO: Add short and long radiation
        print("Inversions Start display mixed subplots  ")
        
        data1 = [np.array(diffarr), np.array(diffarr)]
        dateTimes1 = [ndateTimeArr[1],ndateTimeArr[1]]
        ylabels = custom
        limits1 = [[-0.5, 10], [-0.15, 0.0]]
        limits1 = [[-0.5, 10], [-0.5, 0.0]]
        
        utools.display_data.display_mixed_subplot(dateTimes1 = dateTimes1, data = data1, varnames = [], ylabels1 = ylabels, limits1 = limits1,\
                                           dateTimes2 = [], groups = [], groupnames = [], ylabels2 = [], \
                                           dateTimes3 = [], imgs = [], ylabels3 = [], ticks = [], maxdepths = None, \
                                           mindepths = None, mintemps = None, firstlogs = None, maxtemps = None, \
                              fnames = None, revert = False, custom = None, maxdepth = None, tick = None, firstlog = None, yday = True, \
                              title = False, grid = False, limits = None, sharex = True, fontsize = 20, group_first = False, interp = None)

        



        ycustom = "Stations"
        revert = True
        utools.display_data.display_img_temperatures(ndateTimeArr, ntempArr, nresultsArr, nk, tick, maxdepth, firstlogdepth, maxtemp, revert = revert, \
                                              fontsize = 22, datetype = datetype, thermocline = thermocline, interp = interpolate, ycustom = ycustom, \
                                              cblabel = "Temp [$^\circ$C]", draw_hline = draw_lines, hline_freq = line_divisor)

        utools.display_data.display_temperatures_subplot(ndateTimeArr, ntempArr, nresultsArr, nk, fnames = nsorted_files, revert = False, custom = None, \
                                 maxdepth = None, tick = None, firstlog = None, yday = True, delay = None, group = 2, processed = False, \
                                 limits = [0, 25], sharex = True)


    def detect_bottom_loggers_min_temp(self, path, date, filt, timeavg, peaks = False):
        '''
        Detect the minimum temperature at each bottom logger using a synoptic (7-14 days) running mean for
        determining the upwelling propagation velocities
        '''

        startdate, enddate = date

        lowcut = self.filter[filt]['lowcut']
        highcut = self.filter[filt]['highcut']
        filter = [lowcut, highcut]

        minorgrid = 'mondays'
        datetype = 'dayofyear'
        # upwelling.read_Upwelling_files(path, [startdate, enddate], timeavg = timeavg, subplot = None, filter = filter, fft = False, stats = True, with_weather = False)
        [a_max, a_min, afnames] = upwelling.plot_Upwelling_one_fig(path, [startdate, enddate], timeavg = timeavg, \
                                                                   subplot = None, filter = filter, peaks = peaks, \
                                                                   datetype = datetype)
        return [a_max, a_min, afnames]

    def get_lat_lon(self, file):
        '''

        '''

        ifile = open(file, 'rt')
        reader = csv.reader(ifile, delimiter = ',', quotechar = '"')

        hdr = ["location", "Lat", "Lon", "easting", "northing"]

        rownum = 0
        station = []
        lat = []
        lon = []

        for row in reader:

            # Save header row.
            strg = row[0]
            if rownum == 0 :
                header = row
            else:
                colnum = 0
                for col in row:
                    if header[colnum] == "location":
                        station.append(str(col))
                    if header[colnum] == "Lat":
                        lat.append(str(col))
                    if header[colnum] == "Lon":
                        lon.append(str(col))

                    colnum += 1
                # end for col
            rownum += 1
        # end for roe
        ifile.close()

        return [station, lat, lon]

    def determine_temp_rate_per_loc(self, dateTime, results, grad, tg, delta = 1):
        k = 0
        t = dateTime
        T = results
            
        dt_hour = (t[2] - t[1]) * 24

        hour = 0
        grad = []
        tg = [] 
        for j in range(1, len(t) - 1):
            # cummulate an hour
            hour += dt_hour
            if j == 1:
                Ti = T[j]
            if hour >= 1 * delta:
                Tf = T[j]
                grad.append(Tf - Ti)
                tg.append(t[j])
                Ti = Tf
                k += 1
                hour = 0
        
        gmax = np.max(grad)
        gmin = np.min(grad) 
        return np.array(grad), np.array(tg), k, gmax, gmin

    def determine_temp_rate(self, dateTime, results, grad, tg, delta = 1):
        '''
        '''
        ymax = 0
        ymin = 0

        for i in range(len(dateTime)):
            
            grad[i],tg[i],k, gmax, gmin =  self.determine_temp_rate_per_loc(dateTime[i], results[i], grad[i], tg, delta = 1)
            # resize the array
            #grad[i] = np.resize(grad[i], k - 1)
            #tg[i] = np.resize(tg[i], k - 1)
            ymax = np.maximum(ymax, np.amax(grad[i], axis = 0))
            ymin = np.minimum(ymin, np.amin(grad[i], axis = 0))

        return grad, tg, ymax, ymin

    def plot_temp_rate(self, paths, date, timeavg, window, tunits = 'day', percent = False, delta = 1):

        startdate, enddate = date

        minorgrid = 'mondays'
        datetype = 'dayofyear'
        binsarr = []
        valuearr = []
        fnamesarr = []

        for path in paths:
            dateTime, temp, results, k, fnames = self.get_timeseries_data(path, date, timeavg, window)
            
            
              #Create a table : Name | max rate | max temp | min temp " # > 4C
            print("Station, Location, Max rate, Min rate, No events >+_ 4OC, Max temp, Min temp Avg temp")
            
            overrate= 0.3    
            for i in range(0, len(fnames)):
                locgrad = np.object
                loctg = np.object
                locgrad, tg, k, gmax, gmin = self.determine_temp_rate_per_loc(dateTime[i], results[i], locgrad, \
                                                                              loctg, delta = 1) 
                print("%s %s, %.2f, %.2f, %d, %.2f, %.2f, %.2f" % \
                (fnames[i], "LOCAION", gmax, gmin, np.sum(np.abs(locgrad)>overrate), np.max(results[i]),\
                 np.percentile(results[i],5), np.mean(results[i]))) 
                 #np.min(np.nonzero(results[i])))

            #Histogram
            grad = np.zeros(len(dateTime), dtype = np.ndarray)  # rate
            tg = np.zeros(len(dateTime), dtype = np.ndarray)  #
            ghist = np.zeros(len(dateTime), dtype = np.ndarray)  # histogram
            perc = np.zeros(len(dateTime), dtype = np.ndarray)  # histogram
            edges = np.zeros(len(dateTime), dtype = np.ndarray)  # edges
            bins = np.zeros(len(dateTime), dtype = np.ndarray)  # bins

            if tunits == 'day':
                factor = 86400
            elif tunits == 'hour':
                factor = 3600
            else:
                factor = 1

            grad, tg, ymax, ymin = self.determine_temp_rate(dateTime, results, grad, tg, delta)
            
          

            # put data in bins
            for i in range(len(dateTime)):
                # put data in bins
                edges[i] = [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5 , 6, 7]
                grange = [ymin, ymax]
                ghist[i], edges[i] = np.histogram(grad[i], bins = edges[i], range = grange)

                bins[i] = edges[i][:-1]


                if percent:
                    total = 0.0
                    perc[i] = np.zeros(len(ghist[i]), dtype = np.double)
                    for j in range(0, len(ghist[i])):
                        total += ghist[i][j]
                        #print "TOTAL location:%s total:%d j:%d hist:%d" % (fnames[i], total, j, ghist[i][j])
                    for j in range(0, len(ghist[i])):

                        perc[i][j] = ghist[i][j] * 100.0 / total
                        #print "PERCENT location:%s j:%d hist:%f" % (fnames[i], j, perc[i][j])
            # end for i

            ylab = 'Temperature rate [$^\circ$C$h^-1$]'

            utools.display_data.display_temperatures(tg, grad, k, fnames, False, difflines = False, custom = '', maxdepth = None, \
                                               tick = None, firstlog = None, fontsize = 20, ylim = [ymin - 1, ymax + 1], fill = False, \
                                               show = True, datetype = "dayofyear", minorgrid = "mondays", ylab = ylab)
            if percent:
                values = perc
            else:
                values = ghist

            binsarr.append(bins[:])
            valuearr.append(values[:])
            fnamesarr.append(fnames[:])
        # end for k paths


        utools.display_data.display_marker_histogram(binsarr, valuearr, fnamesarr, xlabel = r'Temperature rate [$\mathsf{^\circ C\cdot h^{-1}}$]', ylabel = "Frequency [%]", \
                                              title = None, log = True, grid = False, fontsize = 18)


        #=======================================================================

    def determine_velocity(self, a_max, a_min, afnames, location, lat, lon, exclusions):

        # rearrange a_min eliminating exclusions

        for i in range(0, len (a_min)):
            name = afnames[i]
            try:
                min_list = exclusions[name]
            except:
                continue
            a_min[i] = np.delete(a_min[i], min_list, 0)

                # calculate distances
        distances = gsw.distance(lon, lat, 0)
        print("distances", distances, end=' ')
        print("names", afnames)

        # calculate velocities u=D/t  i is the location  the length of each a_min is the number of peaks
        dt = [[] for i in range(len (a_min))]
        v = [[] for i in range(len (a_min))]
        for i in range(0, len (a_min) - 1):  # iterate on places
            name = afnames[i]
            for j in range(0, len(a_min[0])):  # iterate on min points at each place
                print(i, ':', j)
                dt[i].append((a_min[i + 1][j][0] - a_min[i][j][0]) * 3600 * 24)  # sec
                print("a_min[%d ] (%f)- a_min[%d ] (%f) = %f" % (i + 1, a_min[i + 1][j][0], i, a_min[i][j][0], (a_min[i + 1][j][0] - a_min[i][j][0]) * 3600 * 24))
        for i in range(0, len (a_min) - 1):  # iterate on places
            for j in range(0, len(a_min[0])):  # iterate on min points at each place
                v[i].append(distances[0][i] / dt[i][j])
                print("velocity at %s to %s (dist = %f)  event[%d] = %f [m/s]" % (afnames[i], afnames[i + 1], distances[0][i], j, v[i][j]))

        print("------------------------------------------------------------------------------")

        for j in range(len (a_min[0])):
            if j == 0:
                for i in range(0, len (a_min) - 1):  # iterate on places
                    print('%12s | ' % afnames[i], end=' ')
            print()
            print("-----------------------------------------------------------------------------")
            for i in range(0, len (a_min) - 1):  # iterate on places
                print("%12.4f | " % (v[i][j]), end=' ')

        # end for
        print()
        print("-----------------------------------------------------------------------------")

    def plot_filtered_data(self, dateTimeArr, tempArr, fnames, k, filt, ylim):

        lowcut = self.filter[filt]['lowcut']
        highcut = self.filter[filt]['highcut']
        filter = [lowcut, highcut]

        upwelling.plot_buterworth_filtered_data(dateTimeArr, tempArr, fnames, k, filter, ylim)


    def get_temp_snapshots(self, path, date, no_of_interv, timeavg, window):
        '''
        get temperatures at all points from date each interval for a number of intervals
        '''
        # get the data
        dateTime, temp, results, k, fnames = self.get_timeseries_data(path, date, timeavg, window)

        name = np.zeros(len(dateTime) , np.dtype('a14'))
        X = np.zeros(len(dateTime) , dtype = np.float_)
        Y = np.zeros(len(dateTime) , dtype = np.float_)
        snap_temp = np.zeros(len(dateTime), dtype = np.ndarray)

        for i in range(0, len(results)):
            name[i] = fnames[i]
            X[i] = 0.0
            Y[i] = 0.0
            temp_i = results[i][1:]

            length = len(temp_i)
            snap_temp[i] = np.zeros(no_of_interv, dtype = np.float_)
            idx_increment = length / no_of_interv

            for j in range(0, no_of_interv):
                snap_temp[i][j] = temp_i[j * idx_increment]
                print("name= %s temp=%f  idx = %i" % (name[i], snap_temp[i][j], j * idx_increment))
            # end for j
        # end for i
        return [X, Y, name, snap_temp]



    def calculate_avg_maxgrd_max_min(self, path, date, timeavg, window):
        '''
        Calculate average temperatures, max rate, max temperature and min temperatures
        '''

        # get the data
        dateTime, temp, results, k, fnames = self.get_timeseries_data(path, date, timeavg, window)

        # calculate max & min temperature hourly rate
        grad = np.zeros(len(dateTime), dtype = np.ndarray)
        tg = np.zeros(len(dateTime), dtype = np.ndarray)
        grad, tg, ymax, ymin = self.determine_temp_rate(dateTime, results, grad, tg)


        maxidx = len(results)
        for i in range(0, len(results)):
            print("fname %s, len:%d" % (fnames[i], len(results[i])))
            maxidx = min(maxidx, len(temp[i]))

        mean_temp = np.zeros(maxidx)
        max_temp = np.zeros(maxidx)
        min_temp = np.zeros(maxidx)
        max_grad = np.zeros(maxidx)

        for i in range(0, len(results)):
            # calculate mean
            mean_temp[i] = np.mean(results[i][1:])  # this is good

            # USe percentile for a more accurate perspective and to avoid flukes and extremes
            # calculate max
            # max_temp[i] = np.amax(results[i][1:])  # along the time line not the stations

            max_temp[i] = np.percentile(results[i][1:], 95, axis = 0)

            # calculate min
            # min_temp[i] = np.amin(results[i][1:])  # along the time line not the stations

            min_temp[i] = np.percentile(results[i][1:], 5, axis = 0)

            # calculate max rate
            # max_grad[i] = np.max(np.abs(grad[i][1:]))  # along the time line not the stations
            max_grad[i] = np.percentile(grad[i][1:], 95, axis = 0)

        for i in range(0, maxidx):
            print("Stn %s : mean_temp:%2.2f  max_temp:%2.2f  min_temp:%2.2f  max_grad:%2.2f" \
                % (fnames[i], mean_temp[i], max_temp[i], min_temp[i], max_grad[i]))


    def correlate_N2_with_upwelling_velocity(self):
        '''
        Create a correlation , unfortunately will be 5 or 6 points corresponding to the velocity of the upwelling
        event and the N2 (stratification frequency) - either at thermocline or an average of the column?
        '''
        pass


    def detect_upper_loggers_min_temp(self):
        '''
        Detect the minimum temperature at each above bottom logger using a synoptic (7-14 days) running mean for
        determining the upwelling propagation velocities
        '''
        pass

    def Cherry_Beach_stratification(self):
        '''
        Draw the heat map of the temperature variation at Cherry beach location based on the 3 logger
        and hopefully a surface logger. Interpoate
        '''
        pass

    
    def correlate_meteo_with_temperature_variability(self, str_date, date, water_path, harbour_path, weather_path, cloud_path, lake_file, wfile):
        '''
        get meteo : wind (speed and dir), air temp, solar radiation, arit pressure
        correlate (with time lag) with the water temperature (surface and benthic)
        '''
        upwelling.plot_weather_data(date, weather_path, wfile, windrose = True)
        upwelling.subplot_weather_data(str_date, date, water_path, harbour_path, weather_path, cloud_path, lake_file, wfile)

    def spectral_analysis(self, path, files, names, log, withci = True):
        draw = False
        type = 'amplitude'
        # type = 'power'
        num_segments = 6
        ufft.spectral_analysis.doMultipleSpectralAnalysis(path, files, names, draw, window = "hanning", num_segments = num_segments, \
                                                     tunits = "day", funits = "cph", log = log, grid = False, type = type, withci = withci)

    
    def spectral_PE(self, water_path, harbour_path, name, str_date):

        dt = datetime.datetime.strptime(str_date[0], "%y/%m/%d %H:%M:%S")
        start_num = dates.date2num(dt)
        dt = datetime.datetime.strptime(str_date[1], "%y/%m/%d %H:%M:%S")
        end_num = dates.date2num(dt)
        
        #sorted from surface to bottom
        [dateTimeArr, resultsArr, tempArr, TH_dateTimeArr, TH_resultsArr, TH_tempArr] = \
                    upwelling.read_lake_and_harbour_data(str_date, [start_num,end_num], water_path, harbour_path)
        
        
        if name == "Lake Ontario":
            time = dateTimeArr
            z = list(range(3, len(time)+3,1))
            t = resultsArr
        elif name == "Toronto Harbour":
            time = TH_dateTimeArr
            z = list(range(1, len(time)+1, 1)) 
            t = TH_resultsArr
        
        g = 9.81
        #calculate temperature spectrum based on Potential energy
        
                                                 
        #SA  =   Absolute Salinity                  [ g/kg ]
        #t   =   in-situ temperature (ITS-90)       [ deg C ]
        #p   =   sea pressure                       [ dbar ]( i.e. absolute pressure - 10.1325 dbar )
        #OPTIONAL:  
        #p_ref = reference pressure                 [ dbar ]   ( i.e. absolute reference pressure - 10.1325 dbar )
        #(If reference pressure is not given then it is assumed that reference pressure is zero).
        #pt   =  potential temperature with                             [ deg C ]
        pt = np.zeros(len(z), dtype=np.ndarray)
        parr = np.zeros(len(time[0]))
        p_ref = 0
        SA = np.zeros(len(time[0]))
        for i in range(0,len(z)):
            pt[i] = np.zeros(len(time[i]))
            #p  =  sea pressure [ dbar ] ( i.e. absolute pressure - 10.1325 dbar )
            depth = -z[i]
            p = gsw.p_from_z(depth,[43.4])
            #parr.empty(len(time[i]))
            #parr.fill(p[0])
            #for j in range(0, len(time[i])):
            #    pt[i][j] = gsw.pt_from_t(SA,t[i],p,p_ref)[0]
            pt[i] = gsw.pt_from_t(SA,t[i],p[0],p_ref)
        
        
        #SA  =  Absolute Salinity                               [ g/kg ]
        #pt  =  potential temperature (ITS-90)                  [ deg C ]
        #SA & pt need to have the same dimensions.
        #CT  =  Conservative Temperature                        [ deg C ]
               
        CT = np.zeros(len(z), dtype=np.ndarray)
        for i in range(0,len(z)):
            CT[i] = np.zeros(len(time[i]))
            #for j in range(0, len(time[i])):
            #    CT[i][j] = gsw.CT_from_pt(SA,pt[i][j])[0]
            CT[i] = gsw.CT_from_pt(SA,pt[i])
            
        #SA  =  Absolute Salinity          [ g/kg ]
        #CT  =  Conservative Temperature   [ deg C ]
        #p   =  sea pressure               [ dbar ](i.e. absolute pressure - 10.1325 dbar)
        # rho  =  in-situ density     [ kg m^-3 ]
        rho = np.zeros(len(z), dtype=np.ndarray)
        for i in range(0,len(z)):
            rho[i] = np.zeros(len(time[i]))
            #for j in range(0, len(time[i])):
            #    rho[i][j] = gsw.rho(SA,CT[i][j],p)[0]
            rho[i] = gsw.rho(SA,CT[i],p)
        
        #integrate the PE
        PE= np.zeros(len(time[0]))
        for j in range(0, len(time[0])):
            for i in range(0,len(z)-1):
                PE[j]=rho[i][j]*g*z[i]*(z[i+1]-z[i])
    
        draw = False
        type = 'amplitude'
        # type = 'power'
        label  = "PSD Potential Energy [($J m^{-2})^2cph^{-1}$]"
        title =  ""
        ufft.spectral_analysis.doSpectralAnalysis([time[0],PE], name, label, title, draw, window = "hanning", num_segments=6,\
                                                  tunits = "day", funits = "cph", log = 'loglog', b_wavelets = False)


    def test(self):
        sal = np.array([0.1, 0.1])  #
        temp = np.array([4., 21.])  # Celsius
        pres = np.array([10., 20.])
        rho = gsw.rho(sal, temp, pres)
        print("density", rho)

        lat = [43.2, 43.2]
        CT = gsw.CT_from_t(sal, temp, pres)
        N2, p_mid = gsw.Nsquared(sal, CT, pres, lat = lat)
        print("N2", N2)
        print("p_mid", p_mid)

if __name__ == '__main__':

    # set what we want to do - Shouldd be controlled by cmd line args
    ###########################################################
    climate = False
    rate = False
    upwelling_anim = False
    slide_timestamp = False
    show_timeseries = False
    CB_heatmap = False
    EG_heatmap = False
    WG_heatmap = False
    OutHarb_heatmap = True
    JarvDock_heatmap = False
    filter_data = False
    weather_data = False
    spectral_harbour = False
    spectral_PE = False
    correlation_curr_temp = False

    ############################################################
    # initilize object
    upw = Upwelling("")
    # upw.test()
    # upw.Nsquared()

    #date = ['13/05/19 00:00:00', '13/10/24 00:00:00']
    # exclude_min = []


    filt = "semidiurnal"

    if climate:
        date1 = ['13/05/01 00:00:00', '13/06/05 00:00:00']
        date2 = ['13/06/05 00:00:00', '13/09/20 00:00:00']
        date3 = ['13/09/20 00:00:00', '13/11/01 00:00:00']
        datearr = [date1, date2, date3]

        for date in datearr:
            dt = datetime.datetime.strptime(date[0], "%y/%m/%d %H:%M:%S")
            start_num = dates.date2num(dt)
            dt = datetime.datetime.strptime(date[1], "%y/%m/%d %H:%M:%S")
            end_num = dates.date2num(dt)
            path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/ClimateMap'
            timeavg = Upwelling.window_hour
            print("Start date %s:" % date[0])
            print("===================================")
            upw.calculate_avg_maxgrd_max_min(path, [start_num, end_num], timeavg, upw.windows[1])

    if weather_data:

        # select one upwelling
        #date = ['13/08/12 00:00:00', '13/08/24 00:00:00']

        date = ['13/05/10 00:00:00', '13/10/27 00:00:00']
        # date = ['12/04/30 00:00:00', '12/10/27 00:00:00']  # 2012
        # stratified profile
        #date = ['13/06/30 00:00:00', '13/09/07 00:00:00']


        dt = datetime.datetime.strptime(date[0], "%y/%m/%d %H:%M:%S")
        start_num = dates.date2num(dt)
        dt = datetime.datetime.strptime(date[1], "%y/%m/%d %H:%M:%S")
        end_num = dates.date2num(dt)

        water_path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-LakeOntario/csv_processed'
        harbour_path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/AllHarbour/csv_processed/EGap-JarvisDock'
        weather_path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/ClimateData/Weather'
        # weather_path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2012/MOE deployment 18-07-2012/Data/ClimateData/all'  # 2012
        cloud_path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/ClimateData/Radiation/HDF'
        # cloud_path = "/home/bogdan/Documents/UofT/PhD/Data_Files/2013/ClimateData/Radiation/2012HDF"
        wfile = 'eng-hourly-04012013-11302013.csv'
        # wfile = 'eng-hourly-04012012-11302012-all.csv'  # 2012
        lake_file = '10_2393006.csv'
        upw.correlate_meteo_with_temperature_variability(date, [start_num, end_num], water_path, harbour_path, weather_path, cloud_path, lake_file, wfile)


    if upwelling_anim:
        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/ClimateMap'
        timeavg = Upwelling.window_hour
        #date = ['13/08/12 00:00:00', '13/08/24 00:00:00']
        #
        # must be correlated with the total length of the interval
        #
        # no_of_interv = 48 # 6 hours interval 
        no_of_interv = 288  # 1 hours interval -  

       
        date = ['13/09/09 10:00:00', '13/09/09 18:00:00']
        no_of_interv = 10  # 1 hours interval -  9 points  + 1 truncation 

        
        dt = datetime.datetime.strptime(date[0], "%y/%m/%d %H:%M:%S")
        start_num = dates.date2num(dt)
        dt = datetime.datetime.strptime(date[1], "%y/%m/%d %H:%M:%S")
        end_num = dates.date2num(dt)

        [X, Y, name, snap_temp] = upw.get_temp_snapshots(path, [start_num, end_num], no_of_interv, timeavg, upw.windows[1])
        ofile = open('/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/' + 'TempSnapshots_1H.csv', "wt")
        writer = csv.writer(ofile, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
        locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
        for i in range(0, len(name)):
            row = []
            row.append(X[i])
            row.append(Y[i])
            row.append(name[i])
            for j in range(0, len(snap_temp[i])):
                dt = dates.num2date(start_num + j / 24.0)
                timestampstr = dt.strftime("%y-%m-%d %H:%M:%S")
                row.append(timestampstr)
                row.append(snap_temp[i][j])
            writer.writerow(row)
        ofile.close()
        print("Done Upwelling animation!")

    if slide_timestamp:
        # try to get attributes from the shapefiles
        # import shapefile
        # shf_name = "/home/bogdan/Documents/UofT/PhD/Data_Files/TorontoHarbour-bathymetry/TorontoHarbourMapFiles/Temp_loggers_1h_snapshots_somefake.shp"
        # input = shapefile.Reader(shf_name)
        # shapes = input.shapes()  # -> the geometries in a list
        # fields = input.fields[1:]  # -> the fields definition in a list
        # fields_name = [field[0] for field in fields]  # -> the fields names in a list
        # attributes = input.records()  # -> the attributes in a list

        # dates teken drom csv file
        csv_name = "/home/bogdan/Documents/UofT/PhD/Data_Files/TorontoHarbour-bathymetry/tor_harb_instr_snap_dates.csv"
        ifile = open(csv_name, 'rt')
        reader = csv.reader(ifile, delimiter = ',', quotechar = '"')
        ts = []
        for row in reader:
            i = 1
            for col in row:
                if i % 2 == 0:
                    pass
                else :
                    ts.append(str(col))
                i += 1
            # end for col
        # end for row
        ifile.close()


        imgdir = "/home/bogdan/Documents/UofT/PhD/Data_Files/TorontoHarbour-bathymetry/TorHarb_1h_HeatMaps_TS"
        imgdir_out = "/home/bogdan/Documents/UofT/PhD/Data_Files/TorontoHarbour-bathymetry/TorHarb_1h_HeatMaps_TS_OUT"

        # convert /home/bogdan/Documents/UofT/PhD/Data_Files/TorontoHarbour-bathymetry/TorHarb_1h_HeatMaps_TS/TH_1h_001.png -size 800x506 -font Bookman-DemiItalic -pointsize 16 -draw "text 50,100 '13-08-12 00:00:00'" /home/bogdan/Documents/UofT/PhD/Data_Files/TorontoHarbour-bathymetry/TorHarb_1h_HeatMaps_TS/TH_1h_001_1.png
        for j in range(0, len(ts)):
            text = "text 50,100 '" + ts[j] + "'"
            fn = imgdir + "/TH_1h_%03d.png" % (j + 1)
            fn_out = imgdir_out + "/TH_1h_%03d.png" % (j + 1)
            arg = fn + " -size 800x506 -font Bookman-DemiItalic -pointsize 16 -draw \"" + text + "\" " + fn_out
            cmd = "convert " + arg
            os.popen(cmd)

        print("Done Upwelling animation TIMESTAMP!")

    if rate:
        # Plot histogram of hourly rates
        percent = True
        delta = 1  # delta = 6
        date = ['13/06/17 00:00:00', '13/10/01 00:00:00']
        dt = datetime.datetime.strptime(date[0], "%y/%m/%d %H:%M:%S")
        start_num = dates.date2num(dt)
        dt = datetime.datetime.strptime(date[1], "%y/%m/%d %H:%M:%S")
        end_num = dates.date2num(dt)

        paths = []

        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Carleton-Nov2013/csv_processed/ShelteredOuterHarbour'
        # upw.plot_temp_rate(path, [start_num, end_num], Upwelling.window_halfhour, Upwelling.windows[1], tunits = 'hour', percent = percent, delta = delta)
        paths.append(path)

        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/csv_processed/BottomGradient'
        # upw.plot_temp_rate(path, [start_num, end_num], Upwelling.window_halfhour, Upwelling.windows[1], tunits = 'hour', percent = percent, delta = delta)
        paths.append(path)

        # path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/csv_processed/AboveBottomGradient'
        # upw.plot_temp_rate(path, [start_num, end_num], Upwelling.window_halfhour, Upwelling.windows[1], tunits = 'hour', percent = percent, delta = delta)
        # paths.append(path)

        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Carleton-Nov2013/csv_processed/InnerHarbour'
        # upw.plot_temp_rate(path, [start_num, end_num], Upwelling.window_halfhour, Upwelling.windows[1], tunits = 'hour', percent = percent, delta = delta)
        paths.append(path)

        upw.plot_temp_rate(paths, [start_num, end_num], Upwelling.window_halfhour, Upwelling.windows[1], tunits = 'hour', \
                            percent = percent, delta = delta)


    if show_timeseries:
        date = ['13/06/30 00:00:00', '13/08/24 00:00:00']
        exclude_min = { "Bot_TC4.csv":[3, 7], "Bot_St21.csv":[3] }
        # filtering
        timeavg = Upwelling.window_hour
        timeavg = Upwelling.window_3days
        timeavg = Upwelling.window_6hour
        timeavg = Upwelling.window_day

        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/csv_processed'
        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/csv_processed/Bottom'
        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/csv_processed/AboveBottom'
        location = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/location.csv'

        peaks = True # peaks nees to be True to calculate the velosities
        [a_max, a_min, afnames] = upw.detect_bottom_loggers_min_temp(path, date, filt, timeavg, peaks = peaks)

        if timeavg == Upwelling.window_3days or timeavg == Upwelling.window_6hour or timeavg == Upwelling.window_day:
            for i in range(0, len(a_max)):
                print("max : %s, len=%d" % (afnames[i], len(a_max[i])))

            for i in range(0, len(a_min)):
                print("min i: %s, len=%d" % (afnames[i], len(a_min[i])))

            [locations, lat, lon] = upw.get_lat_lon(location)
            upw.determine_velocity(a_max, a_min, afnames, locations, lat, lon, exclude_min)
        # end if
    # endif

    if CB_heatmap:
        # draw the temperature heatmap for 3 Cherry Beach goggers spaced 1 m apart on vertical starting from bottom
        ipath = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/csv_processed/CherryBeach'
        startdate = '13/05/01 00:00:00'
        enddate = '13/10/24 00:00:00'

        dt = datetime.datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
        start_num = dates.date2num(dt)
        dt = datetime.datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
        end_num = dates.date2num(dt)

        t11 = ['0', '2', '4', '6', '8', '10']
        t12 = [ 10, 8, 6, 4, 2, 0]
        tick = [t11, t12]
        maxdepth = 10
        firstlogdepth = 8
        maxtemp = 30
        upw.draw_isotherms(ipath, [start_num, end_num], tick, maxdepth, firstlogdepth, maxtemp, title = "Cherry Beach")

    if EG_heatmap or WG_heatmap:
        # draw the temperature heatmap for 3 Cherry Beach goggers spaced 1 m apart on vertical starting from bottom

        startdate = '13/05/01 00:00:00'
        enddate = '13/10/24 00:00:00'

        dt = datetime.datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
        start_num = dates.date2num(dt)
        dt = datetime.datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
        end_num = dates.date2num(dt)
        t11 = ['0', '1', '2', '3', '5']
        t12 = [ 5, 4, 3, 2, 1, 0]
        tick = [t11, t12]
        maxdepth = 5
        firstlogdepth = 0
        maxtemp = 30

        if EG_heatmap:
            ipath = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/AllHarbour/csv_processed/EGap'
            upw.draw_isotherms(ipath, [start_num, end_num], tick, maxdepth, firstlogdepth, maxtemp, title = "Eastern Gap")
        if WG_heatmap:
            ipath = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/AllHarbour/csv_processed/WGap'
            upw.draw_isotherms(ipath, [start_num, end_num], tick, maxdepth, firstlogdepth, maxtemp, title = "Western Gap")

    if JarvDock_heatmap:
        # draw the temperature heatmap for 3 Cherry Beach goggers spaced 1 m apart on vertical starting from bottom
        ipath = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/AllHarbour/csv_processed/JarvDock'
        startdate = '13/05/01 00:00:00'
        enddate = '13/10/24 00:00:00'

        dt = datetime.datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
        start_num = dates.date2num(dt)
        dt = datetime.datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
        end_num = dates.date2num(dt)
        t11 = ['0', '3', '6', '9']
        t12 = [ 9, 6, 3, 0]
        tick = [t11, t12]
        maxdepth = 9
        firstlogdepth = 5
        maxtemp = 30
        upw.draw_isotherms(ipath, [start_num, end_num], tick, maxdepth, firstlogdepth, maxtemp)

    if OutHarb_heatmap:
        # draw the temperature heatmap for 3 Cherry Beach goggers spaced 1 m apart on vertical starting from bottom
        # ipath = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/colormap/bot'
        ipath = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/colormap'

        # full timeseries
        startdate = '13/04/30 00:00:00'
        enddate = '13/10/27 00:00:00'

        # 1 upwellings
        # startdate = '13/09/02 00:00:00'
        # enddate = '13/09/07 00:00:00'


        dt = datetime.datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
        start_num = dates.date2num(dt)
        dt = datetime.datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
        end_num = dates.date2num(dt)
        t11 = ['TC4', 'St21', 'TC3', 'TC2', 'TC1', 'CB']
        t12 = [ 1, 3, 5 , 7, 9, 11 ]
        tick = [t11, t12]
        maxdepth = 12
        firstlogdepth = 0
        maxtemp = 20
        interpolate = None  # 4
        draw_lines = True
        line_divisor = 2
        upw.draw_isotherms(ipath, [start_num, end_num], tick, maxdepth, firstlogdepth, maxtemp, thermocline = False, \
                            interpolate = interpolate, draw_lines = draw_lines, line_divisor = line_divisor)

    if filter_data:
        timeavg = None
        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/csv_processed/Filter'
        dateTimeArr, tempArr, windowedArr, k, fnames = upw.get_timeseries_data(path, [start_num, end_num], timeavg, upw.windows[1])

        filt = "poincare"
        filt = "h0.5_1.5"
        filt = 'h2_10'
        filt = 'semidiurnal'
        filt = 'h10_16'
        filt = 'h18_30'
        filt = 'diurnal'
        filt = 'k3_7'
        filt = 'k10_15'
        ylim = [-3, 3]
        upw.plot_filtered_data(dateTimeArr, tempArr, fnames, k, filt, ylim)

    if spectral_harbour:
        path = "/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Spectral_Temp/Deep"
        names = ['Tc3' , 'Jarvis Dock', 'Lake Ontario']
        ##names = ['Cherry Beach' , 'Jarvis Dock', 'Lake Ontario']
        
        #path = "/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Spectral_Temp/Surface"
        #names = ['Embayment A', 'Ferry Term.', 'Lake Ontario']
        ##names = ['Cherry Beach', 'Ferry Term.', 'Lake Ontario']
        
        
        #log = False
        log = 'log'
        log='linear'
        withci = True
        base, dirs, files = next(iter(os.walk(path)))
        sorted_files = sorted(files, key = lambda x: x.split('.')[0])

        upw.spectral_analysis(path, sorted_files, names, log, withci)

    if spectral_PE:
        water_path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-LakeOntario/csv_processed'
        harbour_path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/AllHarbour/csv_processed/EGap-JarvisDock'
        name = "Lake Ontario"
        name = "Toronto Harbour"
        
        str_date = ['13/05/10 00:00:00', '13/10/27 00:00:00']
        # date = ['12/04/30 00:00:00', '12/10/27 00:00:00']  # 2012
        # stratified profile
        #date = ['13/06/30 00:00:00', '13/09/07 00:00:00']
        upw.spectral_PE(water_path, harbour_path, name, str_date)

                    
    if correlation_curr_temp:

        # full timeseries
        startdate = '13/06/25 00:00:00'
        enddate = '13/10/09 00:00:00'
        dt = datetime.datetime.strptime(startdate, "%y/%m/%d %H:%M:%S")
        start_num = dates.date2num(dt)
        dt = datetime.datetime.strptime(enddate, "%y/%m/%d %H:%M:%S")
        end_num = dates.date2num(dt)

        window = '1H'

        # ADCP velocity data path
        path = "/software/SAGEwork/rdrADCP"
        # bin_no = [1, 2, 3, 4]
        bin_no = [4]

        reader_obj = utools.custom_csv_readers.Read_ADCP_WrittenData(path, 'northVel.csv', start_num, end_num, bin_no)
        nvel_ts = utools.timeseries_correlation.LimnologyTimesSeries(reader_obj, window)

        # Temperature data path EGap 2 m depth S/N 10098821
        path = "/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/AllHarbour/csv_processed"
        filenames = ['10098822.csv']
        # filenames = ['10098822.csv', '10098823.csv', '10098821.csv', '10098825.csv']

        # path = "/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/csv_processed"
        # filenames = '10298872.csv',

        reader_obj = utools.custom_csv_readers.Read_Temp_Data_2013(path, filenames, start_num, end_num)
        temp_ts = utools.timeseries_correlation.LimnologyTimesSeries(reader_obj, window)

        method = 'pearson'
        # method = 'spearman'

        # best with pandas
        # '10098822.csv', 'northVel.csv' +  bin 4, window = 1H lag= 14  avarage_int = hour => corr =31%

        # best with Emery & Thomson
        # '10098822.csv', 'northVel.csv' +  bin 4, window = 1H lag= 66  avarage_int = hour => corr =60.96%


        lag = 13

        r = utools.timeseries_correlation.LimnologyTimesSeries.cross_corr_func(nvel_ts, temp_ts, 150)
        print("cross corr func (lag) = %f" % r)

        r = utools.timeseries_correlation.LimnologyTimesSeries.pearson_corr_coeff(nvel_ts, temp_ts, lag)
        print("pearson corr coef r=%f" % r)

        r = utools.timeseries_correlation.LimnologyTimesSeries.normalized_cross_corr_coeff(nvel_ts, temp_ts, 150)
        print("normalized cross corr f(lag) = %f" % r)

        average_interval = 'hour'
        # average_interval = 'second'
        # average_interval = 'minute'
        # average_interval = 'day'
        # average_interval = None
        r = utools.timeseries_correlation.LimnologyTimesSeries.corr(nvel_ts, temp_ts, method, lag, average_interval)
        print("Pandas r=%f" % r)

        cv = utools.timeseries_correlation.LimnologyTimesSeries.cov(nvel_ts, temp_ts, lag)
        print("Pandas cov=%f" % cv)

#===============================================================================
#         r = np.correlate(nvel_ts.data, temp_ts.data, mode = 'valid', old_behavior = False)
#         print "scipy xcorr = ", r
#
#         r = sp.signal.fftconvolve(temp_ts.data, nvel_ts.data, mode = 'valid')
#         print "scipy fftconv = ", r
#
#         xcorr = lambda x, y : np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(y[::-1]))
#         print "cross corr FFT", xcorr(temp_ts.data, nvel_ts.data)
#===============================================================================

        r = np.corrcoef(temp_ts.data[:-1], nvel_ts.data)
        print("numpy xcorr coef = ", r)
