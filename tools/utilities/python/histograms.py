
import matplotlib.pylab as mpl
import numpy as na
#mpl.rcParams.update({'font.family':'serif',})


def get_colors_pastel(n):
    """ Return n pastel colours. """
    base = na.asarray([[1,0,0], [0,1,0], [0,0,1]])

    if n <= 3:
        return base[0:n]

    # how many new colours to we need to insert between
    # red and green and between green and blue?
    needed = (((n - 3) + 1) / 2, (n - 3) / 2)

    colours = []
    for start in (0, 1):
        for x in mpl.linspace(0, 1, needed[start]+2):
            colours.append((base[start] * (1.0 - x)) +
                           (base[start+1] * x))
    return colours[0:n]

def get_colors(n):
    """ Return n shades of gray. """
    return [[x, x, x] for x in mpl.linspace(0.3, 0.8, n)]
        


class Histogram:
    def __init__(self):
        self.bins = {}
    def add(self, data, amount=1):
        self.bins.setdefault(data, 0)
        self.bins[data] += amount
    def merge(self, histogram):
        for key, amount in histogram.bins.iteritems():
            self.add(key, amount)
    def tuples(self):
        tuples = list(self.bins.iteritems())
        tuples.sort(lambda x, y: cmp(x[1], y[1]), reverse=True)
        return tuples

def showHistogram(prefix, titleText, tuples, xlbl="Counts", leftAdjust=0.23):
    mpl.figure(figsize=(5,3))
    mpl.clf()
    ylocations = na.arange(len(tuples)) + 0.5
    width = 0.7
    tuples.reverse()
    labels = [label for label, count in tuples]
    data = [count for label, count in tuples]

    
    mpl.barh(ylocations, data, height=width, align='center')
    mpl.yticks(ylocations, labels)
    mpl.xlabel(xlbl)
#    mpl.subplots_adjust(left=leftAdjust)
    mpl.title(titleText)
    #mpl.show()
    mpl.savefig("%s.%s.png" % (prefix, titleText.replace(" ", "_")))

def condenseHistograms(histogramMap):



    condensedHistogram = Histogram()
    keys = []

    stopwords = ["the", "a", "an", "of", "and", "your"]
    for hkey, histogram in histogramMap.iteritems():


        for oldKey, count in histogram.bins.iteritems():

            tokenSet = set(oldKey.split())
            matched = False

            for key, keySet, wordHist in keys:
                intersect = keySet.intersection(tokenSet)
                intersect = [w for w in intersect if not w in stopwords]
                if len(intersect) != 0:
                    if "go" in keySet:
                        print "merging '%s' to '%s'" % (oldKey, key)
                    for w in intersect:
                        wordHist.add(w)
                    condensedHistogram.bins[key] += count
                    matched = True
                    break
            if not matched:
                condensedHistogram.bins[oldKey] = count
                wordHist = Histogram()
                assert len(tokenSet) != 0, (tokenSet, oldKey)
                for w in tokenSet:
                    wordHist.add(w)
                keys.append((oldKey, tokenSet, wordHist))

    newHistogram = Histogram()
    for key, keySet, wordHist in keys:
        print wordHist.tuples()
        typicalKey, count = wordHist.tuples()[0]
        newHistogram.bins[typicalKey] = condensedHistogram.bins[key]
                
    return {"All":newHistogram}

def graphStacked(histogramMap, prefix, titleText, leftAdjust=0.23, maxCols=None,
                 figsize=(6,6), showEntries=True, bottomAdjust=0.19, topAdjust=0.75,
                 condensed=False, xticks=None, makeLegend=True):


    if condensed:
        histogramMap = condenseHistograms(histogramMap)
    #print "user", histogramMap
    #print "bin", histogramMap[6].bins
    allValues = Histogram()


    for histogram in histogramMap.values():
        allValues.merge(histogram)
    mpl.figure(figsize=figsize)

    if not showEntries:
        histogramMap = {"all":allValues}

    if xticks == None:
        maxval = na.max(allValues.bins.values())
        xticks = na.arange(0, maxval, maxval/5)


    width = 0.7
    allTuples = allValues.tuples()
    if maxCols != None:
        allTuples = allTuples[0:maxCols]
    allTuples.reverse()
    #print "tuples", allTuples
    colors = get_colors(len(histogramMap))
    yoff = na.array([0.0] * len(allTuples))
    ylocations = na.arange(len(allTuples)) + 0.5
    mpl.xlabel("Count", fontsize=20)
    legendArray = []
    legendNames = []
    #print allTuples
    for row, userId in enumerate(sorted(histogramMap.keys())):
        histogram = histogramMap[userId]
        data = [histogram.bins[desc] if desc in histogram.bins else 0
                for desc, count in allTuples]
        rects = mpl.barh(ylocations, data, width, left=yoff, color=colors[row], align="center")

        if len(rects) != 0:
            legendArray.append(rects[0])
            legendNames.append(userId)

        yoff = yoff + data
    
    mpl.yticks(ylocations, [label.replace("Davin", "the baby") for label, count in allTuples])
    mpl.subplots_adjust(left=leftAdjust, bottom=bottomAdjust, top=topAdjust)

    if len(legendArray) > 1 and makeLegend:
        mpl.legend(legendArray, legendNames, loc="lower right")
    mpl.xticks(xticks)
    mpl.title(titleText, fontsize=20)
    ax = mpl.axes()
    for tick in ax.xaxis.get_major_ticks():
        tick.label1.set_fontsize(15)
    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_fontsize(15)


    basename = "%s.%s%s" % (prefix, titleText.replace(" ", "_"), "" if not condensed else ".condensed")
    mpl.savefig("%s.png" % (basename))
    mpl.savefig("%s.pdf" % (basename))
