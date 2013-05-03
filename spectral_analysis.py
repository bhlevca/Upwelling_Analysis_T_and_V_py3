import time, os, sys, locale

sys.path.insert(0, '/software/SAGEwork/Seiches')
import fft.FFTGraphs as fftGraphs


def doSpectralAnalysis(data, name, label, title, draw, window = "hanning", num_segments = 10, tunits = "sec", funits = "Hz", b_wavelets = False) :
    # show extended calculation of spectrum analysis
    show = True


    # ToDo: modify this method to accept data instead of file name. It needs to separate the file handling layer form the daa processing layer
    # use directly the data processing layer

    fftsa = fftGraphs.FFTGraphs(None, None, None, show, data)
    showLevels = False
    detrend = False

    [Time, y, x05, x95] = fftsa.doSpectralAnalysis(showLevels, draw, tunits, window, num_segments, filter)
    fftsa.plotLakeLevels(name, None, detrend, label, title)
    fftsa.plotSingleSideAplitudeSpectrumFreq(name, None, funits, label, title)
    fftsa.plotSingleSideAplitudeSpectrumTime(name, None, label, title)

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

def doLogSpectralAnalysis(data, name, label, title, draw, window = "hanning", num_segments = 10, tunits = "sec", funits = "Hz", b_wavelets = False) :
    # show extended calculation of spectrum analysis
    show = True


    # ToDo: modify this method to accept data instead of file name. It needs to separate the file handling layer form the daa processing layer
    # use directly the data processing layer

    fftsa = fftGraphs.FFTGraphs(None, None, None, show, data)
    showLevels = False
    detrend = False

    [Time, y, x05, x95] = fftsa.doLogSpectralAnalysis(showLevels, draw, tunits, window, num_segments, filter)
    fftsa.plotLakeLevels(name, None, detrend, label, title)
    fftsa.plotLogSingleSideAplitudeSpectrumFreq(name, None, funits, label, title)
    fftsa.plotLogSingleSideAplitudeSpectrumTime(name, None, label, title)

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



def doCospectralAnalysis(data1, data2):
    pass

