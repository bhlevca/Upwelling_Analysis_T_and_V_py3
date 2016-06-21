#!/usr/bin/env python

#
# $Id: profile.py,v 1.3 2009-04-27 11:02:32 dintrans Exp $
# Vertical profile for uz by zooming around a given frequency
#

import numpy as N
import pylab as P
import pencil as pc
from scipy.integrate import simps
from theory import *

#
#  the input data
#
kx=1     # the horizontal wavenumber that we want study
node=0   # the mode order for the zoom
dw=5e-2  # the width in frequency for the zoom

uz, t = pc.read_slices(field='uu3', proc=0)

dim=pc.read_dim()
par=pc.read_param(quiet=True)
par2=pc.read_param(quiet=True, param2=True)
grid=pc.read_grid(param=par, quiet=True, trim=True)
nt=len(t)
uz=uz.reshape(nt, dim.nz, dim.nx)

w1 = N.empty((nt, dim.nz, dim.nx), dtype='Complex64')
for i in range(dim.nz):
  w1[:, i, :] = N.fft.fft2(uz[:, i, :])/nt/dim.nx
w2 = N.abs(w1[1:nt/2+1, ...])
dw = 2*N.pi/(t[-1]-t[0])
w = dw*N.arange(nt)
w = w[1:nt/2+1]

kmax=kx
inte = N.empty((nt/2, kmax+1), dtype='Float64')
for k in range(kmax+1):
  for i in range(nt/2):
    inte[i, k] = simps(w2[i, :, k], grid.z)

frame= par.xyz0[2], par.xyz1[2], w[0], 1

# theoretical frequencies of the g-modes
wth, bv, haut=theory(kx, par.cs0, par.lxyz[0])
P.subplot(311)
im=P.imshow(w2[w<1, :, kx], aspect='auto', origin='lower', 
extent=frame, cmap=P.get_cmap('binary'))
for n in range(3): P.axhline(wth[n], ls='--', color='b')
P.title('kx=%i'%kx)
P.xlabel('z')
P.ylabel('frequency')

# integrated spectrum
P.subplot(312)
P.semilogy(w[w < 1], inte[w < 1, kx])
for n in range(3): P.axvline(wth[n], ls='--', color='k')
P.xlabel('frequency')

#
#  vertical profile: zoom in around a given frequency
#
w0=wth[node] 
wmin=w0-dw ; wmax=w0+dw
ind = N.where(w >= wmin, 1, 0)*N.where(w <= wmax, 1, 0)
ind = N.asarray(N.nonzero(ind))[0, :]
print('Zoom in wth', w[ind])
f = w2[ind, :, kx]
prof = f.mean(axis=0)

P.subplot(313)
P.plot(grid.z, prof/prof.max(), label='simulation')
kz=(node+1)*N.pi
fth=N.exp(0.5*grid.z/haut)*N.cos(kz*grid.z)
P.plot(grid.z, fth/fth.max(), label='theory')
P.xlim(grid.z[0], grid.z[-1])
P.xlabel('z')
P.ylabel('$u_z$')
P.legend(loc='best')

P.subplots_adjust(hspace=0.35, left=0.1, right=0.98, top=0.95,
bottom=0.1)

P.show()

