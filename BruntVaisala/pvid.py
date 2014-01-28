#!/usr/bin/env python

#
# $Id: pvid.py,v 1.5 2009-08-27 08:11:08 dintrans Exp $
# Animate the entropy snapshots with the velocity field superimposed
#

import numpy as N
import pylab as P
import pencil as pc

ss, t = pc.read_slices(field='ss', proc=0)
ux, t = pc.read_slices(field='uu1', proc=0)
uz, t = pc.read_slices(field='uu3', proc=0)

dim=pc.read_dim()
par=pc.read_param(quiet=True)
par2=pc.read_param(quiet=True, param2=True)
grid=pc.read_grid(param=par, quiet=True, trim=True)
nt=len(t)
ss=ss.reshape(nt, dim.nz, dim.nx)
ux=ux.reshape(nt, dim.nz, dim.nx)
uz=uz.reshape(nt, dim.nz, dim.nx)

qs1=N.random.random_integers(0,dim.nx-1, 1000)
qs2=N.random.random_integers(0,dim.nz-1, 1000)
xx,zz=P.meshgrid(grid.x, grid.z)
frame=par.xyz0[0],par.xyz1[0],par.xyz0[2],par.xyz1[2]

P.ion()
im=P.imshow(ss[0,...], extent=frame, origin='lower', aspect='auto')
a=ux[0, qs2, qs1]**2+uz[0, qs2, qs1]**2 ; norm=N.sqrt(a.max())
ux[0, qs2, qs1]=ux[0, qs2, qs1]/norm
uz[0, qs2, qs1]=uz[0, qs2, qs1]/norm
vel=P.quiver(xx[qs2, qs1], zz[qs2, qs1], ux[0, qs2, qs1],
uz[0, qs2, qs1], scale=7)
st=P.figtext(0.8,0.2,'t=%.1f'%t[0], color='w')
P.xlabel('x')
P.ylabel('z')

for i in range(1, nt):
  im.set_data(ss[i, ...])
  a=ux[i, qs2, qs1]**2+ux[i, qs2, qs1]**2 ; norm=N.sqrt(a.max())
  ux[i, qs2, qs1]=ux[i, qs2, qs1]/norm
  uz[i, qs2, qs1]=uz[i, qs2, qs1]/norm
  vel.set_UVC(ux[i, qs2, qs1], uz[i, qs2, qs1])
  st.set_text('t=%.1f'%t[i])

  P.draw()

P.show()
