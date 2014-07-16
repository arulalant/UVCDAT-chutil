import cdms2, cdutil, vcs, os, sys 
sys.path.append(os.path.abspath('../../'))
from chutil.region_utils import maskOutOfRegions
from plot_utils import genTemplate

        
# lets plot it
v = vcs.init()
v.setcolormap('ASD')

f = cdms2.open('data/TRMM_3A12.007.nc')

data = f('convectPrecipitation', latitude=(6, 45, 'ccb'), longitude=(66, 98, 'ccb'))

# lets make region1 cdms domain selector variable
region1 = cdms2.selectors.Selector(cdutil.region.domain(latitude=(23.125, 31.875, 'ccb'),
                                         longitude=(68.125, 78.875, 'ccb')))
# lets make region2 cdms domain selector variable
region2 = cdms2.selectors.Selector(cdutil.region.domain(latitude=(8.125, 21.875, 'ccb'), 
                                         longitude=(72.125, 77.875, 'ccb')))

print "Options "
print "1. without fill value (masked out of regions)"
print "2. with fill values (fill value out of regions)"
con = input("Enter choise 1 or 2 : ")

if con == 1:
    # lets mask other than regions
    data = maskOutOfRegions(data, [region1, region2])
    status = 'Masked'
elif con == 2:
    # lets mask other than regions
    data = maskOutOfRegions(data, [region1, region2], fillvalue=0.4)
    status = 'Filled'
# end of if con == 1:

print "data after masked out of regions", data 

mindata = data.min() 
maxdata = data.max() 
levels = vcs.mkscale(mindata, maxdata, 10, zero=1)

myisofill = v.createisofill()
myisofill.levels = levels
myisofill.fillareacolors = vcs.getcolors(levels, split=0)

###
# make portrait in v object is essential to work perfectly in uv-cdat.
v.portrait()
gen = genTemplate()

dirname = 'outplots_maskOutOfRegions'
if not os.path.isdir(dirname): os.mkdir(dirname)

tit = "TRMM 3A25 v7 - Conv Mean Rain Rate "
cm = "2 Regions Demo - %s out of needed regions - [mm/hr]" % status
out = os.path.join(dirname, 'maskOutOfRegionsDemo_%d.png' % con)
# continents=7 represents data_continent_other8 which contains indian state boundaries
# if you dont have then set it within 1 to 6
v.plot(data, myisofill, gen, title=tit, comment1=cm, continents=7, bg=0)
v.png(out)
print "Plot saved in '%s'" % out 
f.close()




