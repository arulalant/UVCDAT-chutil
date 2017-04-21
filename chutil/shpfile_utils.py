import cdms2, numpy, ocgis, MV2, os
cdms2.setNetcdfShuffleFlag(0)
cdms2.setNetcdfDeflateFlag(0)
cdms2.setNetcdfDeflateLevelFlag(0)


def createVarSubdivisionShpNCfile(varid, cfile, shpfile, outpath, **kwarg):
    """
    createVarSubdivisionShpNCfile : create variable of subdivison shaped using 
          shp file as one of the input and store into nc file.
    args:
        varid : variable name of input file 
        cfile : input climate netcdf file path
        shpfile : shpfile path which has proper subdivison level map
        outpath : output directory
    kwargs:
        preserve_original_data_shape_in_all_subregions : True | False (default).
           If it is True, then all subdivison regions of input variable will 
           have same shape of full region but masked fully (lat, lon) other
           than subdivison / state boundary region. Useful to retain the full 
           data shape but keep only subdivison region data alone.
           
           If it is False, then all subdivison regions of input variable will
           be store with its corresponding lat, lon shape.
         latitude : range of latitude to be retain in the output in case of 
                    preserve_original_data_shape_in_all_subregions is True.
         longitude : range of longitude to be retain in the output in case of 
                    preserve_original_data_shape_in_all_subregions is True. 
                    
    output : It create nc file named as varid + '_subdivisions.nc'.
             This function works well for the input shape of (time, latitude, longitude).
             
    Author :  Arulalan.T (arulalant@gmail.com), Research Scholar, CAS, IITD
    Date :  21-Apr-2017
    
    """ 

    # export the environment variable path of shape file
    shpfname = shpfile.split('/')[-1].split('.')[0 ]
    shppath = shpfile.split(shpfname)[0]
    ocgis.env.DIR_GEOMCABINET = shppath
    
    preserve_original_data_shape_in_all_subregions = kwarg.get('preserve_original_data_shape_in_all_subregions', False)
    
    lat = kwarg.get('latitude', None)
    lon = kwarg.get('longitude', None)
    outpath = '.' if outpath is None else outpath
    
    outfile_sequentialnumbers = varid + '_filledwith_sequentialnumbers.nc'
    shpdata_outfile = os.path.join(outpath, varid + '_subdivisions.nc')
    
    # open the nc file via uvcdat
    inf = cdms2.open(cfile)
    sdata = inf(varid, time=slice(1))
    tottimeax = inf[varid].getTime()
    # get the shape of one time step, lat, lon for dummy sequential numbers
    dshape = sdata.shape[-2:]
    dlen = dshape[0] * dshape[1]
    oshape = (len(tottimeax), dshape[0], dshape[1])
    dshape = (1, dshape[0], dshape[1])
    # create dummy sequential numbers
    numbers = numpy.arange(1, dlen+1, 1).reshape(dshape)
    numbers = cdms2.createVariable(numbers, id=varid)
    
    timeax = sdata.getTime()
    taxis = cdms2.createAxis(numpy.array([0]), id='time')
    taxis.units = timeax.units
    taxis.designateTime()
    # set all axis 
    numbers.setAxisList([taxis, sdata.getLatitude(), sdata.getLongitude()])
    # store into temporary nc file of sequential numbers.
    outf = cdms2.open(outfile_sequentialnumbers, 'w')
    outf.write(numbers)
    outf.close()
    
    # repeat nos for time dimension
    tnumbers = numbers.data.repeat(len(tottimeax), 0)
   
    # get sequential numbers via ocgis 
    rd_sequentialnumbers = ocgis.RequestDataset(outfile_sequentialnumbers, variable=varid)
    # get actual data via ocgis 
    rd_data = ocgis.RequestDataset(cfile, variable=varid)
    print "Hold on ... it may take some time ..."
    # get list of state bounded numpy arrays of sequential numbers
    state_sequentialnumbers = ocgis.OcgOperations(dataset=rd_sequentialnumbers, 
                                spatial_operation='intersects', #'clip', 
                                aggregate=False, agg_selection=False, 
                                allow_empty=True, snippet=True, 
                                geom=shpfname, output_format='numpy').execute()


    # get list of state bounded numpy arrays of actual climate data 
    state_data = ocgis.OcgOperations(dataset=rd_data, 
                                spatial_operation='intersects',# 'clip', 
                                aggregate=False, agg_selection=False, 
                                allow_empty=True, snippet=False, 
                                geom=shpfname, output_format='numpy').execute()

    # lets store the output here
    outf = cdms2.open(shpdata_outfile, 'w')
    outf.write(sdata(latitude=lat, longitude=lon)) # store sample data full spatial 

    for idxx, state in enumerate(state_sequentialnumbers): 
        # lets loop through all the state boundaries
        idx = idxx + 1
        # get the sequential numbers of particular state boundary
        state_seq_val = state_sequentialnumbers[idx][varid].variables[varid].value
        # get the actual climate data of particular state boundary
        state_data_val = state_data[idx][varid].variables[varid].value.squeeze()    
        # find start and end row of particular state boundary
        start_row = numpy.where(numbers==state_seq_val.min())[1][0]
        end_row = numpy.where(numbers==state_seq_val.max())[1][0]
        # find start and end coloum of particular state boundary
        start_col = numpy.where(numbers==state_seq_val[0][0][0][:,0].min())[2][0]
        end_col = numpy.where(numbers==state_seq_val[0][0][0][:,-1].max())[2][0]
        
        if preserve_original_data_shape_in_all_subregions:
            # get the mask of particular state boundary from sequential numbers
            result = MV2.masked_greater_equal(tnumbers, 0)
            result[:, start_row: end_row+1, start_col:end_col+1] = state_data_val 
            result = result.reshape(oshape)
            # store the clipped actual data into original shapped data by masking other grid points 
            result = cdms2.createVariable(result, id=varid+'_'+str(idx))
            result.setAxisList([tottimeax, sdata.getLatitude(), sdata.getLongitude()])
            if lat and lon: result = result(latitude=lat, longitude=lon)
        else:        
            # store the clipped shaped data as it is into nc file with its lat, lon 
            latax = sdata.getLatitude()[start_row: end_row+1]
            latax = cdms2.createAxis(latax, id='latitude'+str(idx))
            latax.designateLatitude()
            
            lonax = sdata.getLongitude()[start_col:end_col+1]
            lonax = cdms2.createAxis(lonax, id='longitude'+str(idx))
            lonax.designateLongitude()
            stshp = state_data_val.shape
            state_data_val = state_data_val.reshape((len(tottimeax), stshp[-2], stshp[-1]))            
            result = cdms2.createVariable(state_data_val, id=varid+'_'+str(idx))
            result.setAxisList([tottimeax, latax, lonax]) 
            
        outf.write(result)
        print "stored stateboundary data", idx, "shaped : ", result.shape 
    # end of for idx,state in enumerate(path): 

    outf.close()
    inf.close()
    print "Stored the input data with boundaries of shape file into : ", shpdata_outfile
    os.remove(outfile_sequentialnumbers)
# end of def createVarBoundariesOfShp(varid, ...):

if __name__ == '__main__':
            
    cfile = raw_input('Enter input climate data nc filepath : ').strip()
    varid = raw_input('Enter input variable name : ').strip()
    shpfile = raw_input('Enter subdivison shp file path (absolute) : ').strip()
    outpath = raw_input('Enter outpath : ').strip()    
    flag = raw_input('Do you want to retain original datashape in all subregions with proper mask [yes/no] : ').strip()
    flag = True if flag == 'yes' else False
    lat = (0, 40)
    lon = (60, 100)
    if flag:
        ilat = raw_input('Enter required out latitude common range [default (0, 40)]: ').strip()
        ilon = raw_input('Enter required out longitude common range [default (60, 100)]: ').strip()
        if ilat: lat = eval(ilat)
        if ilon: lon = eval(ilon)
     
    createVarSubdivisionShpNCfile(varid, cfile, shpfile, outpath, 
                  latitude=lat, longitude=lon,
                  preserve_original_data_shape_in_all_subregions=flag)


