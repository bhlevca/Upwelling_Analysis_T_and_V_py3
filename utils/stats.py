import numpy
import scipy.stats
import numpy.polynomial.polynomial as polynomial
import matplotlib.pyplot as plt

def interquartile_range(X, a = 25, b = 75, onlylower = False):
    """Calculates the Freedman-Diaconis bin size for
    a data set for use in making a histogram

    Arguments:
    X:  1D Data set
    a: lower quartile 0-> 100
    b: upperquartile  0 ->100

    b neesd to be greater thant a
    Returns:
    h:  F-D bin size
    """
    # check
    if b < a:
        raise Exception("upper quartile has to be greater than lower quartile")


    # First Calculate the interquartile range
    X = numpy.sort(X)
    upperQuartile = scipy.stats.scoreatpercentile(X, b)
    lowerQuartile = scipy.stats.scoreatpercentile(X, a)

    if onlylower:
        return lowerQuartile
    else:
        IQR = upperQuartile - lowerQuartile
        return IQR


# end interquartile_range


def rsquared(x, y):
    """ Return R^2 where x and y are array-like."""

    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    return [r_value ** 2, slope, intercept, r_value, p_value, std_err]


def plot_regression(x, y, slope, intercept, point_labels = None, x_label = None, y_label = None, title = None, \
                    r_value = None, p_value = None, fontsize = 20, bbox = False):

    print "intercept = %f, slope = %f" % (slope, intercept)
    fig, ax = plt.subplots()
    ax.plot(x, y, 'bo')

    ax.plot(x, slope * x + intercept, 'r-')

    xmax = numpy.max(x)
    scalex = ax.xaxis.get_view_interval()
    xbins = len(ax.xaxis.get_gridlines()) - 1
    xn_per_bin = (scalex[1] - scalex[0]) / xbins

    scaley = ax.yaxis.get_view_interval()
    ybins = len(ax.yaxis.get_gridlines()) - 1
    ybin_sz = (scaley[1] - scaley[0])
    yn_per_bin = ybin_sz / ybins

    if point_labels != None:
        dx = scalex[0] / scalex[1] + 3.5 / xn_per_bin
        dy = scaley[0] / scaley[1] + 3.5 / yn_per_bin
        for i in range(0, len(point_labels)):
            ax.annotate(point_labels[i], xy = (x[i], y[i]), xycoords = 'data', xytext = (dx, dy) , textcoords = 'offset points',
                        ha = 'right', va = 'top', bbox = dict(fc = 'white', ec = 'none', alpha = 0.3))

    if bbox:
        bbox_props = dict(boxstyle = "square,pad=0.3", fc = "white", ec = "b", lw = 1)
    else:
        bbox_props = None

    # transform = ax.transAxes ensures independence of text position from the plotting scale
    if r_value != None:
        text = "R$^2$=%4.2f" % r_value ** 2
        x0 = scalex[0] + (1.2) * xn_per_bin
        # x0 = scalex[0] + (xbins - 1.5) * xn_per_bin
        y0 = scaley[0] + (ybins - 0.8) * yn_per_bin
        # y0 = scaley[0] + (2) * yn_per_bin
        ax.text(0.02, 0.95, text, ha = 'left', va = 'center', bbox = bbox_props, fontsize = 14, transform = ax.transAxes)
    if p_value != None:
        text2 = "p-value=%2.5f" % p_value
        x0 = scalex[0] + (1.2) * xn_per_bin
        # x0 = scalex[0] + (xbins - 1.5) * xn_per_bin

        # y0 = scaley[0] + (1) * yn_per_bin
        ax.text(0.02, 0.9, text2, ha = 'left', va = 'center', bbox = bbox_props, fontsize = 14, transform = ax.transAxes)

    if x_label != None:
        plt.xlabel(x_label).set_fontsize(fontsize)
    if y_label != None:
        plt.ylabel(y_label).set_fontsize(fontsize)
    if title != None:
        plt.title(title).set_fontsize(fontsize + 2)

    ax.set_xlim(xmax = xmax + xmax / 10)

    plt.grid(True)
    # plt.show()



if __name__ == "__main__":
    x = [1, 2, 3, 4, 5, 6]
    y = [6, 5, 4, 3, 2, 1]
    x = [5.05, 6.75, 3.21, 2.66]
    y = [1.65, 26.5, -5.93, 7.96]
    print rsquared(x, y)
