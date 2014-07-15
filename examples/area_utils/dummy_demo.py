'''
dummy_demo.py

Written By : Arulalan.T
Date : 15.07.2014

'''

import os, sys 
sys.path.append(os.path.abspath('../../'))
from chutil.area_utils import irregularClosedRegionSelector, getAreaOfAllClosedDomains
import numpy, cdms2, MV2

a = numpy.zeros((180, 360))
b = numpy.random.random_integers(1, 5, (3, 5))
c = numpy.random.random_integers(1, 5, (6, 9))
d = numpy.random.random_integers(1, 5, (5, 8))
e = numpy.random.random_integers(1, 5, (15, 18))
a[4:7, 3:8] = b
a[1, 5] = 3
a[2, 5] = 3
a[3, 4:7] = [3, 2, 3]
a[7, 4:7] = [3, 2, 3]
a[8, 4:7] = [3, 0, 1]
a[9, 4:7] = [3, 0, 1]

# to get funny nos with masked area (i.e. funny complex area)
#print a[0:11, 2:9] # dummy[0:11, 2:9]

a[0:6, 120:129] = c
a[10:15, 16:24] = d
a[100:115, 100:118] = e

lat = numpy.arange(-89.5, 90)
lat = cdms2.createAxis(lat, id='latitude')

lon = numpy.arange(-179.5, 180)
lon = cdms2.createAxis(lon, id='longitude')

data = cdms2.createVariable(a, id='dummy')
data.setAxisList([lat, lon])

del a

print "slice of input data "
d = data[0:11, 2:9]
print d
#print d.getLatitude(), d.getLongitude(), d.mask

condition = MV2.masked_equal(data, 0)
dic = getAreaOfAllClosedDomains(data, condition, update_mask=0)

print "dictionary", dic 

latlon = dic['region2']['blatlons']

lat, lon = zip(*latlon)


print data[0:11, 2:9]
sd = irregularClosedRegionSelector(data, latitude=lat,
                longitude=lon, overwrite=1, condition=condition)

print "Extracted irregular Selector data"
print sd
print 'count=', sd.count()
print "After overwritten original data slice"
print data(latitude=(min(lat), max(lat)), longitude=(min(lon), max(lon)))

print "slice of input data after update_mask"
print data[0:11, 2:9]
#print data.mask[0:11, 2:9]
print 'totalPixelsCount', dic['region2']['totalPixelsCount']
print 'area', dic['region2']['area']
