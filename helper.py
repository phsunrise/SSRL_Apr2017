import pickle
import numpy as np

def getparam(param, run):
    scans = pickle.load(open("scans.pickle", 'rb'))
    return scans[param][run]
