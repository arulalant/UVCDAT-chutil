'''
demo.py

Written By : Arulalan.T
Date : 15.07.2014

'''

import os, sys 
sys.path.append(os.path.abspath('../../'))
import cdms2
from chutil.nonrect_utils import get1LatLonFromNonRectiLinearGrid

datapath = raw_input("Enter the datapath : ")
var = raw_input("Enter the variable : ")
lat = float(raw_input("Enter the latitude you looking for : "))
lon = float(raw_input("Enter the longitude you looking for : "))
f = cdms2.open(datapath)
x = f(var, time=slice(1), squeeze=1)
f.close()
latidx, lonidx = get1LatLonFromNonRectiLinearGrid(x.getGrid(), lat, lon)
print "The value is = %f for the given lat=%r, lon=%r " % (x[latidx][lonidx], lat, lon)
