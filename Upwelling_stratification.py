'''
Created on Dec 21, 2013

@author: bogdan
'''

# libraries
import numpy as np
import gsw
import csv

# local
import upwelling


class Upwelling(object):
    '''
    classdocs
    '''
    windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
    window_6hour = "window_6hour"  # 30 * 6 for a 2 minute sampling
    window_hour = "window_hour"  # 30
    window_day = "window_day"  # 30 * 24
    window_half_day = "window_half_day"  # 30 * 12
    window_3days = "window_3days"  # 3 * 30 * 24
    window_7days = "window_7days"  # 7 * 30 * 24

    filter = {
              'k3_7' : {  # Kelvin 3-7 days
                       'lowcut' :1.0 / (24 * 10) / 3600,
                       'highcut' :1.0 / (24 * 3) / 3600
              },
              'k10_15' :{  # Kelvin 10-15 days
                          'lowcut' :1.0 / (24 * 15) / 3600,
                          'highcut' : 1.0 / (24 * 10) / 3600
              },
              'poincare': {  # poincare
                            'lowcut': 1.0 / (17.3) / 3600,
                            'highcut' :1.0 / (16.6) / 3600
              },
              'diurnal' : {  # diurnal
                           'lowcut' : 1.0 / (24.2) / 3600,
                           'highcut' : 1.0 / (23.8) / 3600
              },
              'semidiurnal': {  # 12 hours
                              'lowcut' : 1.0 / (12.1) / 3600,
                              'highcut' : 1.0 / (11.9) / 3600
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

    def detect_bottom_loggers_min_temp(self, path, date, filt, timeavg):
        '''
        Detect the minimum temperature at each bottom logger using a synoptic (7-14 days) running mean for
        determining the upwelling propagation velocities
        '''

        startdate, enddate = date

        lowcut = self.filter[filt]['lowcut']
        highcut = self.filter[filt]['highcut']
        filter = [lowcut, highcut]


        # upwelling.read_Upwelling_files(path, [startdate, enddate], timeavg = timeavg, subplot = None, filter = filter, fft = False, stats = True, with_weather = False)
        [a_max, a_min, afnames] = upwelling.plot_Upwelling_one_fig(path, [startdate, enddate], timeavg = timeavg, subplot = None, filter = filter, fft = False, stats = True, with_weather = False)
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
                dt[i].append((a_min[i + 1][j][0] - a_min[i][j][0]) * 3600 * 24)  # sec
                # print "a_min[%d ] (%f)- a_min[%d ] (%f) = %f" % (i + 1, a_min[i + 1][j][0], i, a_min[i][j][0], (a_min[i + 1][j][0] - a_min[i][j][0]) * 3600 * 24)
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
    upw = Upwelling("")
    # upw.test()
    # upw.Nsquared()

    # date = ['13/05/19 00:00:00', '13/10/24 00:00:00']
    # exclude_min = []
    date = ['13/06/17 00:00:00', '13/10/01 00:00:00']
    exclude_min = { "Bot_TC4.csv":[3, 7], "Bot_St21.csv":[3] }
     # filtering
    filt = "semidiurnal"
    timeavg = Upwelling.window_3days

    path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/csv_processed'
    path = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/csv_processed/Bottom'
    location = '/home/bogdan/Documents/UofT/PhD/Data_Files/2013/Hobo-Apr-Nov-2013/TC-OuterHarbour/location.csv'

    [a_max, a_min, afnames] = upw.detect_bottom_loggers_min_temp(path, date, filt, timeavg)

    for i in range(0, len(a_max)):
        print "max : %s, len=%d" % (afnames[i], len(a_max[i]))

    for i in range(0, len(a_min)):
        print "min i: %s, len=%d" % (afnames[i], len(a_min[i]))

    [locations, lat, lon] = upw.get_lat_lon(location)

    upw.determine_velocity(a_max, a_min, afnames, locations, lat, lon, exclude_min)
