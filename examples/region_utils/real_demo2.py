'''
real_demo2.py

Written By : Arulalan.T
Date : 15.07.2014

'''

import os, sys 
sys.path.append(os.path.abspath('../../'))
import numpy
import cdms2, MV2, vcs
from chutil.region_utils import irregularClosedRegionSelector, getAreaOfAllClosedDomains


f = cdms2.open('data/snc.nc')
data = f('snc', time=slice(1), squeeze=1)

print "Contions \n 1. Mask less than 100 \n 2. Mask less than 30 and greater than 70"
con = input('Enter Condion Option 1 or 2 : ')

if con == 1:
    mask_condition = MV2.masked_less(data, 100.)
    value = 'value equal to 100'
    dirname = 'outplots_eq_100'
elif con == 2:
    c1 = MV2.masked_greater(data, 70.)
    c2 = MV2.masked_less(data, 30.)
    mask_condition = MV2.logical_and(c1, c2)
    value = 'value equal to within 30 to 70'
    dirname = 'outplots_eq_30_to_70'
# end of if con == 1:

if not os.path.isdir(dirname):  os.mkdir(dirname)
print "Output plots will be saved in '%s' directory" % dirname

v = vcs.init()
# Assign the variable "cf_asd" to the persistent 'ASD' isofill graphics methods.
cf_asd = v.createboxfill()

cf_asd.level_1 = data.min()         # change to default minimum level
cf_asd.level_2 = data.max()         # change to default maximum level

# set missing color as white
cf_asd.missing = 240
v.landscape()
v.plot(data, cf_asd,continents=1, bg=0)
v.png(os.path.join(dirname, 'snc_full_data.png'))

dic = getAreaOfAllClosedDomains(data, mask_condition, update_mask=1)

raw_input('enter to see diff in vcs')
v.clear()



for reg in dic:

    dummy = MV2.zeros(data.shape)
    dummy = MV2.masked_equal(dummy, 0)
    dummy = cdms2.createVariable(dummy, id=data.id)
    dummy.setAxisList(data.getAxisList())
    print reg,
    minrow, maxrow = dic[reg]['cpixels']['row']
    mincol, maxcol = dic[reg]['cpixels']['col']
    lat, lon = zip(*dic[reg]['blatlons'])

    regionData = irregularClosedRegionSelector(data, lat, lon,
                                    overwrite=1, condition=mask_condition)

    dummy[minrow: maxrow+1, mincol: maxcol+1] = regionData
    dummy.mask[minrow: maxrow+1, mincol: maxcol+1] = regionData.mask
    area = dic[reg]['area']
    totalPixelsCount = dic[reg]['totalPixelsCount']
    
    print "totalPixelsCount", dic[reg]['totalPixelsCount'], "area", dic[reg]['area']
    # Plot the data using the above boxfill graphics method.
    tit = '     '+ reg.capitalize() + '        Total Pixels Count = '
    tit+= str(totalPixelsCount) + '      Area = '+str(area)+' m^2'
    v.plot(dummy, cf_asd,continents=1, title=tit, bg=0)
    v.png(os.path.join(dirname, reg + '.png'))

    raw_input("enter")
    v.clear()
# end of for reg in dic:

print "After update data "
dataid = data.id
data = MV2.where(mask_condition, data, numpy.nan)
data.id = dataid
v.plot(data, cf_asd, continents=1, title='  All regions '+value, bg=0)
v.png(os.path.join(dirname, 'all_regions.png'))
