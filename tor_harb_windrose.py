import matplotlib.pyplot as plt
import matplotlib.cm as cm
from numpy import arange
import numpy
from windrose import WindroseAxes



def new_axes():
    fig = plt.figure(figsize = (8, 8), dpi = 80, facecolor = 'w', edgecolor = 'w')
    rect = [0.1, 0.1, 0.8, 0.8]
    wax = WindroseAxes(fig, rect, axisbg = 'w')
    fig.add_axes(wax)
    return wax

def set_legend(wax, fontsize = 10):
    l = wax.legend(axespad = -0.10)
    plt.setp(l.get_texts(), fontsize = fontsize)


def draw_windrose(wd, ws, type, fontsize = 10):
    if type == 'bar':
        # windrose like a stacked histogram with normed (displayed in percent) results
        wax = new_axes()
        # for i in range(0, len(wd)):
        #    print "%d) direction: %f,  speed: %f " % (i, wd[i], ws[i])
        wax.bar(wd, ws, nsector = 32, normed = True, opening = 0.8, edgecolor = 'white')
        set_legend(wax, fontsize)

    if type == 'contour':

        # Same as above, but with contours over each filled region...
        wax = new_axes()
        wax.contourf(wd, ws, nsector = 32, bins = arange(0, 40, 4), cmap = cm.hot)
        wax.contour(wd, ws, nsector = 32, bins = arange(0, 40, 4), colors = 'black')
        set_legend(wax, fontsize)

    if type == 'hist':
        wax = new_axes()
        wax.bar(wd, ws, normed = True, nsector = 32, opening = 0.8, edgecolor = 'white')
        set_legend(wax, fontsize)

        table = wax._info['table']
        wd_freq = numpy.sum(table, axis = 0)
        dir = wax._info['dir']
        wd_freq = numpy.sum(table, axis = 0)

        # create another plain figure otherwise it will call the other bar() method from WindRose
        fig = plt.figure(figsize = (8, 8), dpi = 80, facecolor = 'w', edgecolor = 'w')
        ax = fig.add_subplot(111)
        ax.bar(numpy.arange(32), wd_freq, align = 'center')
        xlabels = ('N', '', 'NNE', '', 'N-E', '', 'ENE', '', 'E', '', 'ESE', '', 'S-E', '', 'SSE', '', 'S', '', 'SSW', '', 'S-W', '', 'WSW', '', 'W', '', 'WNW', '', 'N-W', '', 'NNW', '')
        xticks = numpy.arange(32)
        plt.gca().set_xticks(xticks)
        plt.draw()
        plt.gca().set_xticklabels(xlabels)
        plt.draw()

    # #print ax._info
    return plt

# Create wind speed and direction variables
# wd = numpy.random.random_integers(180, 350, 2500)
# ws = numpy.random.random(2500) * 36
# plt = draw_windrose(wd, ws , 'bar')
# plt.show()
