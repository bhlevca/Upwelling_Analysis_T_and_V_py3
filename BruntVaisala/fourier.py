#!/usr/bin/env python

#
# $Id: fourier.py,v 1.3 2009-04-27 10:29:47 dintrans Exp $
# Fourier diagram of the vertical velocity
#

import numpy as N
import pylab as P
import pencil as pc
from scipy.integrate import simps
from theory import *

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

kmax=5
inte = N.empty((nt/2, kmax+1), dtype='Float64')
for k in range(kmax+1):
  for i in range(nt/2):
    inte[i, k] = simps(w2[i, :, k], grid.z)

#frame= par.xyz0[2], par.xyz1[2], w[0], w[-1]
frame= par.xyz0[2], par.xyz1[2], w[0], 1

iplot=1
for kx in range(1,4):
  # theoretical frequencies of the g-modes
  wth, bv, haut=theory(kx, par.cs0, par.lxyz[0])
  P.subplot(3, 2, iplot)
  im=P.imshow(w2[w<1, :, kx], aspect='auto', origin='lower', 
  extent=frame, cmap=P.get_cmap('binary'))
  for n in range(3): P.axhline(wth[n], ls='--', color='b')
  P.title('kx=%i'%kx)
  if (kx == 3): 
    P.xlabel('z')
    P.ylabel('frequency')

  # integrated spectrum
  P.subplot(3, 2, iplot+1)
  P.semilogy(w[w < 1], inte[w < 1, kx])
  for n in range(3): P.axvline(wth[n], ls='--', color='k')
  if (kx == 3): P.xlabel('frequency')
  iplot+=2

P.subplots_adjust(hspace=0.3, left=0.1, right=0.98, top=0.95,
bottom=0.1)
P.show()

