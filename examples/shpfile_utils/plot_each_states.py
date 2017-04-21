import cdms2, cdutil, vcs, os, sys 
sys.path.append(os.path.abspath('.'))
from plot_utils import genTemplate

        
# lets plot it
v = vcs.init()
v.portrait()
gen = genTemplate()
#v.setcolormap('ASD')

## Follow the below procedure to call custom indian map in conda installed uvcdat-2.6 onwards.
## copy data_continent_other8 into /home/arulalan/miniconda2/envs/uvcdat-2.6.1/share/vcs 
## v.setcontinentstype(0)
## indiamappath = os.path.join(vcs.prefix, "share", "vcs", "data_continent_other8")
## v.plot(data, continents=indiamappath)

## to call custom india map in uvcdat-1.5.1 
## just copy the data_continent_other8 into $HOME/.uvcdat/
## and then v.plot(data, continents=7) this will work.

sourcefile = 'outdata/t_subdivisions.nc'
var = 't'

dirname = var + '_outplots'
if not os.path.isdir(dirname): os.mkdir(dirname)
    
f = cdms2.open(sourcefile)

data = f(var, time=slice(1), latitude=(0, 40), longitude=(60, 100), )

mindata = data.min() 
maxdata = data.max() 
levels = vcs.mkscale(mindata, maxdata, 25, zero=1)
print levels

myisofill = v.createisofill()
myisofill.levels = levels
myisofill.fillareacolors = vcs.getcolors(levels, split=0)


tit = "ECMWF Temperature @ 500 hPa - India "
out = os.path.join(dirname, 'India.png')
cm = '' # comment 
# continents=7 represents data_continent_other8 which contains indian state boundaries
# if you dont have then set it within 1 to 6
v.plot(data, myisofill, gen, title=tit, comment1=cm, continents=7, bg=0)
v.png(out)
v.clear()

for idx in range(1, 37):
    data = f('%s_%d' % (var, idx), latitude=(0, 40), longitude=(60, 100), )
    tit = "ECMWF Temperature @ 500 hPa - State %d " % idx 
    out = os.path.join(dirname, 'state_%d.png' % idx)
    cm = '' # comment     
    if not data.min(): 
        print "couldnt plot idx", idx 
        continue
    v.plot(data, myisofill, gen, title=tit, comment1=cm, continents=7, bg=0) 
    v.png(out)
    v.clear()
    print "Plot saved in '%s'" % out 

f.close()




