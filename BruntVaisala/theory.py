import numpy as N

def theory(kk, cs, Lx):
  """
  $Id: theory.py,v 1.3 2009-04-27 10:29:47 dintrans Exp $
  theory(kk, cs, Lx): compute the g-modes of an isothermal atmosphere
  kk: horizontal wavenumber
  cs: sound speed
  Lx: width in the x-direction
  """

  gamma=5./3.
  haut=cs**2/gamma ; bv2=(1.-1./gamma)/haut
  bv=N.sqrt(bv2)

  kx=2*N.pi/Lx*kk
  nn=N.arange(5)
  kz=(nn+1)*N.pi
  k2=kx**2+kz**2
  # (-) is for g-modes, (+) for p-modes
  a=cs**2*(k2+0.25/haut**2)-cs*N.sqrt(cs**2*(k2+0.25/haut**2)**2-4*kx**2*bv2)
  wth=N.sqrt(0.5*a)
  for i in range(5):
    print 'kk=%i  n=%i  wth=%8.5f'%(kk, nn[i], wth[i])

  return wth, bv, haut
