import pickle
import numpy as np

def getparam(param, run):
    scans = pickle.load(open("scans.pickle", 'rb'))
    return scans[param][run]

def getdpa(sample):
    d = {'0.2dpa':0.2, '0.6dpa':0.6, '2dpa':2, '5dpa':5}
    return d[sample]

def getsamplename(sample):
    samplenames = {'0.2dpa_ref':'Ref', '0.2dpa':'0.2DPA', '0.6dpa':'0.6DPA', \
                   '2dpa':'2DPA', '5dpa':'5DPA'}
    return samplenames[sample]

