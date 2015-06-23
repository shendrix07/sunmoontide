# -*- coding: utf-8 -*-
"""This module builds Tides objects from NOAA Annual Tide Prediction text
files, with helper functions that may be useful in other applications.
Search for `&**&` to find code segments that assume a certain format for the
NOAA text file input. Last updated 6/8/2015 by Sara Hendrix.
"""

import itertools
import numpy as np
import math
import pandas as pd
import pkgutil
from io import BytesIO

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def sine_interp(height1, height2, resolution, remove_end=False):
    """ Interpolate a half sine wave between two heights.

    Args:
        height1 (float): the starting height
        height2 (float): the ending height
        resolution (int):  the resolution desired (length of returned array)
                           must be >2
        OPTIONAL:
        remove_end (boolean): if True, the function removes the last element
                              (height2) of the result. This can be useful when
                              appending subsequent high/low interpolations.
        
    Returns:
    For default optional argument (remove_end = False):
        y: a 1D array of floats with length `resolution`.
        y[0] == height1, y[res-1] == height2
    If optional argument remove_end = True:
        y will instead have length `resolution`-1; the final value is removed.
    y will be a peak-to-trough half wave for height1 > height2,
        a trough-to-peak half wave for height1 < height2,
        and a flat line for height1 == height2.

    Examples:
    >>> yy = sine_interp(-1.2, -6.2, 5)
    >>> print(yy)
    [-1.2        -1.93223305 -3.7        -5.46776695 -6.2       ]
    >>> yy = sine_interp(6.2, 1.2, 5)
    >>> print(yy)
    [ 6.2         5.46776695  3.7         1.93223305  1.2       ]
    >>> yy = sine_interp(-6.2, -1.2, 5)
    >>> print(yy)
    [-6.2        -5.46776695 -3.7        -1.93223305 -1.2       ]
    >>> yy = sine_interp(-6.2, -1.2, 5, True)
    >>> print(yy)
    [-6.2        -5.46776695 -3.7        -1.93223305]
    """
    h1 = float(height1)
    h2 = float(height2)
    assert(type(resolution) is int)
    assert(resolution > 2)
    
    amp = (max(h1, h2) - min(h1, h2)) / 2.  # amplitude
    bump = max(h1, h2) - amp                # vertical offset

    if h1 < h2:
        # -pi/2 to pi/2 => trough-to-peak
        x = np.linspace(-math.pi / 2., math.pi / 2., resolution)
    else:
        # pi/2 to (3/2)*pi => peak-to-trough
        x = np.linspace(math.pi / 2., (3. / 2.) * math.pi, resolution)
    
    y = amp * np.sin(x) + bump
    
    # round off for float comparison
    assert(round(y[0], 8) == round(height1, 8))
    assert(len(y) == resolution)
    assert(round(y[resolution-1], 8) == round(height2, 8))

    if remove_end == True:
        return y[0:resolution-1]
    else:
        return y


def read_noaa_header(filename):
    """ Return the metadata in the header of a NOAA Annual Tide Prediction
    text file, plus the line of column names. Assumes headers are separated
    from main data table by a single blank/whitespace-only line, and then
    the next line is the column names.

    &**& This entire function is heavily dependent on the NOAA file format.
         Last updated for 2015 annual files.

    Args:
        filename (str): the name of a NOAA Annual Tide Prediction text file
                        in the current interpreter directory, or path to file
    
    Returns:
      metadata, column_header
        metadata (dict): all file header information, split on ': '. Keys are
                         whatever came before ': ', values whatever came after.
                         Both keys and values are strings and provided as read
                         from the file - no stripping or reformatting.
                         If header line has no ': ' substring, the key contains
                         the whole line, and value = ''.
        column_names (string): the file line containing column names.  

    Examples:
    
    >>> metdat, colhead = read_noaa_header('example_NOAA_file.TXT')
    >>> metdat['Time Zone'].strip()
    'LST/LDT'
    >>> colhead.split()
    ['Date', 'Day', 'Time', 'Pred(Ft)', 'Pred(cm)', 'High/Low']

    """
    metadata = {}
    with open(filename, 'r') as file:
        for line in file:
            if line.isspace():
                    break
            elif line.find(': ') >= 0:
                k, v = line.split(': ')
            else:
                k = line
                v = ''
            metadata[k] = v
        column_names = file.readline()
    
    def _check_that(Boolean_valued_statement):
        """If `Boolean_valued_statement` is False, raise a detailed error."""
        if not Boolean_valued_statement:
            error_message = ('In Tides, read_noaa_header found a problem in ' +
                            filename +'.\nThis file failed a header format ' +
                            'check. (`_check_that` in Traceback above.)' +
                            '\nSee example_noaa_file.TXT for an example ' +
                            'of the expected file format.')
            raise ValueError(error_message)
    
    _check_that(metadata['NOAA/NOS/CO-OPS\n'] == '')
    _check_that(metadata['Product Type'].strip() == 'Annual Tide Prediction')
    _check_that(metadata['Interval Type'].strip() == 'High/Low Tide Predictions')
    _check_that(metadata['Time Zone'].find('LST') >= 0)
    _check_that(metadata['Stationid'])
    expected_column_names = ['Date', 'Day', 'Time', 'Pred(Ft)',
                             'Pred(cm)', 'High/Low']
    col_names = column_names.split()
    _check_that(col_names == expected_column_names)

    return metadata, column_names


def lookup_station_info(StationID):
    """  Given a NOAA tide prediction station ID, look it up in
    station_info.csv and return the information in a dict.
    
    station_info.csv has the following columns:
    StationID, StationName, State, Latitude, Longitude, StationType, Timezone
        
    Args:
        StationID (string): a NOAA station ID code.
        
    Returns:
        info (dict of strings): the lookup information for the given station.
        Keys are: st_id, name, state, latitude, longitude, st_type, timezone

    Examples:
    
    >>> info = lookup_station_info('8731439')
    >>> info['name']
    'Gulf Shores, Icww'
    >>> info['timezone']
    'US/Central'
"""
    try:
        lookup = pkgutil.get_data('tides', 'station_info.csv')
    except Exception as e:
        error_message = ('In Tides, lookup_station_info could not find ' +
            'its lookup file, station_info.csv. Error: ' + e)
        raise IOError(error_message)

    all_data = pd.read_csv(BytesIO(lookup), index_col=0)
    try:
        station_data = all_data.loc[StationID]
    except Exception as e:
        error_message = ('In Tides, lookup_station_info could not find ' +
        'Station ID ' + StationID + ' in its lookup dataset. Error: ' + e +
        '... Make sure ' + StationID + ' is present in station_info.csv.')
        raise ValueError(error_message)
            
    info = {}
    info['st_id']     = StationID
    info['name']      = station_data['StationName']
    info['state']     = station_data['State']
    info['latitude']  = station_data['Latitude']
    info['longitude'] = station_data['Longitude']
    info['st_type']   = station_data['StationType']
    info['timezone']  = station_data['Timezone']
    return info


def build_all_tides(raw_tides, resolution, use_column, extend_ends=False):
    """ Interpolate tide magnitudes and timestamps from given highs/lows.
    
    Args:
        raw_tides: a pandas DataFrame with datetime index.
           (i.e. the result of a pandas.read_csv with parse_dates utilized)
           The DatetimeIndex must be in UTC.
        resolution (integer > 2): the resolution for the interpolation;
                                  includes both endpoints for each interval.
        use_column (string): the name of the column of rawtides to use for the
                             tide high/low magnitudes.
    
    Optional:
        extend_ends: if True, the function will extend the beginning and end of
            the time series by repeating raw_tides[1] 7 hours before the actual
            raw_tides[0], and repeating raw_tides[-2] 7 hours after the actual
            raw_tides[-1]. This is for the Sun * Moon * Tide calendar to avoid
            an odd visual cut off in the first hours of Jan 1 when raw_tides
            begins after midnight, and also in the last hours of Dec 31 when
            raw_tides ends before midnight.

    Returns:
        all_tides: a pandas timeseries of sine interpolated tides,
                   with datetime index localized to UTC.
    """
    assert(raw_tides.index.tzinfo.zone == 'UTC')    
    assert(type(resolution) is int)
    assert(resolution > 2)
    
    raw_values = eval('raw_tides.' + use_column)
    alltides = []
    tidetimes = []
    
    if extend_ends:
        # interpolate from second tide height to first tide height
        initial_interps = sine_interp(raw_values[1], raw_values[0],
                                      resolution, True)
        alltides.append(initial_interps)
        # start 7 hours before first tide extreme
        a = np.datetime64(raw_tides.index[0]) - np.timedelta64(7, 'h')
        b = np.datetime64(raw_tides.index[0])
        step = np.timedelta64((b - a) / (resolution - 1))
        initial_times = np.arange(a, b, step)
        initial_times = initial_times[:resolution - 1]
        tidetimes.append(initial_times)
        
    
    for value_a, value_b in pairwise(raw_values):
        interps = sine_interp(value_a, value_b, resolution, True)
        assert(len(interps) == (resolution - 1))
        alltides.append(interps)
    alltides = np.array(alltides).flatten()
    # add on the last tide value, left out of the loop
    alltides = np.append(alltides, raw_values[-1])

    # create datetime index for alltides, with even spacing between each 
    # subsequent high/low time from the raw_tides datetime index.    
    for time_a, time_b in pairwise(raw_tides.index):
        a = np.datetime64(time_a)
        b = np.datetime64(time_b)
        step = np.timedelta64((b - a) / (resolution-1))
        interv = np.arange(a, b, step)
        # assure proper length of time interval
        interv = interv[:resolution-1]
        assert(len(interv) == (resolution - 1))
        tidetimes.append(interv)
    tidetimes = np.array(tidetimes, dtype = 'datetime64[us]').flatten()
    # add on the last datetime, left out of the loop
    last_one = np.datetime64(raw_tides.index[-1])
    assert(np.dtype(tidetimes[1]) == np.dtype(last_one))
    tidetimes = np.append(tidetimes, last_one)
    
    if extend_ends:
        # interpolate from last tide height to next-to-last tide height
        interps = sine_interp(raw_values[-1], raw_values[-2], resolution, False)
        alltides = np.append(alltides, interps)
        # start 10 seconds after last tide extreme
        a = np.datetime64(raw_tides.index[-1]) + np.timedelta64(10, 's')
        b = a + np.timedelta64(7, 'h')  # 7 hours later
        step = np.timedelta64((b - a) / (resolution-1))
        interv = np.arange(a, b, step)
        tidetimes = np.append(tidetimes, interv)

    assert(len(tidetimes)==len(alltides))
    all_tides = pd.Series(alltides,tidetimes)
    all_tides.index = all_tides.index.tz_localize('UTC')
    return all_tides



class Tides:
    """A class with everything related to a NOAA annual tide prediction file.
    Purpose is to calculate and then store the various input required to graph
    tides and provide station information for a Sun * Moon * Tide calendar.
    """
    def __init__(self, NOAA_filename):
        """Take the filename and build everything that needs to be built.
        After this is done, all attributes are set and everything is ready for
        plotting and queries.
        """
        metadata, col_names = read_noaa_header(NOAA_filename)
        self.station_id = metadata['Stationid'].strip() # &**& format dependant
        info = lookup_station_info(self.station_id)
        self.station_name = info['name']
        self.state = info['state']
        self.latitude = info['latitude']
        self.longitude = info['longitude']
        self.station_type = info['st_type']
        self.timezone = info['timezone']
        num_rows_to_skip = len(metadata) + 2
        resolution = 200        # hi res sometimes needed for sparse rawtides
        
# ------------ Read annual tide table into pandas DataFrame--------------
# NOTE: &**& format dependant - main high/low data column name = 'ft'
        rawtides = pd.read_csv(NOAA_filename,
                       names = ['Date', 'Day', 'Time', 'AM/PM', 
                                'ft', 'cm', 'High/Low'],
                       delim_whitespace = 1, skiprows = num_rows_to_skip,
                       parse_dates = {'TimeIndex' :
                                        ['Date', 'Day', 'Time', 'AM/PM']},
                       index_col=0)
        del rawtides['High/Low']
        del rawtides['cm']
        rawtides.index = rawtides.index.tz_localize(self.timezone)
        # convert to UTC for calculations        
        rawtides.index = rawtides.index.tz_convert('UTC')
        self.all_tides = build_all_tides(rawtides, resolution, 'ft',
                                         extend_ends = True) # &**&
        self.all_tides.index = self.all_tides.index.tz_convert(self.timezone)
        # back to local time, ready for plotting        
        rawtides.index = rawtides.index.tz_convert(self.timezone)
        self.raw_tides = rawtides

        if self.station_type == 'Subordinate':
            self._set_reference_station_info(metadata)

        self.year = str(self.raw_tides.index[100].year)
        self.annual_max = max(rawtides.ft)     # &**&
        self.annual_min = min(rawtides.ft)     # &**&

    def _set_reference_station_info(self,metadata):
        """Set attributes for reference station information, if station type
        is subordinate. Argument: a dict of metadata in the format returned by
        `read_noaa_header`. This function is heavily dependant on NOAA text
        file format. &**& """
        self.ref_station_id = metadata['ReferenceToStationId'].strip()
        ref_info = lookup_station_info(self.ref_station_id)
        self.ref_station_name = ref_info['name']
        # height offsets are a multiplicative factor
        self.height_offset_low = metadata['HeightOffsetLow'].strip('*').strip()
        self.height_offset_high = metadata['HeightOffsetHigh'].strip('*').strip()
        # time offsets are in minutes + or -
        self.time_offset_low = metadata['TimeOffsetLow'].strip()
        self.time_offset_high = metadata['TimeOffsetHigh'].strip()



if __name__ == "__main__":
    import doctest
    doctest.testmod()