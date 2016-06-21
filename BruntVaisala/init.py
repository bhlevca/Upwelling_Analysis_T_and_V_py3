#!/usr/bin/python

#
# $Id: init.py,v 1.3 2009-04-27 11:02:31 dintrans Exp $
# Plot the initial setup for the isothermal atmosphere with an entropy
# bubble
#

import pencil as pc
import pylab as P

param=pc.read_param(quiet=True)
grid=pc.read_grid(trim=True,param=param,quiet=True)

frame=param.xyz0[0],param.xyz1[0],param.xyz0[2],param.xyz1[2]

var=pc.read_var(ivar=0,run2D=True,quiet=True,param=param,trimall=True,
magic=['rho'])

P.subplot(311)
im=P.imshow(var.ss, extent=frame, origin='lower', aspect='auto')
P.ylabel('z')
P.title('Initial entropy field')

P.subplot(312)
im=P.imshow(var.rho, extent=frame, origin='lower', aspect='auto')
P.xlabel('x')
P.ylabel('z')
P.title('Initial density field')

P.subplot(313)
ssm=var.ss.mean(axis=1)
rhom=var.rho.mean(axis=1)
jump=rhom[0]/rhom[-1]
print("density jump=rho_bot/rho_top=%6.2f"%jump)
P.plot(grid.z, ssm, label='entropy')
P.plot(grid.z, rhom, label='density')
P.legend(loc='best')
P.xlabel('z')

P.subplots_adjust(hspace=0.3, left=0.1, right=0.98, top=0.95,
bottom=0.05)
P.show()

