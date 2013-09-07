import numpy
import scipy
import matplotlib.pyplot as plt
import sys

sys.path.insert(0, '/software/SAGEwork/Seiches')
import fft.filters as filters
import fft.fft_utils as fft_utils

fs = 100
T = 1.0
nsamples = T * fs
t = numpy.linspace(0, T, nsamples, endpoint = False)
# xs = numpy.arange(1, 100, 0.01)  # generate Xs (0.00,0.01,0.02,0.03,...,100.0)

# signal = sin1 = numpy.sin(xs * .3)  # (A)

sin1 = numpy.sin(2 * numpy.pi * t * 10) * 4.0  # (B) sin1

sin2 = numpy.sin(2 * numpy.pi * t * 20) * 2.0  # (B) sin2

sin3 = numpy.sin(2 * numpy.pi * t * 3) * 6.0  # (B) sin3

noise = sin1 + sin2 + sin3  # (C)


static = (numpy.random.random_sample((len(t))) - .5) * .2  # (D)

# sigstat = static + signal  # (E)

# rawsignal = sigstat + noise  # (F)

plt.plot(t, sin1, label = "sin1")
plt.plot(t, sin2, label = "sin2")
plt.plot(t, sin3, label = "sin3")

plt.plot(t, noise, label = 'raw')
plt.legend()
plt.show()


# for tobermory
T = 10000.0
nsamples = 10000
t = numpy.linspace(0, T, nsamples, endpoint = False)
sin1 = numpy.sin(2 * numpy.pi * t * 1. / (60. * 7.2) + numpy.pi / 4.) * 3.5  # (B) sin1
sin2 = numpy.sin(2 * numpy.pi * t * 1. / (60. * 16.8)) * 5.7  # (B) sin2

noise = sin1 + sin2
plt.plot(t, sin1, label = "sin1")
plt.plot(t, sin2, label = "sin2")
plt.plot(t, noise, label = 'raw')
plt.legend()
plt.show()


# highcut = 1.0 / (fnumber - delta) / 3600
# lowcut = 1.0 / (fnumber + delta) / 3600

highcut = 21
lowcut = 19

btype = 'band'


yday = True
debug = False
order = None
gpass = 9
astop = 20
recurse = True



data1, w, h, N, delay1 = filters.butterworth(noise, btype, lowcut, highcut, fs, output = 'zpk', passatten = gpass, stopatten = astop, order = order, recurse = True, debug = debug)
plt.plot(t, data1)
plt.show()
