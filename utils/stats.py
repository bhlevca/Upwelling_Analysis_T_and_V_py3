import numpy
import scipy.stats
import numpy.polynomial.polynomial as polynomial
import matplotlib.pyplot as plt

def rsquared(x, y):
    """ Return R^2 where x and y are array-like."""

    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    return [r_value ** 2, slope, intercept, r_value, p_value, std_err]


def plot_regression(x, y, slope, intercept, x_label = None, y_label = None, title = None, \
                    r_value = None, p_value = None):

    print "itercept = %f, slope = %f" % (slope, intercept)
    plt.plot(x, y, 'bd')
    plt.plot(x, slope * x + intercept, 'r-')

    if r_value != None:
        text = "R$^2$=%4.2f" % r_value ** 2
        y0 = max(y) * 7.9 / 8
        x0 = max(x) * 3.2 / 4
        plt.annotate(text, (x0, y0), ha = 'left', va = 'center', bbox = dict(fc = 'white', ec = 'none'))
    if p_value != None:
        text2 = "p value=%2.5f" % p_value
        y0 = max(y) * 7.8 / 8 - 7
        plt.annotate(text2, (x0, y0), ha = 'left', va = 'center', bbox = dict(fc = 'white', ec = 'none'))

    if x_label != None:
        plt.xlabel(x_label).set_fontsize(14)
    if y_label != None:
        plt.ylabel(y_label).set_fontsize(14)
    if title != None:
        plt.title(title).set_fontsize(16)

    plt.grid(True)
    plt.show()



if __name__ == "__main__":
    x = [1, 2, 3, 4, 5, 6]
    y = [6, 5, 4, 3, 2, 1]
    x = [5.05, 6.75, 3.21, 2.66]
    y = [1.65, 26.5, -5.93, 7.96]
    print rsquared(x, y)
