import time, os, sys, locale
import numpy as np

sys.path.insert(0, '/software/SAGEwork/Seiches')
import fft.FFTGraphs as fftGraphs


def doSpectralAnalysis(data, name, label, title, draw, window = "hanning", num_segments = 10, tunits = "sec", funits = "Hz", b_wavelets = False, log = False) :
    # show extended calculation of spectrum analysis
    show = True


    # ToDo: modify this method to accept data instead of file name. It needs to separate the file handling layer form the daa processing layer
    # use directly the data processing layer

    fftsa = fftGraphs.FFTGraphs(None, None, None, show, data)
    showLevels = False
    detrend = False

    [Time, y, x05, x95, fftx, f, mx] = fftsa.doSpectralAnalysis(showLevels, draw, tunits, window, num_segments, filter = None, log = log)
    fftsa.plotLakeLevels(name, None, detrend, label, title)
    fftsa.plotSingleSideAplitudeSpectrumFreq(name, None, funits, label, title, log, fontsize = 20, tunits = tunits)
    fftsa.plotPowerDensitySpectrumFreq(name, None, funits, label, title, log, fontsize = 20, tunits = tunits)
    # This uses the matplotlib psd and deos not have  log axes
    # fftsa.plotPSDFreq(name, None, funits, label, title, log = True, fontsize = 20, tunits = tunits)
    fftsa.plotSingleSideAplitudeSpectrumTime(name, bay_name = None, y_label = None, title = title, ymax_lim = None, log = False, tunits = tunits)

    # fftsa.plotZoomedSingleSideAplitudeSpectrumFreq()
    # fftsa.plotZoomedSingleSideAplitudeSpectrumTime()
    # fftsa.plotCospectralDensity()
    # fftsa.plotPhase()

    if b_wavelets:
        graph = wavelets.Graphs.Graphs(None, None, None, show)

        graph.doSpectralAnalysis()
        graph.plotDateScalogram(scaleType = 'log', plotFreq = True)
        graph.plotSingleSideAplitudeSpectrumTime()
        graph.plotSingleSideAplitudeSpectrumFreq()
        graph.showGraph()
    # end if b_wavelets

    return  [Time, y, x05, x95]
# end doSpectralAnalysis


def doSimpleSpectralAnalysis(data, name, label, title, draw, window = "hanning", num_segments = 10, tunits = "sec", funits = "Hz", b_wavelets = False, log = False) :
    # show extended calculation of spectrum analysis
    show = True
    # ToDo: modify this method to accept data instead of file name. It needs to separate the file handling layer form the daa processing layer
    # use directly the data processing layer

    fftsa = fftGraphs.FFTGraphs(None, None, None, show, data)
    showLevels = False
    detrend = False

    [Time, y, x05, x95, fftx, f, mx] = fftsa.doSpectralAnalysis(showLevels, draw, tunits, window, num_segments, filter = None, log = log)
    fftsa.plotSingleSideAplitudeSpectrumFreq(name, None, funits, label, title, log, fontsize = 20, tunits = tunits)

    return  [Time, y, x05, x95]
# end doSimpleSpectralAnalysis

def doMultipleSpectralAnalysis(path, files, names, draw, window = "hanning", num_segments = 10,
                               tunits = "sec", funits = "Hz", log = False, grid = False, type = 'power', withci = True):
    showLevels = False
    detrend = False
    show = False
    fftsa = np.zeros(len(files), dtype = np.object)
    data = []
    ci05 = []
    ci95 = []
    freq = []
    for i in range(0, len(files)):
        fftsa[i] = fftGraphs.FFTGraphs(path, files[i], None, show, tunits)
        date1st = True
        fftsa[i].doSpectralAnalysis(showLevels, draw, tunits, window, num_segments, filter = None, log = log, date1st = date1st)

        if type == 'power':
            data.append(fftsa[i].power)
        else:
            data.append(fftsa[i].mx)
        ci05.append(fftsa[i].x05)
        ci95.append(fftsa[i].x95)
        freq.append(fftsa[i].f)
    # end for
    lake_name = ""
    if type == 'power':
        ylabel = "Spectral Power [$^\circ$C$^2$/Hz]"
    else:
        ylabel = "Temperature [$^\circ$C]"
    if withci:
        ci = [ci05, ci95]
    else:
        ci = None
    fftGraphs.plotSingleSideSpectrumFreqMultiple(lake_name, names, data, freq, ci, type, \
                                                         num_segments, funits, y_label = ylabel, title = None, \
                                                         log = log, fontsize = 24, tunits = tunits)


def doCospectralAnalysis(data1, data2):
    pass

