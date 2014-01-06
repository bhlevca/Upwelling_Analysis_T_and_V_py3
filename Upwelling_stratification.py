'''
Created on Dec 21, 2013

@author: bogdan
'''

import numpy as np
import gsw

class Upwelling(object):
    '''
    classdocs
    '''


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
    upw.test()
    # upw.Nsquared()
