#!/usr/bin/python

#
# $Id: peaks.py,v 1.4 2009-04-29 09:32:04 dintrans Exp $
# Plot the time evolution of <rho*uz> and compare it to an exponential law
#

import pylab as P
import numpy as N

data=N.loadtxt('data/time_series.dat', comments='#')
t=data[:, 1]
ruzm=data[:, 3]
#
#  find the peaks
#
fmax=N.zeros(1, dtype='Float32')
tt=fmax
for i in range(1,len(ruzm)-1):
  if (ruzm[i] > ruzm[i+1] and ruzm[i] > ruzm[i-1] ):
     fmax=N.append(fmax, ruzm[i])
     tt=N.append(tt, t[i])
# remove the first elements that is null
fmax=fmax[1:] ; tt=tt[1:]

tmin=10 ; tmax=tt[-1]
i1=((N.where(tt>=tmin))[0])[0]
i2=((N.where(tt>=tmax))[0])[0]
print "tmin=%6.2f  tmax=%6.2f"%(tt[i1], tt[i2])
a, b=N.polyfit(tt[i1:i2], N.log(fmax[i1:i2]), 1)
print 'slope=', a, b 

P.plot(t, ruzm, 'k')
P.plot(tt, fmax)
P.plot(tt[tt>=tmin], fmax[tt>=tmin])
P.plot(tt[tt>=tmin], fmax[tt>=tmin], 'o')
P.plot(tt[tt>=tmin], N.exp(a*tt[tt>=tmin]+b),'r--')
P.xlabel('time')
P.ylabel(r'$<\rho u_z>$')
P.title('Evolution of the vertical momentum')
P.show()

