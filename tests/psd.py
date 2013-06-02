# This program below do reveal that mlab.psd and pyplot.psd are different
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
dt = np.pi / 100.
fs = 1. / dt
t = np.arange(0, 8, dt)
y = 10. * np.sin(2 * np.pi * 4 * t) + 5. * np.sin(2 * np.pi * 4.25 * t)
y = y + np.random.randn(*t.shape)
print "t=", t
print "y=", y
print "fs=", fs
# Plot the raw time series
fig = plt.figure()
fig.subplots_adjust(hspace = 0.6, wspace = 0.5)
#
ax = fig.add_subplot(3, 1, 1)
plt.title('Data')
ax.plot(t, y)

ax = fig.add_subplot(3, 1, 2)
plt.title('psd using pyplot')
ax.psd(y, Fs = fs, scale_by_freq = False)

ax = fig.add_subplot(3, 1, 3)
plt.title('psd using mlab')

x, y = mlab.psd(y, Fs = fs, scale_by_freq = False)
x = 10 * np.log10(np.absolute(x))
ax.plot(y, x)
plt.show()
