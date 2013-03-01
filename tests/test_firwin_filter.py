'''
The python code generates the Finite Impulse Response (FIR) filter coefficients for a lowpass filter (LPF)
at 10 (Hz) cut off using firwin from scipy. A highpass filter is then created by subtracting the lowpass filter
output(s) from the output of an allpass filter. To do this the coefficients of the LPF are multiplied by -1 and 1
added to the centre tap (to create the allpass filter with subtraction).

A second LPF is then created with a cutoff at 15 (Hz) and the bandpass filter formed by addition of the LPF and HPF coefficients.
'''
from numpy import cos, sin, pi, absolute, arange
from numpy.random import normal
from scipy.signal import kaiserord, lfilter, firwin, freqz
from pylab import figure, clf, plot, xlabel, ylabel, xlim, \
 ylim, title, grid, axes, show
from math import sqrt, log10

#----------------------------------------------------------
# Set the sampling frequency to 100. Sample period is 0.01.
# A frequency of 1 will have 100 samples per cycle, and
# therefore have 4 cycles in the 400 samples.


sample_rate = 100.0
nyq_rate = sample_rate / 2.0
nsamples = 400
t = arange(nsamples) / sample_rate

# t = 0.01,0.02.......4.0 (400 samples)

#----------------------------------------------------------
# Create a test signal at pass band centre plus gaussian
# noise. Check sigma = rms of generated samples


peak = 0.3
x = peak * sin(2 * pi * 12.5 * t)

mu, sigma = 0, 0.1  # mean and standard deviation
noise = normal(mu, sigma, 400)

squares = map(lambda x: x * x, noise)
# squares is list of the noise samples squared

total = sqrt(sum(squares) / 400)
snr = 10 * log10(0.707 * peak / total)
print 'rms noise = ', total
print 'signal to noise ratio', snr, ' dB'

x = [sum(pair) for pair in zip(x, noise)]

#------------------------------------------------
# First create a 10 (Hz) lowpass FIR filter
#------------------------------------------------

width = 5.0 / nyq_rate  # pass to stop transition width

# The desired attenuation in the stop band, in dB.
ripple_db = 55.0

# Compute the order and Kaiser parameter for the FIR filter.
N, beta = kaiserord(ripple_db, width)

print 'N = ', N, 'beta = kaiser param = ', beta

# The cutoff frequency of the filter.
cutoff_hz = 10.0

# Use firwin with a Kaiser window to create a lowpass FIR filter.
hpftaps = firwin(N, cutoff_hz / nyq_rate, window = ('kaiser', beta))

#----------------------------------------------------------
# now create the taps for a high pass filter.
# by multiplying tap coefficients by -1 and
# add 1 to the centre tap ( must be even order filter)

hpftaps = [-1 * a for a in hpftaps]
hpftaps[33] = hpftaps[33] + 1

#----------------------------------------------------------
# Now calculate the tap weights for a lowpass filter at say 15hz

cutoff_hz = 15.0
lpftaps = firwin(N, cutoff_hz / nyq_rate, window = ('kaiser', beta))

# Subtract 1 from lpf centre tap for gain adjust for hpf + lpf
lpftaps[33] = lpftaps[33] - 1

#----------------------------------------------------------
# Now add the lpf and hpf coefficients to form the bpf.

taps = [sum(pair) for pair in zip(hpftaps, lpftaps)]

#----------------------------------------------------------
# Use lfilter to filter test signal with Bandpass filter.
filtered_x = lfilter(taps, 1.0, x)

#----------------------------------------------------------
# Plot the Bandpass filter coefficients.

figure(1)
plot(taps, 'bo-', linewidth = 2)
title('FIR Bandpass Filter Coefficients (%d taps)' % N)
grid(True)

#----------------------------------------------------------
# Plot the magnitude response of the filter.

figure(2)
clf()
w, h = freqz(taps, worN = 8000)
plot((w / pi) * nyq_rate, absolute(h), linewidth = 2)
xlabel('Frequency (Hz)')
ylabel('Gain')
title('FIR Bandpass Filter Frequency Response')
ylim(-0.05, 1.05)
grid(True)

# Upper inset plot.
ax1 = axes([0.42, 0.6, .45, .25])
plot((w / pi) * nyq_rate, absolute(h), linewidth = 2)
xlim(8.0, 16.0)
ylim(0.9, 1.1)
grid(True)

# Lower inset plot
ax2 = axes([0.42, 0.25, .45, .25])
plot((w / pi) * nyq_rate, absolute(h), linewidth = 2)
xlim(17.0, 25.0)
ylim(0.0, 0.0025)
grid(True)

#----------------------------------------------------------
# Plot the test signal and filtered output.


# The phase delay of the filtered signal.
delay = 0.5 * (N - 1) / sample_rate

figure(3)
# Plot the test signal.
plot(t, x)

# Plot the filtered signal, shifted to compensate for
# the phase delay.

plot(t - delay, filtered_x, 'r-')

# Plot just the "good" part of the filtered signal.
# The first N-1 samples are "corrupted" by the
# initial conditions.
plot(t[N - 1:] - delay, filtered_x[N - 1:], 'g', linewidth = 4)

xlabel('t')
title('Signal + noise and filtered ouput of FIR BPF')
grid(True)

show()
