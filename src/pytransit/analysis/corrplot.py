import sys

try:
    import wx
    WX_VERSION = int(wx.version()[0])
    hasWx = True

except Exception as e:
    hasWx = False
    WX_VERSION = 0

if hasWx:
    import wx.xrc
    from wx.lib.buttons import GenBitmapTextButton
    from pubsub import pub
    import wx.adv

import os
import time
import math
import random
import numpy
import scipy.stats
import datetime

from pytransit.analysis import base
import pytransit.transit_tools as transit_tools
import pytransit.tnseq_tools as tnseq_tools
import pytransit.norm_tools as norm_tools
import pytransit.stat_tools as stat_tools

# stuff specific to corrplot.py

import pandas as pd
import seaborn as sns

# filterwarnings is need to suppress this message: 
#   matplotlib.use() has no effect because the backend has already been chosen; 
#   matplotlib.use() must be called *before* pylab, matplotlib.pyplot, or matplotlib.backends is imported for the first time. 
#   The backend was *originally* set to 'TkAgg' (see pytransit.__main__)

import warnings
warnings.filterwarnings('ignore') 

import matplotlib
import matplotlib.pyplot as plt

# might need this if logged in remotely with no X...
# setenv DISPLAY :0.0

############# Description ##################

short_name = "corrplot"
long_name = "Corrplot"
short_desc = "Correlation among TnSeq datasets"
long_desc = "Correlation among TnSeq datasets"
transposons = ["himar1", "tn5"]
columns = ["Position","Reads","Genes"]


############# Analysis Method ##############

class Corrplot(base.TransitAnalysis):
    def __init__(self):
        base.TransitAnalysis.__init__(self, short_name, long_name, short_desc, long_desc, transposons, CorrplotMethod, CorrplotGUI, []) # [CorrplotFile])


################## FILE ###################

# there is no output file that could be loaded into the GUI

#class CorrplotFile(base.TransitFile):
#
#    def __init__(self):
#        base.TransitFile.__init__(self, "#CombinedWig", columns) 
#
#    def getHeader(self, path):
#        text = """This is file contains mean counts for each gene. Nzmean is mean accross non-zero sites."""
#        return text

################# GUI ##################

# right now, tnseq_stats is just intended for the command-line; TRI

class CorrplotGUI(base.AnalysisGUI):

    def __init__(self):
        base.AnalysisGUI.__init__(self)

########## METHOD #######################


class CorrplotMethod(base.SingleConditionMethod):
    """   
    Norm
 
    """
    def __init__(self,gene_means,outfile): 
                ctrldata=None # initializers for superclass
                annotation_path=""
                output_file=outfile
                replicates="Sum"
                normalization="nonorm" 
                LOESS=False
                ignoreCodon=True
                NTerminus=0.0
                CTerminus=0.0
                wxobj=None
                base.SingleConditionMethod.__init__(self, short_name, long_name, short_desc, long_desc, ctrldata, annotation_path, output_file, replicates=replicates, normalization=normalization, LOESS=LOESS, NTerminus=NTerminus, CTerminus=CTerminus, wxobj=wxobj)


    @classmethod
    def fromargs(self, rawargs): 
        (args, kwargs) = transit_tools.cleanargs(rawargs)
        if (kwargs.get('-help', False)): print(self.usage_string()); sys.exit(0)
        if len(args)<2: print(self.usage_string()); sys.exit(0)
        self.gene_means = args[0]
        self.outfile = args[1]
        return self(self.gene_means,outfile=self.outfile)

    def Run(self):

        self.transit_message("Starting Corrplot")
        start_time = time.time()

        # assume first non-comment line is header; samples are 
        headers = None
        data,counts = [],[]
        for line in open(self.gene_means):
          w = line.rstrip().split('\t')
          if line[0]=='#': headers = w[3:]; continue # last comment line has names of samples
          data.append(w)
          cnts = [float(x) for x in w[3:]]
          counts.append(cnts)

        d = pd.DataFrame(data=counts,columns=headers)
        corr = d.corr()
        cc = corr.unstack()
        a,b = min(cc),max(cc)
        # Generate a mask for the upper triangle
        #mask = np.triu(np.ones_like(corr, dtype=np.bool))
        f, ax = plt.subplots(figsize=(11, 9))
        # Generate a custom diverging colormap
        cmap = sns.diverging_palette(10, 240, as_cmap=True)
        sns.heatmap(corr, cmap=cmap, vmin=min(a,0.5),vmax=1,# vmin=-1, vmax=1, center=0,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})
        print("generating corrplot %s" % self.outfile)
        #plt.show()
        plt.savefig(self.outfile)

        self.finish()
        self.transit_message("Finished Corrplot") 

    @classmethod
    def usage_string(self):
        return "usage: python %s corrplot <gene_means> <output.png>" % sys.argv[0]


if __name__ == "__main__":

    (args, kwargs) = transit_tools.cleanargs(sys.argv[1:])

    G = Norm.fromargs(sys.argv[1:])
    G.Run()

