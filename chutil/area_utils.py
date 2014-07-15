"""
area_utils.py

Available Functions:
    irregularClosedRegionSelector()
    getAllBoundaryOfClosedAreas()
    getAreaOfAllClosedDomains()


For detailed docstring read available functions __doc__.

Author : Arulalan.T
Date : 10.07.2014

"""

import numpy, MV2, cdms2, cdutil


def _getEastPixel(data, row, col):
    return data[row][col + 1]


def _getSouthEastPixel(data, row, col):
    return data[row + 1][col + 1]


def _getSouthPixel(data, row, col):
    return data[row + 1][col]


def _getSouthWestPixel(data, row, col):
    return data[row + 1][col - 1]


def _getWestPixel(data, row, col):
    return data[row][col - 1]


def _getNorthWestPixel(data, row, col):
    return data[row - 1][col - 1]


def _getNorthPixel(data, row, col):
    return data[row - 1][col]


def _getNorthEastPixel(data, row, col):
    return data[row - 1][col + 1]


_allDirections_ = [_getNorthEastPixel, _getEastPixel, _getSouthEastPixel,
                            _getSouthPixel, _getSouthWestPixel, _getWestPixel,
                             _getNorthWestPixel, _getNorthPixel]

_allDirectionsRowCol_ = [(-1, 1), (0, 1), (1, 1),
                        (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0)]

_ESWNDirectionsRowCol_ = [(0, 1), (1, 0), (0, -1), (-1, 0)]


def _isPixelOnBoundary(data, row, col, checkval=0):
    # return false if passed pixel value is equal to checkval.
    # i.e on outside boundary region
    if data[row][col] == checkval: return False
    maxrow, maxcol = data.shape
    # if row is equal to 0 or maxrow then pixel is on boundary
    if row in [0, maxrow-1]: return True
    # if col is equal to 0 or maxcol then pixel is on boundary
    if col in [0, maxcol-1]: return True
    # check for in between pixel
    for direction in _allDirections_:
        # atleast one of 8 directions, pixel value should be equal to
        # checkval. i.e. passed row, col (pixel) is pointing on boundary
        # region. so return true
        if direction(data, row, col) == checkval: return True
    # end of for direction in _allDirections_:
    # i.e. on inside boundary region. so return false.
    return False
# end of def _isPixelOnBoundary(data, row, col, checkval=0):


def _isIslandPixel(data, row, col, checkval=0):
    # return false if passed pixel value is equal to checkval.
    if data[row][col] == checkval: return False
    maxrow, maxcol = data.getGrid().shape
    maxrow, maxcol = maxrow-1, maxcol-1

    if row == 0 and col == 0:
        checkDirections = [_getEastPixel, _getSouthEastPixel, _getSouthPixel]

    elif row == 0 and col == maxcol:
        checkDirections = [_getSouthPixel, _getSouthWestPixel, _getWestPixel]

    elif row == maxrow and col == 0:
        checkDirections = [_getNorthEastPixel, _getEastPixel, _getNorthPixel]

    elif row == maxrow and col == maxcol:
        checkDirections = [_getWestPixel, _getNorthWestPixel, _getNorthPixel]

    elif row == 0:
        checkDirections = [_getEastPixel, _getSouthEastPixel,
                _getSouthPixel, _getSouthWestPixel, _getWestPixel]

    elif row == maxrow:
        checkDirections = [_getNorthEastPixel, _getEastPixel, _getWestPixel,
                           _getNorthWestPixel, _getNorthPixel]

    elif col == 0:
        checkDirections = [_getNorthEastPixel, _getEastPixel,
                _getSouthEastPixel, _getSouthPixel, _getNorthPixel]

    elif col == maxcol:
        checkDirections = [_getSouthPixel, _getSouthWestPixel, _getWestPixel,
                            _getNorthWestPixel, _getNorthPixel]
    else:
        checkDirections = _allDirections_
    # end of if row == 0 and col == 0:

    # check for in between pixel
    for direction in checkDirections:
        # all of 8 directions, pixel value should be equal to
        # checkval. i.e. passed row, col (pixel) is pointing on Island Pixel.
        # If any one of 8 directions pixel value is not equal to checkval,
        # then it is not Islan pixel, so return false.
        if direction(data, row, col) != checkval: return False
    # end of for direction in checkDirections:
    # i.e. Island Pixel. so return true.
    return True
# end of def _isIslandPixel(data, row, col, checkval=0):


def _getBoundaryClosedAreaPixels(data, srow, scol):

    boundaryPixels = []
    crow, ccol = -1, -1
    brow, bcol = srow, scol
    mrow, mcol = data.getGrid().shape
    idx = -2
    visited = False
    if _isIslandPixel(data, srow, scol): return [(srow, scol)]

    while((crow, ccol) != (srow, scol)):

        for i, j in _ESWNDirectionsRowCol_:
            crow, ccol = brow + i, bcol + j
            # attains max index, so change the direction
            if crow >= mrow or ccol >= mcol: continue
            # attains min index, so change the direction
            if crow < 0 or ccol < 0: continue
            # check for chosen pixel is on boundary.
            if _isPixelOnBoundary(data, crow, ccol) and \
                        not (crow, ccol) in boundaryPixels:
                # so add chosen pixel to boundary list
                boundaryPixels.append((crow, ccol))
                break
            # end of if _isPixelOnBoundary(data, crow, ccol):
        # end of for i, j in _ESWNDirectionsRowCol_:
        if (crow, ccol) in boundaryPixels or not boundaryPixels:
            # exchange current row, col into boundary row, col
            brow, bcol = crow, ccol
        else:
            # exchange one step previous row, col into boundary row,col
            if visited: idx -= 1
            brow, bcol = boundaryPixels[idx]
            visited = True
        # end of if (crow, ccol) in boundaryPixels or not boundaryPixels:
    # end of while((crow, ccol) != (row, col)):
    return boundaryPixels
# end of def _getBoundaryClosedAreaPixels(data, srow, scol):


def _rowcol2latlon_(pixels, latitude, longitude):

    return [(latitude[row], longitude[col]) for row, col in pixels]
# end of def _rowcol2latlon_(pixels, latitude, longitude):


def irregularClosedRegionSelector(data, latitude, longitude,
                                                overwrite=False, **kwarg):
    """

    Inputs :
        data : 2Dimensional data with proper latAxis and lonAxis.
        latitude : List of latitudes (each represents single lat position,
                                    jointly with corresponding lon position)
        longitude : List of longitude (each represents single lon position,
                                    jointly with corresponding lat position)
           Both latitude & longitudes maked sense to point single pixel in
           the passed data.

        overwrite : Takes boolean True | False (by default)
                    If it is True, then the data's mask will be
                    overwrite with updated mask array out side regions other
                    than passed latitudes, longitudes and its inner pixels
                    of closed latitudes, longitudes (i.e. inside of passed
                    latitude, longitude list).
    Kwarg:
        condition : User can passed any MV2 condition over input data
                    to mask out unwanted values in the resultant region data.

    Output :
        It returns sliced data from original input data with proper masked
        for the irregular selector with latAxis, lonAxis.

        e.g.1 :


    FUNCTION LIMITATION without 'condition' keyword arg:
    ***************************************************
    PS : User can override this limitation by passing 'condition' kwarg.
         See below docstring.

    e.g.2:

    Input :- data and boundary latitudes & longitudes are passed to
             this function.

    data =
   ([[   0       0       0       0       0       0       0     ]
    [    0       0       0     366       0       0       0     ]
    [    0       0       0     726       0       0       0     ]
    [    0       0    1085    1086    1087       0       0     ]
    [    0    1444    1445    1446    1447    1448       0     ]
    [    0    1804    1805    1806    1807    1808       0     ]
    [    0    2164    2165    2166    2167    2168       0     ]
    [    0       0    2525    2526    2527       0       0     ]
    [    0       0    2885       0    2887       0       0     ]
    [    0       0    3245       0    3247       0       0     ]
    [    0       0       0       0       0       0       0     ]],

    mask = False,
    fill_value = 1e+20)


    Actual Output By This Function :-
    *****************************

        This function assumes that passed latitudes, longitudes co-ordinates
        pointing the closed boundary out layer path. So it retains everything
        inside in between two longitudes (columns) at any latitude's (row's).

        In the below actual output of this program to the above input,
        (9th row, 4th column) and (10th rows, 4th column) we will end up
        with input value itself. (here 0s).

        User may not expected any values in 9th and 10th rows Vs 4th column.

   data =
   ([[  --         --         --      --      --      --      --        ]
    [   --         --         --     366      --      --      --        ]
    [   --         --         --     726      --      --      --        ]
    [   --         --       1085    1086    1087      --      --        ]
    [   --       1444       1445    1446    1447    1448      --        ]
    [   --       1804       1805    1806    1807    1808      --        ]
    [   --       2164       2165    2166    2167    2168      --        ]
    [   --         --       2525    2526    2527      --      --        ]
    [   --         --       2885       0    2887      --      --        ]
    [   --         --       3245       0    3247      --      --        ]
    [   --         --         --      --      --      --      --        ]],

     mask =
[[True       True        True        True        True        True      True]
 [True       True        True       False        True        True      True]
 [True       True        True       False        True        True      True]
 [True       True       False       False       False        True      True]
 [True      False       False       False       False       False      True]
 [True      False       False       False       False       False      True]
 [True      False       False       False       False       False      True]
 [True       True       False       False       False        True      True]
 [True       True       False       False       False        True      True]
 [True       True       False       False       False        True      True]
 [True       True        True        True        True        True      True]],
       fill_value = 1e+20)


    But Expected Output By User :-
    **************************

        User may expect the result as follows. But this function can return
        only as shown in above.

    data =
   ([[  --         --         --      --      --      --      --        ]
    [   --         --         --     366      --      --      --        ]
    [   --         --         --     726      --      --      --        ]
    [   --         --       1085    1086    1087      --      --        ]
    [   --       1444       1445    1446    1447    1448      --        ]
    [   --       1804       1805    1806    1807    1808      --        ]
    [   --       2164       2165    2166    2167    2168      --        ]
    [   --         --       2525    2526    2527      --      --        ]
    [   --         --       2885      --    2887      --      --        ]
    [   --         --       3245      --    3247      --      --        ]
    [   --         --         --      --      --      --      --        ]],

     mask =
[[True       True        True        True        True        True      True]
 [True       True        True       False        True        True      True]
 [True       True        True       False        True        True      True]
 [True       True       False       False       False        True      True]
 [True      False       False       False       False       False      True]
 [True      False       False       False       False       False      True]
 [True      False       False       False       False       False      True]
 [True       True       False       False       False        True      True]
 [True       True       False        True       False        True      True]
 [True       True       False        True       False        True      True]
 [True       True        True        True        True        True      True]],
       fill_value = 1e+20)

    FUNCTION LIMITATION OVERRIDE WITH 'condition' keyword arg:
    **********************************************************
    User can override the above limitation by passing 'condition' kwarg.

    e.g.3:

    Input :- data and boundary latitudes & longitudes are passed to
             this function.

    data =
   ([[   0       0       0       0       0       0       0     ]
    [    0       0       0     366       0       0       0     ]
    [    0       0       0     726       0       0       0     ]
    [    0       0    1085    1086    1087       0       0     ]
    [    0    1444    1445    1446    1447    1448       0     ]
    [    0    1804    1805    1806    1807    1808       0     ]
    [    0    2164    2165    2166    2167    2168       0     ]
    [    0       0    2525    2526    2527       0       0     ]
    [    0       0    2885       0    2887       0       0     ]
    [    0       0    3245       0    3247       0       0     ]
    [    0       0       0       0       0       0       0     ]],

    mask = False,
    fill_value = 1e+20)

        >>> c = MV2.masked_equal(data, 0)
        >>> selectedData = irregularClosedRegionSelector(data, lattides,
                                                longitudes, condition=c)
        >>> print selectedData


    data =
   ([[  --         --         --      --      --      --      --        ]
    [   --         --         --     366      --      --      --        ]
    [   --         --         --     726      --      --      --        ]
    [   --         --       1085    1086    1087      --      --        ]
    [   --       1444       1445    1446    1447    1448      --        ]
    [   --       1804       1805    1806    1807    1808      --        ]
    [   --       2164       2165    2166    2167    2168      --        ]
    [   --         --       2525    2526    2527      --      --        ]
    [   --         --       2885      --    2887      --      --        ]
    [   --         --       3245      --    3247      --      --        ]
    [   --         --         --      --      --      --      --        ]],

     mask =
[[True       True        True        True        True        True      True]
 [True       True        True       False        True        True      True]
 [True       True        True       False        True        True      True]
 [True       True       False       False       False        True      True]
 [True      False       False       False       False       False      True]
 [True      False       False       False       False       False      True]
 [True      False       False       False       False       False      True]
 [True       True       False       False       False        True      True]
 [True       True       False        True       False        True      True]
 [True       True       False        True       False        True      True]
 [True       True        True        True        True        True      True]],
       fill_value = 1e+20)

     # As expected values in (9th row, 4th column) and
     # (10th rows, 4th column) are masked.

    Author : Arulalan.T
    Date : 10.07.2014

    """

    condition = kwarg.get('condition', MV2.array([]))

    minBLat, maxBLat = min(latitude), max(latitude)
    minBLon, maxBLon = min(longitude), max(longitude)
    selectedRectDomain = data(latitude=(minBLat, maxBLat, 'ccb'),
                              longitude=(minBLon, maxBLon, 'ccb'))
    selectedRectDomainOriginalMask = selectedRectDomain.mask.copy()
    dummy = MV2.zeros(selectedRectDomain.size, dtype=int)
    dummy = dummy.reshape(selectedRectDomain.shape)
    dummy.setAxisList(selectedRectDomain.getAxisList())

    for lat, lon in zip(latitude, longitude):
        # fills closed boundary pixels with -1
        dummy(latitude=(lat, lat, 'ccb'), longitude=(lon, lon, 'ccb'))[0] = -1
    # end of for lat,lon in zip(latitude, longitude):

    for lat in latitude:
        row = dummy(latitude=(lat, lat, 'ccb'), squeeze=1).tolist()
        if isinstance(row, int): continue

        con = row.count(-1)
        if con >= 2:
            # get first index of -1 in longitudes of particular lat
            first = row.index(-1)
            # get last index of -1 in longitudes of particular lat
            # (here it may has more than two -1s, so get last most index
            # of -1 value)
            end = len(row) - row[::-1].index(-1)
            # fills with -1s in b/w first and last indecies
            dummy(latitude=(lat, lat, 'ccb'), squeeze=1)[first: end] = \
                                    numpy.array([-1] * (end - first))
        # end of if con >= 2:
    # end of for lat in latitude:

    if condition.any():
        # apply user passed condition and fill with our dummy data whereever
        # mask is false (i.e. actual data) and fill with 0s whereever mask
        # is true (i.e. no data in those pixels)
        dummy = MV2.where(condition(latitude=(minBLat, maxBLat, 'ccb'),
                            longitude=(minBLon, maxBLon, 'ccb')), dummy, 0)
    # end of if condition.any():

    # Now make mask equal to 0. i.e. mask other than -1s
    # (where -1 pointing actual boundary pixels. other than closed boundary
    # region, we can mask those pixels)
    dummy = MV2.masked_equal(dummy, 0)

    # get  mask of above dummy array and set to actual selectedRectDomain
    # dataset
    selectedRectDomain.mask = dummy.mask

    # make memory free
    del dummy

    if overwrite:
        # since we set mask to part of cdms2 variable,
        # its already overwritten in the passed data mask itself.
        # So return selectedRectDomain with masked outside of
        # closed boundary pixels
        return selectedRectDomain
    else:
        # here we should not overwritten the passed data's mask.
        # so lets create copy of selectedRectDomain data,mask,axes variable
        selectedRectMaskedDomain = selectedRectDomain.clone()
        # and finally revert back mask to original
        selectedRectDomain.mask = selectedRectDomainOriginalMask
        # lets return copy of selectedRectDomain with masked outside of
        # closed boundary pixels
        return selectedRectMaskedDomain
    # end of if overwrite:
# end of def irregularClosedRegionSelector(...):


def getAllBoundaryOfClosedAreas(data, **kwarg):
    """
    Input : cdms data with proper lat, lon axis.

        Note : This is not actual real data. we need to pass fake data
               (no starting from 1 to mxn) with mask of original data.

               eg:
                    >>> dummy = MV2.arange(1, data.size+1, 1)
                    >>> dummy.mask = data.mask
                    >>> dummy.setAxisList(data.getAxisList())
                    >>> outdict = getAllBoundaryOfClosedAreas(dummy)

    Kwarg :
        update_mask : Takes boolean True | False (by default)
                      If it is True, then the data's mask will be
                      updated with masked array over out side regions other
                      than closed boundaries pixels or (lats, lons) domain.

        condition : User can passed any MV2 condition over input data
                    to mask out unwanted values in the resultant region data.

    Return : It returns dictionary whose keys are 'region%d' % area_number
             starting from 1 to N (available irregular closed regions)

             Each key ['regionN'] contains another dictionary which contains
             following keys & values

             'area'     -> lat, lon weighted area value in m^2 of that
                           particular closed domain/region

             'unit'     -> area unit is m^2

             'bpixels'  -> list of tuples contain (i, j) or (x, y) or
                           (row, col) of boundary pixels of closed domain

             'blatlons' -> list of tuples contain actual (lat, lon) of
                           boundary pixels of closed domain [i.e equivalent
                           (lats, lons) to `bpixels` (rows, cols) ]

             'cpixels'  -> contains dictionary whose keys are 'row' & 'col'.
                         'row' has (min boundary row, max boundary row) tuple,
                         'col' has (min boundary col, max boundary col) tuple
                          of corner pixels of closed irregular domain/region.
                          # Using this user can extract regular rectangle
                          # shaped data by slicing input data.

             'clatlons' -> contains dictionary whose keys are 'lat' & 'lon'.
                         'lat' has (min boundary lat, max boundary lat) tuple,
                         'lon' has (min boundary lon, max boundary lon) tuple
                          of corner pixels of closed irregular domain/region.
                          [i.e. equivalent to 'cpixels' (row, col)]
                          # Using this user can extract regular rectangle
                          # shaped data by passing argument to input cdms var
                          # data(latitude=lat, longitude=lon).

             'region'   -> cdms selector variable (At this moment no use !)

             'totalPixelsCount' -> total no of pixels in that particular
                            closed domain/region


    Author : Arulalan.T

    Date : 08.07.2014

    """

    update_mask = kwarg.get('update_mask', False)
    latAxis = data.getLatitude()
    lonAxis = data.getLongitude()
    lat, lon = data.shape
    min_val = -1
    areadic = {}

    if update_mask:
        # assign mask of selectedRectDomain into original dataset mask.
        # so in original dataset itself outside of closed boundary pixels
        # will be masked.
        dmask = data.mask
        if not dmask.all():
            # i.e. data mask is single False. So lets make data shaped False.
            dmask = MV2.make_mask(data)
        # end of if not dmask.all():
    # end of if update_mask:
    # counter for regions
    count = 0
    while (True):
        dic = {}
        count += 1
        if MV2.masked_equal(data, 0).mask.all(): break

        min_val = MV2.masked_equal(data, 0).min()

        row = min_val / lon
        col = min_val - (lon * row)
        if col > 0: col -= 1

        bPixels = _getBoundaryClosedAreaPixels(data, row, col)
        # store boundary pixels
        dic['bpixels'] = bPixels
        # convert pixels (i, j) into corresponding lat, lon
        bLatLons = _rowcol2latlon_(bPixels, latAxis, lonAxis)
        # store boundary lat, lons
        dic['blatlons'] = bLatLons

        # split list of tuples into corresponding lats,lons
        bLats, bLons = zip(*bLatLons)
        # pixels list of tuples into corresponding rows, cols
        bRows, bCols = zip(*bPixels)

        minBRow, maxBRow = min(bRows), max(bRows)
        minBCol, maxBCol = min(bCols), max(bCols)

        # corner row, col pixels to extract squared/rectangle shaped area
        # to extract correct boundaries
        dic['cpixels'] = {'row': (minBRow, maxBRow), 'col': (minBCol, maxBCol)}
        # corner lat, lon points to extract squared/rectangle shaped area
        # to extract correct boundaries
        dic['clatlons'] = {'lat': (latAxis[minBRow], latAxis[maxBRow]),
                           'lon':(lonAxis[minBCol], lonAxis[maxBCol])}
        # create selector region with latitudes & longitudes of closed area
        region = cdms2.selectors.Selector(cdutil.region.domain(latitude=bLats,
                                                             longitude=bLons))
        # store the above region into dictionary
        dic['region'] = region
        # get the irregularSelector data (i.e. masked outside this
        # irregular closed area)
        selectedRegionData = irregularClosedRegionSelector(data,
                                 latitude=bLats, longitude=bLons,
                                        overwrite=False, **kwarg)
        # counting the no of pixel contains value other than masked pixels.
        dic['totalPixelsCount'] = selectedRegionData.count()
        # compute region area
        oneRegionData = MV2.ones(selectedRegionData.shape)
        oneRegionData = cdms2.createVariable(oneRegionData,
                                    mask=selectedRegionData.mask)
        oneRegionData.setAxisList(selectedRegionData.getAxisList())
        # get the weighted area by sum action and multiply with (111km)^2
        area = cdutil.averager(oneRegionData, axis='xy',
                          weight='weighted', action='sum').data * 1.2321e10
        dic['area'] = area
        dic['unit'] = 'm^2'

        # store dic into global dictionary whose key is no of pixels
        # in the selected region.
        areadic['region'+str(count)] = dic

        zeroRegionData = numpy.zeros(selectedRegionData.shape)
        # fills with 0s in the selected area / region in full dataset,
        # so that we can find next min element index in full dataset.
        data[minBRow: maxBRow+1, minBCol: maxBCol+1] = zeroRegionData

        if update_mask:
            # update dmask boolean array with each closed domain's mask
            dmask[minBRow: maxBRow+1, minBCol: maxBCol+1] = selectedRegionData.mask
        # end of  if update_mask:
    # end of while (min_val == 0):

    if update_mask:
        # and finally set the altered mask to original dataset
        data.mask = dmask.data
    # end of if update_mask:

    # return dictionary
    return areadic
# end of def getAllBoundaryOfClosedAreas(data, latAxis, lonAxis, **kwarg):


def getAreaOfAllClosedDomains(data, condition, **kwarg):

    """
    Input : cdms data with proper lat, lon axis.

    condition : it must be MV2 or numpy.ma masked condition.
        eg1 : condition = MV2.masked_equal(data, 0)

        Using this condition, user can seperate out or distinguish between
        needed domains and unwanted domains.

       eg2:
            >>> condition1 = MV2.masked_less(data, 3)
            >>> condition2 = MV2.masked_greater(data, 5)
            >>> condition3 = MV2.logical_and(condition1, condition2)
            >>> outdict = getAllBoundaryOfClosedAreas(data, condition3)

         The above example2 makes clear that we are masking less than 3 and
         greater than 5 values. So accoring to our `condition3`, we are
         masking out of the range (< 3 && > 5). From this condition3 masked
         data, this function calls `getAllBoundaryOfClosedAreas()` to get
         all closed regions boundary latitudes, longitudes, its no of pixels
         and its weighted area in m^2.

    Kwarg :
        update_mask : Takes boolean True | False (by default)
                      If it is True, then the data's mask will be
                      overwrite with updated mask array out side regions other
                      than closed boundaries pixels or (lats, lons).


    Return : It returns dictionary whose keys are 'region%d' % area_number
             starting from 1 to N (available irregular closed regions)

             Each key ['regionN'] contains another dictionary which contains
             following keys & values

             'area'     -> lat, lon weighted area value in m^2 of that
                           particular closed domain/region

             'unit'     -> area unit is m^2

             'bpixels'  -> list of tuples contain (i, j) or (x, y) or
                           (row, col) of boundary pixels of closed domain

             'blatlons' -> list of tuples contain actual (lat, lon) of
                           boundary pixels of closed domain [i.e equivalent
                           (lats, lons) to `bpixels` (rows, cols) ]

             'cpixels'  -> contains dictionary whose keys are 'row' & 'col'.
                         'row' has (min boundary row, max boundary row) tuple,
                         'col' has (min boundary col, max boundary col) tuple
                          of corner pixels of closed irregular domain/region.
                          # Using this user can extract regular rectangle
                          # shaped data by slicing input data.

             'clatlons' -> contains dictionary whose keys are 'lat' & 'lon'.
                         'lat' has (min boundary lat, max boundary lat) tuple,
                         'lon' has (min boundary lon, max boundary lon) tuple
                          of corner pixels of closed irregular domain/region.
                          [i.e. equivalent to 'cpixels' (row, col)]
                          # Using this user can extract regular rectangle
                          # shaped data by passing argument to input cdms var
                          # data(latitude=lat, longitude=lon).

             'region'   -> cdms selector variable (At this moment no use !)

             'totalPixelsCount' -> total no of pixels in that particular
                            closed domain/region


    eg:

    Input :
    *******

    data =
   ([[ 0.  0.  0.  0.  0.  0.  0.]
     [ 0.  0.  0.  3.  0.  0.  0.]
     [ 0.  0.  0.  3.  0.  0.  0.]
     [ 0.  0.  3.  2.  3.  0.  0.]
     [ 0.  4.  2.  1.  1.  2.  0.]
     [ 0.  1.  4.  3.  5.  4.  0.]
     [ 0.  2.  2.  1.  3.  5.  0.]
     [ 0.  0.  3.  2.  3.  0.  0.]
     [ 0.  0.  3.  0.  1.  0.  0.]
     [ 0.  0.  3.  0.  1.  0.  0.]
     [ 0.  0.  0.  0.  0.  0.  0.]],

     mask = False,
     fill_value = 1e+20)

 >>> condition = MV2.masked_equal(data, 0)
 >>> outdict = getAllBoundaryOfClosedAreas(data, condition, update_mask=True)

    Outputs :
    *********

    data =
([[--    --    --    --    --    --    --]
  [--    --    --   3.0    --    --    --]
  [--    --    --   3.0    --    --    --]
  [--    --   3.0   2.0   3.0    --    --]
  [--   4.0   2.0   1.0   1.0   2.0    --]
  [--   1.0   4.0   3.0   5.0   4.0    --]
  [--   2.0   2.0   1.0   3.0   5.0    --]
  [--    --   3.0   2.0   3.0    --    --]
  [--    --   3.0    --   1.0    --    --]
  [--    --   3.0    --   1.0    --    --]
  [--    --    --    --    --    --    --]],

     mask =
[[ True  True  True  True  True  True  True]
 [ True  True  True False  True  True  True]
 [ True  True  True False  True  True  True]
 [ True  True False False False  True  True]
 [ True False False False False False  True]
 [ True False False False False False  True]
 [ True False False False False False  True]
 [ True  True False False False  True  True]
 [ True  True False  True False  True  True]
 [ True  True False  True False  True  True]
 [ True  True  True  True  True  True  True]],

     fill_value = 1e+20)

    # keys contains no of independent closed boundary pixels count
    >>> outdict.keys()
    ['region1', 'region2', 'region3', 'region4']
    [40, 27, 270, 54]

    # eg : region2
    >>> outdict['region2'].keys()
    ['area', 'region', 'bpixels', 'blatlons',
    'cpixels', 'clatlons', 'totalPixelsCount', 'unit']

    # total no of valid pixels within the irregular closed domain
    >>> outdict['region2']['totalPixelsCount']
    27

    # weighted area of particular closed boundary region (here 27 pixels)
    >>> outdict['region2']['area']
    902159.07029304397

    # area unit
    >>> outdict['region2']['unit']
    'm^2'

    # boundary lat, lon of particular closed boundary region
    >>> outdict['region2']['blatlons']
    [(-87.5, -174.5), (-86.5, -174.5), (-86.5, -173.5), (-85.5, -173.5),
    (-85.5, -172.5), (-84.5, -172.5), (-83.5, -172.5), (-83.5, -173.5),
    (-82.5, -173.5), (-81.5, -173.5), (-80.5, -173.5), (-82.5, -174.5),
    (-82.5, -175.5), (-81.5, -175.5), (-80.5, -175.5), (-83.5, -175.5),
    (-83.5, -176.5), (-84.5, -176.5), (-85.5, -176.5), (-85.5, -175.5),
    (-86.5, -175.5), (-88.5, -174.5)]

    # boundary row, col of particular closed boundary region
    >>> outdict['region2']['bpixels']
    [(2, 5), (3, 5), (3, 6), (4, 6), (4, 7), (5, 7), (6, 7), (6, 6), (7, 6),
    (8, 6), (9, 6), (7, 5), (7, 4), (8, 4), (9, 4), (6, 4), (6, 3), (5, 3),
    (4, 3), (4, 4), (3, 4), (1, 5)]

    # corner lat, lon of above closed irregular region
    >>> dic['region2']['clatlons']
    {'lat': (-88.5, -80.5), 'lon': (-176.5, -172.5)}

    # corner row, col of above closed irregular region
    >>> dic['region2']['cpixels']
    {'col': (3, 7), 'row': (1, 9)}


    # eg : region4
    # total no of valid pixels within the irregular closed domain
    >>> outdict['region4']['totalPixelsCount']
    54

    # area of 54 pixels
    >>> outdict['region4']['area']
    843696.5895938098

    >>> outdict['region4']['blatlons']
    [(-89.5, -58.5), (-89.5, -57.5), (-89.5, -56.5), (-89.5, -55.5),
    (-89.5, -54.5), (-89.5, -53.5), (-89.5, -52.5), (-89.5, -51.5),
    (-88.5, -51.5), (-87.5, -51.5), (-86.5, -51.5), (-85.5, -51.5),
    (-84.5, -51.5), (-84.5, -52.5), (-84.5, -53.5), (-84.5, -54.5),
    (-84.5, -55.5), (-84.5, -56.5), (-84.5, -57.5), (-84.5, -58.5),
    (-84.5, -59.5), (-85.5, -59.5), (-86.5, -59.5), (-87.5, -59.5),
    (-88.5, -59.5), (-89.5, -59.5)]

    # By comparing above Area of 'region2' (27 pixels) is greater than
    # Area of 'region4' (54 pixels) since its weighted area.
    # i.e. it is totally depends on the lat, lon positions

    Note : outdict 'blatlons' contains only outer boundary lat,lons only.
           But area will be calculated w.r.t no of pixels inside the
           closed boundary region and over on the boundary of region.

    Author : Arulalan.T <arulalant@gmail.com>

    Date : 08.07.2014

    """

    update_mask = kwarg.get('update_mask', False)
    # update condition arg to kwarg dictionary
    kwarg['condition'] = condition

    dshape = data.shape
    # it must start with 1, since we masked out side areas/ regions with 0s.
    dummy = numpy.arange(1, data.size + 1, 1)
    dummy = dummy.reshape(dshape)

    # apply user passed condition and fill with our dummy data whereever mask
    # is false (i.e. actual data) and fill with 0s whereever mask is true
    # (i.e. no data in those pixels)
    dummy = MV2.where(condition, dummy, 0)
    # set missing_value as 0. so that filled() return 0s in masked pixels.
    dummy.missing_value = 0
    # Now dummy contains zeros other than needed areas and
    # inside & boundar of needed areas filled with some nos.
    # Here set missing_value as big no & set original data mask to dummy.
    dummy = cdms2.createVariable(dummy.filled(), id=('dummy'),
                        missing_value=data.fill_value, mask=data.mask)
    dummy.setAxisList(data.getAxisList())

    area_irregular_domains = getAllBoundaryOfClosedAreas(dummy, **kwarg)

    if update_mask:
        # update input data mask with dummy mask (masked other than needed
        # irregular regions) along with user passed condition

        # apply logical_and condition with (not of dummy.mask)
        finalmask = MV2.logical_and(condition, MV2.logical_not(dummy.mask))
        # apply original data whereever both condition and dummy's mask
        # becomes true, apply nan whereever false comes.
        data.mask = MV2.where(finalmask, data, numpy.nan).mask
    # end of if update_mask:

    # return the dictionary of area_irregular_domains
    return area_irregular_domains
# end of def getAreaOfAllClosedDomains(data, condition, **kwarg):

