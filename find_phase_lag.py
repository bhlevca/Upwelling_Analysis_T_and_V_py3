'''
Autocorrelation test
'''

import math
import numpy as np
import matplotlib.pyplot as plt


def autocorr(x):
    result = np.correlate(x, x, mode = 'full')
    return result[result.size / 2:]

def xcorr(x, y):
    result = np.correlate(x, y, mode = 'full')
    return result[result.size / 2:]

Fs = 100e3
t = np.linspace(0, Fs, Fs)
x = np.sin(2 * math.pi * 30 * t + (15 * math.pi / 180))
y = np.sin(2 * math.pi * 30 * t)
c = xcorr(x, y)
# c = autocorr(x)

t1 = np.linspace (-100e3, 100e3, 100e3)
t1 = t1 / Fs * 2 * math.pi * 30

fig = plt.figure()
plt.plot(t1, c)
plt.show()

# [val, index]
val = np.amax(c)
index = np.argmax(c)
lag = t1[index]
ph = lag * 180 / math.pi
print 'Phase lag: %f' % lag
print 'Time lag: %f' % ph
