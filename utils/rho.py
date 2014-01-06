'''
Created on Dec 20, 2013

@author: bogdan@hlevca.com
'''
import numpy as np
import sys


def rho (s, t, p):
    '''
    % International Equation of State of sea water : rho=ies80(s,t,p)

    :param s: salinity
    :type s: float
    :param t: temperature (C)
    :type t: float
    :param p: pressure    (bars)
    :type p: float

    return
    :param rho:  density     (kg/m3)
    :type float

    %    rho,s,t,p can be vector or matrix
    %    rho=rho(s,t) use p=0 at athmospheric pressues

    %-----------------------------------
    % Original matlab code
    % Olivier Le Calve
    % E-mail : lecalve@isitv.univ-tln.fr
    %-----------------------------------
    '''
    r0_coef = np.array([999.842594, 6.793952e-2, -9.09529e-3, 1.001685e-4, -1.120083e-6, 6.536332e-9, 8.24493e-1, \
             - 4.0899e-3, 7.6438e-5, -8.2467e-7, 5.3875e-9, -5.72466e-3, 1.0227e-4, -1.6546e-6, 4.8314e-4])

    r0 = np.polyval(r0_coef[0:5][::-1], t) + \
       np.polyval(r0_coef[6:10][::-1], t) * s + \
       np.polyval(r0_coef[11:13][::-1], t) * s ** 1.5 + \
       r0_coef[14] * s ** 2


    K_coef = np.array([19652.21, 148.4206, -2.327105, 1.360447e-2, -5.155288e-5, 3.239908, 1.43713e-3, 1.16092e-4, -5.77905e-7, 8.50935e-5, \
            - 6.12293e-6, 5.2787e-8, 54.6746, -0.603459, 1.09987e-2, -6.1670e-5, 7.944e-2, 1.6483e-2, -5.3009e-4, 2.2838e-3, \
            - 1.0981e-5, -1.6078e-6, 1.91075e-4, -9.9348e-7, 2.0816e-8, 9.1697e-10])

    K = np.polyval(K_coef[0:4][::-1], t) + \
        np.polyval(K_coef[5:8][::-1], t) * p + \
        np.polyval(K_coef[9:11][::-1], t) * p ** 2 + \
        np.polyval(K_coef[12:15][::-1], t) * s + \
        np.polyval(K_coef[16:18][::-1], t) * s ** 1.5 + \
        np.polyval(K_coef[19:21][::-1], t) * p * s + \
        K_coef[22] * p * s ** 1.5 + \
        np.polyval(K_coef[23:25][::-1], t) * p ** 2 * s

    rho = r0 / (1 - p / K)

    # else:
    #    rho = r0

    return rho
    # end rho

if __name__ == '__main__':
    sal = np.array([0.0, 0.0])
    temp = np.array([4., 21.])
    pres = np.array([1., 1.])

    ro = rho(sal, temp, pres)
    print "rho" , ro
