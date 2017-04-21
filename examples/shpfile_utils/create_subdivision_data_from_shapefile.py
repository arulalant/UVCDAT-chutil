import cdms2, cdutil, vcs, os, sys 
sys.path.append(os.path.abspath('../../'))
from chutil.shpfile_utils import createVarSubdivisionShpNCfile

varid = 't'
cfile = 'indata/t_500hPa_ecmwf.nc'
outpath = 'outdata'
shpfile = 'shpdata/india_subdivision.shp'            

createVarSubdivisionShpNCfile(varid, cfile, shpfile, outpath, 
              latitude=(0, 40), longitude=(60, 100),
              preserve_original_data_shape_in_all_subregions=True)


