# # Copyright (C) 2006 Stefan van der Walt <stefan@sun.ac.za>
# #
# # Redistribution and use in source and binary forms, with or without
# # modification, are permitted provided that the following conditions are
# # met:
# #
# #  1. Redistributions of source code must retain the above copyright
# #     notice, this list of conditions and the following disclaimer.
# #  2. Redistributions in binary form must reproduce the above copyright
# #     notice, this list of conditions and the following disclaimer in
# #     the documentation and/or other materials provided with the
# #     distribution.
# #
# # THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# # IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# # WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# # DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
# # INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# # (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# # SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# # HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# # STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# # IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# # POSSIBILITY OF SUCH DAMAGE.

import numpy as N

itype = N.uint16  # See ticket 225

def houghtf(img, angles = None):
    """Perform the straight line Hough transform.

    Input:
      img - a boolean array
      angles - in degrees

    Output:
      H - the Hough transform coefficients
      distances
      angles
    
    """
    if img.ndim != 2:
        raise ValueError("Input must be a two-dimensional array")

    img = img.astype(bool)

    if not angles:
        angles = N.linspace(-90, 90, 180)

    theta = angles / 180. * N.pi
    d = N.ceil(N.hypot(*img.shape))
    nr_bins = 2 * d - 1
    bins = N.linspace(-d, d, nr_bins)
    out = N.zeros((nr_bins, len(theta)), dtype = itype)

    rows, cols = img.shape
    x, y = N.mgrid[:rows, :cols]

    for i, (cT, sT) in enumerate(zip(N.cos(theta), N.sin(theta))):
        rho = N.round_(cT * x[img] + sT * y[img]) - bins[0] + 1
        rho = rho.astype(itype)
        rho[(rho < 0) | (rho > nr_bins)] = 0
        bc = N.bincount(rho.flat)[1:]
        out[:len(bc), i] = bc

    return out, angles, bins

if __name__ == '__main__':
    # Generate a test image
    img = N.zeros((100, 150), dtype = bool)
    img[30, :] = 1
    img[:, 65] = 1
    img[35:45, 35:50] = 1
    for i in range(90):
        img[i, i] = 1
    img += N.random.random(img.shape) > 0.95

    import pylab as P

    print "Performing straight line Hough transform on %s array..." % str(img.shape)
    out, angles, d = houghtf(img)

    P.subplot(121)
    P.imshow(img, cmap = P.cm.gray)
    P.subplot(122)
    P.imshow(out, cmap = P.cm.bone)
    P.xlabel('Angle (degree)')
    P.ylabel('Distance %d (pixel)' % d[0])
    P.show()
