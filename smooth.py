import numpy


def smooth(x, window_len = 11, window = 'hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string   
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len < 3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

    #print "in smooth method"
    #print x, window_len, window
    s = numpy.r_[2 * x[0] - x[window_len:1:-1], x, 2 * x[-1] - x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w = ones(window_len, 'd')
    else:
        w = eval('numpy.' + window + '(window_len)')
    y = numpy.convolve(w / w.sum(), s, mode = 'same')
    dy = s.copy()
    dy[window_len - 1:-window_len + 1] = s[window_len - 1:-window_len + 1] - y[window_len - 1:-window_len + 1]
    return y[window_len - 1:-window_len + 1], dy[window_len - 1:-window_len + 1]


def smoothfit(x, y, winsize, window):
    '''
    returns the residuals            in results['residual']
                determination coeff  in results['determination'] 
                smoothed data         in  results['smoothed']
    '''
    results = {}

    yhat, dy = smooth(numpy.array(y), winsize, window)

    # spline Coefficients

    # fit values, and mean
    #display2(x, y, yhat, 1)

    ybar = sum(y) / len(y)
    rss = 0
    for i in range(0, len(y)):
        rss += (y[i] - yhat[i]) ** 2

    results['residual'] = rss

    sstot = sum([ (yi - ybar) ** 2 for yi in y])
    ssreg = sstot - rss
    results['determination'] = ssreg / sstot
    results['smoothed'] = yhat

    return results

from pylab import *

def smooth_demo():

    t = linspace(-4, 4, 100)
    x = sin(t)
    xn = x + randn(len(t)) * 0.1
    y = smooth(x)

    ws = 31

    subplot(211)
    plot(ones(ws))

    windows = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']

    hold(True)
    for w in windows[1:]:
        eval('plot(' + w + '(ws) )')

    axis([0, 30, 0, 1.1])

    legend(windows)
    title("The smoothing windows")
    subplot(212)
    plot(x)
    plot(xn)
    for w in windows:
        y, dy = smooth(xn, 10, w)
        plot(y)
        #plot(dy)
    l = ['original signal', 'signal with noise']
    l.extend(windows)

    legend(l)
    title("Smoothing a noisy signal")
    show()


if __name__ == '__main__':
    smooth_demo()
