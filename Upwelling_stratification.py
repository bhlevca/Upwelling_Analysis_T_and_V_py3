'''
Created on Dec 21, 2013

@author: bogdan
'''

# libraries
import numpy as np
import gsw
import csv
import os
import datetime
import matplotlib.dates as dates

# local
import upwelling
import readTempHoboFiles
import display_data


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

        dateTime, temp, results, k , fnames = readTempHoboFiles.read_files(moving_avg, window, [date[0], date[1]], path)

        return dateTime, temp, results, k, fnames


    def draw_isotherms(self, path, timeint, tick, maxdepth, firstlogdepth, maxtemp):
        # dirlist needs to be sorted in ascending order
        # Separate directories from files
        base, dirs, files = iter(os.walk(path)).next()

        sorted_files = sorted(files, key = lambda x: x.split('.')[0])

        dateTimeArr = np.zeros(len(sorted_files), dtype = np.ndarray)
        tempArr = np.zeros(len(sorted_files), dtype = np.ndarray)
        resultsArr = np.zeros(len(sorted_files), dtype = np.ndarray)
        k = np.zeros(len(sorted_files), dtype = np.ndarray)
        i = 0
        for fname in sorted_files:
            dateTime, temp, results = readTempHoboFiles.get_data_from_file(fname, self.window_hour, self.windows[1], timeinterv = timeint, rpath = path)
            maxidx = 30000
            dateTimeArr[i] = np.append(dateTimeArr[i], dateTime[:maxidx])
            resultsArr[i] = np.append(resultsArr[i], results[:maxidx])
            tempArr[i] = np.append(tempArr[i], temp[:maxidx])
            k[i] = np.append(k[i], i)
            i += 1
        # end for

        # plot the temperature not the smoothed ones
        datetype = 'dayofyear'
        display_data.display_temperatures(dateTimeArr, tempArr, k, fnames = sorted_files, custom = "Temperature Toronto Waterfront Zones", \
                                      datetype = datetype, ylab = "Temperature ($^oC$")

        display_data.display_img_temperatures(dateTimeArr, tempArr, resultsArr, k, tick, maxdepth, firstlogdepth, maxtemp, revert = True, fontsize = 18, datetype = datetype)


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

        ifile = open(file, 'rb')
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

    def determine_temp_gradient(self, dateTime, results, grad, tg):
        '''
        '''

        ymax = 0
        ymin = 0

        for i in range(len(dateTime)):
            k = 0
            t = dateTime[i]
            T = results[i]
            dt_hour = (t[2] - t[1]) * 24

            hour = 0

            for j in range(1, len(t) - 1):
                # cummulate an hour
                hour += dt_hour
                if j == 1:
                    Ti = T[j]
                if hour >= 1:
                    Tf = T[j]
                    grad[i] = np.append(grad[i], (Tf - Ti))
                    tg[i] = np.append(tg[i], t[j])
                    Ti = Tf
                    k += 1
                    hour = 0

            # resize the array
            grad[i] = np.resize(grad[i], k - 1)
            tg[i] = np.resize(tg[i], k - 1)
            ymax = np.maximum(ymax, np.amax(grad[i], axis = 0))
            ymin = np.minimum(ymin, np.amin(grad[i], axis = 0))

        return grad, tg, ymax, ymin

    def plot_temp_gradient(self, path, date, filt, timeavg, window, tunits = 'day', percent = False):

        startdate, enddate = date

        lowcut = self.filter[filt]['lowcut']
        highcut = self.filter[filt]['highcut']
        filter = [lowcut, highcut]

        minorgrid = 'mondays'
        datetype = 'dayofyear'
        dateTime, temp, results, k, fnames = self.get_timeseries_data(path, date, timeavg, window)

        grad = np.zeros(len(dateTime), dtype = np.ndarray)
        tg = np.zeros(len(dateTime), dtype = np.ndarray)
        ghist = np.zeros(len(dateTime), dtype = np.ndarray)
        edges = np.zeros(len(dateTime), dtype = np.ndarray)
        bins = np.zeros(len(dateTime), dtype = np.ndarray)

        if tunits == 'day':
            factor = 86400
        elif tunits == 'hour':
            factor = 3600
        else:
            factor = 1

        grad, tg, ymax, ymin = self.determine_temp_gradient(dateTime, results, grad, tg)

        # put data in bins
        for i in range(len(dateTime)):
            # put data in bins
            edges[i] = [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5 , 6, 7]
            grange = [ymin, ymax]
            ghist[i], edges[i] = np.histogram(grad[i], bins = edges[i], range = grange)

            bins[i] = edges[i][:-1]

            if percent:
                total = 0.0
                for j in range(0, len(ghist[i])):
                    total += ghist[i][j]
                for j in range(0, len(ghist[i])):
                    ghist[i][j] = ghist[i][j] / total * 100.0

        ylab = 'Temperature gradient ($^\circ$C/h)'
        display_data.display_temperatures(tg, grad, k, fnames, False, difflines = False, custom = '', maxdepth = None, \
                                           tick = None, firstlog = None, fontsize = 16, ylim = [ymin - 1, ymax + 1], fill = False, \
                                           show = True, datetype = "dayofyear", minorgrid = "mondays", ylab = ylab)

        display_data.display_marker_histogram(bins, ghist, fnames, xlabel = 'Temperature gradient ($^\circ$C/h)', ylabel = "Frequency (%)", \
                                              title = None, log = True, grid = True, fontsize = 18)


        #=======================================================================

    def determine_velocity(self, a_max, a_min, afnames, location, lat, lon, exclusions):

        # reareange a_min eliminating exclusions

        for i in range(0, len (a_min)):
            name = afnames[i]
            try:
                min_list = exclusions[name]
            except:
                continue
            a_min[i] = np.delete(a_min[i], min_list, 0)

                # calculate distances
        distances = gsw.distance(lon, lat, 0)
        print "distances", distances,
        print "names", afnames

        # calculate velocities u=D/t  i is the location  the length of each a_min is the number of peaks
        dt = [[] for i in range(len (a_min))]
        v = [[] for i in range(len (a_min))]
        for i in range(0, len (a_min) - 1):  # iterate on places
            name = afnames[i]
            for j in range(0, len(a_min[0])):  # iterate on min points at each place
                print i, ':', j
                dt[i].append((a_min[i + 1][j][0] - a_min[i][j][0]) * 3600 * 24)  # sec
                print "a_min[%d ] (%f)- a_min[%d ] (%f) = %f" % (i + 1, a_min[i + 1][j][0], i, a_min[i][j][0], (a_min[i + 1][j][0] - a_min[i][j][0]) * 3600 * 24)
        for i in range(0, len (a_min) - 1):  # iterate on places
            for j in range(0, len(a_min[0])):  # iterate on min points at each place
                v[i].append(distances[0][i] / dt[i][j])
                print "velocity at %s to %s (dist = %f)  event[%d] = %f (m/s)" % (afnames[i], afnames[i + 1], distances[0][i], j, v[i][j])

        print "------------------------------------------------------------------------------"

        for j in range(len (a_min[0])):
            if j == 0:
                for i in range(0, len (a_min) - 1):  # iterate on places
                    print '%12s | ' % afnames[i],
            print
            print "-----------------------------------------------------------------------------"
            for i in range(0, len (a_min) - 1):  # iterate on places
                print "%12.4f | " % (v[i][j]),

        # end for
        print
        print "-----------------------------------------------------------------------------"

    def plot_filtered_data(self, dateTimeArr, tempArr, fnames, k, filt, ylim):

        lowcut = self.filter[filt]['lowcut']
        highcut = self.filter[filt]['highcut']
        filter = [lowcut, highcut]

        upwelling.plot_buterworth_filtered_data(dateTimeArr, tempArr, fnames, k, filter, ylim)


    def calculate_avg_maxgrd_max_min(self, path, date, timeavg, window):
        '''
        Calculate average temperatures, max gradient, max temperature and min temperatures
        '''

        # get the data
        dateTime, temp, results, k, fnames = self.get_timeseries_data(path, date, timeavg, window)


        # calculate max & min gradient
        grad = np.zeros(len(dateTime), dtype = np.ndarray)
        tg = np.zeros(len(dateTime), dtype = np.ndarray)
        grad, tg, ymax, ymin = self.determine_temp_gradient(dateTime, results, grad, tg)


        maxidx = len(results)
        for i in range(0, len(results)):
            print "fname %s, len:%d" % (fnames[i], len(results[i]))
            maxidx = min(maxidx, len(temp[i]))

        mean_temp = np.zeros(maxidx)
        max_temp = np.zeros(maxidx)
        min_temp = np.zeros(maxidx)
        max_grad = np.zeros(maxidx)

        for i in range(0, len(results)):
            # calculate mean
            mean_temp[i] = np.mean(results[i][1:])

            # calculate max
            max_temp[i] = np.amax(results[i][1:])  # along the time line not the stations

            # calculate min
            min_temp[i] = np.amin(results[i][1:])  # along the time line not the stations

            # calculate max grad
            max_grad[i] = np.max(np.abs(grad[i][1:]))  # along the time line not the stations

        for i in range(0, maxidx):
            print "Stn %s : mean_temp:%2.2f  max_temp:%2.2f  min_temp:%2.2f  max_grad:%2.2f" \
                % (fnames[i], mean_temp[i], max_temp[i], min_temp[i], max_grad[i])


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

    def correlate_N2_with_upwelling_velocity(self):
        '''
        Create a correlation , unfortunately will be 5 or 6 points corresponding to the velocity of the upwelling
        event and the N2 (stratification frequency) - either at thermocline or an average of the column?

        Correlate with velocity and  temperature drop
        '''
        pass

    def correlate_meteo_with_temperature_variability(self):
        '''
        get meteo : wind (speed and dir), air temp, solar radiation, arit pressure
        correlate (with time lag) with the water temperature (surface and benthic)
        '''
        pass

    def test(self):
        sal = np.array([0.1, 0.1])  #
        temp = np.array([4., 21.])  # Celsius
        pres = np.array([10., 20.])
        rho = gsw.rho(sal, temp, pres)
        print "density", rho

        lat = [43.2, 43.2]
        CT = gsw.CT_from_t(sal, temp, pres)
        N2, p_mid = gsw.Nsquared(sal, CT, pres, lat = lat)
        print "N2", N2
        print "p_mid", p_mid

if __name__ == '__main__':

    # set what we want to do - Shouldd be controlled by cmd line args
    ###########################################################
    climate = False
    gradient = True
    show_timeseries = False
    CB_heatmap = False
    EG_heatmap = False
    JarvDock_heatmap = False
    filter_data = False


    ############################################################
    # initilize object
    upw = Upwelling("")
    # upw.test()
    # upw.Nsquared()

    # date = ['13/05/19 00:00:00', '13/10/24 00:00:00']
    # exclude_min = []


    filt = "semidiurnal"

    if climate:
        date = ['13/05/20 00:00:00', '13/09/10 00:00:00']
        dt = datetime.datetime.strptime(date[0], "%y/%m/%d %H:%M:%S")
        start_num = dates.date2num(dt)
        dt = datetime.datetime.strptime(date[1], "%y/%m/%d %H:%M:%S")
        end_num = dates.date2num(dt)
        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/ClimateMap'
        timeavg = Upwelling.window_hour
        upw.calculate_avg_maxgrd_max_min(path, [start_num, end_num], timeavg, upw.windows[1])

    if gradient:

        percent = True
        date = ['13/06/17 00:00:00', '13/10/01 00:00:00']
        dt = datetime.datetime.strptime(date[0], "%y/%m/%d %H:%M:%S")
        start_num = dates.date2num(dt)
        dt = datetime.datetime.strptime(date[1], "%y/%m/%d %H:%M:%S")
        end_num = dates.date2num(dt)

        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/csv_processed/BottomGradient'
        # upw.plot_temp_gradient(path, [start_num, end_num], filt, Upwelling.window_halfhour, Upwelling.windows[1], tunits = 'hour', percent=percent)

        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/csv_processed/AboveBottomGradient'
        # upw.plot_temp_gradient(path, [start_num, end_num], filt, Upwelling.window_halfhour, Upwelling.windows[1], tunits = 'hour', percent=percent)

        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Carleton-Nov2013/csv_processed/ShelteredOuterHarbour'
        # upw.plot_temp_gradient(path, [start_num, end_num], filt, Upwelling.window_halfhour, Upwelling.windows[1], tunits = 'hour', percent=percent)

        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Carleton-Nov2013/csv_processed/InnerHarbour'
        upw.plot_temp_gradient(path, [start_num, end_num], filt, Upwelling.window_halfhour, Upwelling.windows[1], tunits = 'hour', percent = percent)


    if show_timeseries:
        exclude_min = { "Bot_TC4.csv":[3, 7], "Bot_St21.csv":[3] }
         # filtering
        timeavg = Upwelling.window_hour
        # timeavg = Upwelling.window_3days

        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/csv_processed'
        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/csv_processed/Bottom'
        path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/csv_processed/AboveBottom'
        location = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/location.csv'

        peaks = False
        [a_max, a_min, afnames] = upw.detect_bottom_loggers_min_temp(path, date, filt, timeavg, peaks = peaks)

        if timeavg == Upwelling.window_3days:
            for i in range(0, len(a_max)):
                print "max : %s, len=%d" % (afnames[i], len(a_max[i]))

            for i in range(0, len(a_min)):
                print "min i: %s, len=%d" % (afnames[i], len(a_min[i]))

            [locations, lat, lon] = upw.get_lat_lon(location)
            upw.determine_velocity(a_max, a_min, afnames, locations, lat, lon, exclude_min)
        # end if

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
        upw.draw_isotherms(ipath, [start_num, end_num], tick, maxdepth, firstlogdepth, maxtemp)

    if EG_heatmap:
        # draw the temperature heatmap for 3 Cherry Beach goggers spaced 1 m apart on vertical starting from bottom
        ipath = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/AllHarbour/csv_processed/EGap'
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
        upw.draw_isotherms(ipath, [start_num, end_num], tick, maxdepth, firstlogdepth, maxtemp)

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
