import pandas as pd
import numpy as np
import math
import datetime as DT
import time
import geopy
from geopy.geocoders import GoogleV3
import pytz
from pytz import timezone

# TODO import whatever is needed to run doctests - it is not working in new version of ipython



def SineInterp(height1, height2, resolution, remove_end=False):
    """ a half-sine-wave interpolation between extrema heights
    
    Args:
        height1 (float): the starting height
        height2 (float): the ending height
        resolution (int):  the resolution desired (length of returned array), must be >2

        OPTIONAL:
        remove_end (boolean): if True, the function removes the last element (height2) of the result.
                            This can be useful when appending many subsequent high/low interpolations.
        
    Returns:
    For default optional argument (`remove_end = False`):
        y (array of floats): a 1D array of length `resolution`.
        y[0]==height1, y[res-1]==height2
    If optional argument is passed as True (`remove_end = True`):
        y will instead have length `resolution`-1; the final value y[res-1]==height2 will have been removed
    y will be a peak-to-trough half wave for height1>height2,
        a trough-to-peak half wave for height1<height2, a flat line for height1=height2

    Asserts:
        Preconditions: Args all have usable types (heights cast as float successfully) and `resolution`>2
        Postconditions: y is length `resolution`, starts with `height1`, ends with `height2`
                            unless `remove_end==True`, in which case y is length `resolution`-1
            Floating point equality is satisfied here when the numbers are equal to 8 decimal places (rounded off)
        
    Examples: (using `print` to achieve rounding off for the floating point values)
    
    >>> yy = SineInterp(-1.2, -6.2, 5)
    >>> print yy
    [-1.2        -1.93223305 -3.7        -5.46776695 -6.2       ]
    
    >>> yy = SineInterp(6.2, 1.2, 5)
    >>> print yy
    [ 6.2         5.46776695  3.7         1.93223305  1.2       ]
    
    >>> yy = SineInterp(-6.2, -1.2, 5)
    >>> print yy
    [-6.2        -5.46776695 -3.7        -1.93223305 -1.2       ]
    
    >>> yy = SineInterp(-6.2, -1.2, 5, True)
    >>> print yy
    [-6.2        -5.46776695 -3.7        -1.93223305]
    
    
    """
    
    h1 = float(height1)
    h2 = float(height2)
    assert(type(resolution) is int)
    assert(resolution > 2)
    
    amp = (max(h1, h2) - min(h1, h2)) / 2.  # amplitude
    bump = max(h1, h2) - amp                # vertical offset

    if h1 < h2:
        xtmp = np.linspace(-math.pi / 2., math.pi / 2., resolution)       # -pi/2 to pi/2 => trough-to-peak
    else:
        xtmp = np.linspace(math.pi / 2., (3. / 2.) * math.pi, resolution) # pi/2 to (3/2)*pi => peak-to-trough
    
    y = amp * np.sin(xtmp) + bump
    
    assert(round(y[0], 8) == round(h1, 8))     # rounding off to 8 decimal places to compare floats easily
    assert(len(y) == res)
    assert(round(y[res-1], 8) == round(h2,8)) # rounding off to 8 decimal places to compare floats easily

    if remove_end == True:
        return y[0:res-1]
    else:
        return y
    


## TODO - get user input for filename, parse text header

##This part should probably go in a station class?

from geopy.geocoders import GoogleV3
geolocator = GoogleV3()
geopoint = geopy.Point(station.latitude, station.longitude)
TZ_py = geolocator.timezone(mypoint)
station.timezone = TZ_py.zone

### TODO
ThisTZ = 'US/Pacific'
TidesFilePath = "Desktop/9413745.Annual.TXT" # this is the Santa Cruz tide data for 2015
NumberOfRowsToSkip = 20

### This snippet is ready for action...
# read annual tide table into pandas DataFrame
rawtides = pd.read_csv(TidesFilePath,
                       names = ["Date", "Day", "Time", "AM/PM", "ft", "cm", "High/Low"],
                       delim_whitespace = 1, skiprows = NumberOfRowsToSkip,
                       parse_dates = {'TimeIndex':['Date', 'Day', 'Time', 'AM/PM']},
                       index_col=0)
del rawtides["High/Low"] # we don't need to be told this, it is obvious to SineInterp
del rawtides["cm"]       # this is America

# localize to correct time zone, then convert to UTC. This avoids Daylight Savings issues.
# will convert back to local time zone when ready to graph plots
rawtides.index = rawtides.index.tz_localize(ThisTZ).tz_convert('UTC')

#rawtides is a  <class 'pandas.core.frame.DataFrame'> with a single time-indexed column.
#time index (rawtides.index) is a  <class 'pandas.tseries.index.DatetimeIndex'>
#the column of actual data/magnitudes (rawtides.ft) is a  <class 'pandas.core.series.Series'>
#rawtides.index[1] is a  <class 'pandas.tslib.Timestamp'>
#rawtides.ft[1] is a  <type 'numpy.float64'>
#the overall shape/dimensions of rawtides is  (1414, 1)

resolution = 20
highlow_count = len(rawtides.ft)

alltides = np.zeros([highlow_count-1,resolution-1],dtype=float) #initialize

# build 2D array with rows containing subsequent interpolation intervals
for i in range(highlow_count-1):
    interps = SineInterp(rawtides.ft[i],rawtides.ft[i+1],resolution,True)
    alltides[i] = interps

alltides = alltides.reshape((highlow_count-1)*(resolution-1))

alltides = np.append(alltides,rawtides.ft[highlow_count-1]) # add on the last element, left out of the loop


#initialize
tidetimes = np.arange(rawtides.index[0], rawtides.index[1], (rawtides.index[1]-rawtides.index[0])/(resolution-1))
tidetimes = tidetimes[:resolution-1]

# build list with rows containing subsequent time intervals. This will match with alltides1.
for i in range(1,highlow_count-1):
    interv = np.arange(rawtides.index[i],rawtides.index[i+1],(rawtides.index[i+1]-rawtides.index[i])/(resolution-1))
    interv = interv[:resolution-1]
    assert(len(interv)==(resolution-1))
    tidetimes = np.append(tidetimes,interv)

# add the last datetime, which was left out of the loop
last_one = rawtides.index[len(rawtides.index)-1]  #this is a pandas timestamp, need to convert it
last_one = np.datetime64(last_one)        #now it is a numpy datetime64

assert(np.dtype(tidetimes[1])==np.dtype(last_one)) #before appending last one, make sure datatypes are consistent

tidetimes = np.append(tidetimes,last_one)
assert(len(tidetimes)==len(alltides))  #make sure have times for all tide points & vice versa


Tides = pd.Series(alltides,tidetimes)
Tides.index = Tides.index.tz_localize('UTC').tz_convert(ThisTZ)

