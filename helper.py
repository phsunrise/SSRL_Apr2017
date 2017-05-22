import pickle
import numpy as np

def getparam(param, run):
    scans = pickle.load(open("scans.pickle", 'rb'))
    return scans[param][run]

def getdpa(sample):
    d = {'0.2dpa':0.2, '0.6dpa':0.6, '2dpa':2, '5dpa':5}
    return d[sample]
