# -*- coding: utf-8 -*-
"""
This module builds Astro objects, including special attributes for
lunar phases (if Astro object is named 'Moon') and solar equinoxes/solstices
(if Astro object is named 'Sun'). Also includes some helper functions that may
be useful in other applications.
"""

import datetime
import ephem
import numpy as np
import pandas as pd
import pytz


def copy_ephem_observer(original_observer):
    """ephem.Observer objects are missing a copy method. So this returns a
    brand new Observer object whose attributes have been set to the same values
    as in the original observer."""
    new_observer = ephem.Observer()
    new_observer.date = original_observer.date
    new_observer.epoch = original_observer.epoch
    new_observer.long = original_observer.long
    new_observer.lat = original_observer.lat
    new_observer.elev = original_observer.elev
    new_observer.temp = original_observer.temp
    new_observer.pressure = original_observer.pressure
    new_observer.horizon = original_observer.horizon
    return new_observer


def utc_year_bounds(time_zone, year):
    """Given a tzdata/IANA time zone name (string) and a year (can be a string
    or integer), returns two ephem.Date objects corresponding to local midnight
    on Jan 1 of the year, and local time of one second before midnight on
    Dec 31 of the year, in the given timezone. ephem.Date objects are always in
    UTC.
    
    Examples:
    (note: Los Angeles winter time is -0800, i.e. 8 hours behind UTC)

    >>> start, stop = utc_year_bounds('America/Los_Angeles', '2016')
    >>> print(start.datetime().strftime("%Y-%m-%d %H:%M:%S"))
    2016-01-01 08:00:00
    >>> print(stop.datetime().strftime("%Y-%m-%d %H:%M:%S"))
    2017-01-01 07:59:59

    >>> import tzlocal
    >>> my_tz = tzlocal.get_localzone().zone
    >>> alpha, omega = utc_year_bounds(my_tz, 2010)
    >>> print((ephem.localtime(alpha)).strftime("%Y-%m-%d %H:%M:%S"))
    2010-01-01 00:00:00
    >>> print((ephem.localtime(omega)).strftime("%Y-%m-%d %H:%M:%S"))
    2010-12-31 23:59:59
    """
    begin = datetime.datetime(int(year), 1, 1)
    end = datetime.datetime(int(year), 12, 31, 23, 59, 59)
    # make no assumptions about constant offsets, even for similar day of year
    begin_raw_offset = pytz.timezone(time_zone).localize(begin).strftime('%z')
    end_raw_offset = pytz.timezone(time_zone).localize(end).strftime('%z')
    # raw offsets are strings of the form '+HHMM' or '-HHMM'; H=hour, M=minute

    def _parse_UTC_offset(raw_offset: str):
        """arg must be a UTC offset of the form '+HHMM' or '-HHMM'; H = hour,
        M = minute. returns (float) number of days offset, Boolean indicating
        whether offset is ahead (False) or behind (True) UTC.
        """
        assert(len(raw_offset) == 5) #valid raw UTC offsets are '+HHMM'/'-HHMM' 
        if raw_offset[0] == '+':
            behind = False
        elif raw_offset[0] == '-':
            behind = True
        else:
            raise ValueError('raw timezone offsets are not in expected format')
        hour = int(raw_offset[1:3])
        minute = int(raw_offset[3:])
        days = (hour + (minute / 60)) / 24
        return days, behind
    
    def _make_offset_ephemDates(date_time, days, behind):
        """arg types: datetime.datetime, float, Boolean. return type: ephem.Date"""
        if behind:
            return ephem.Date(ephem.Date(date_time) + days)
        else:
            return ephem.Date(ephem.Date(date_time) - days)
    
    begin_days, begin_behind = _parse_UTC_offset(begin_raw_offset)
    begin_result = _make_offset_ephemDates(begin, begin_days, begin_behind)
    end_days, end_behind = _parse_UTC_offset(end_raw_offset)
    end_result = _make_offset_ephemDates(end, end_days, end_behind)
    
    return begin_result, end_result


def fill_in_heights(start, stop, step, observe, body_name, append_NaN=True):
    """Return a sequential list of times and heights at given step
    resolution, for an astronomical body's altitude over time.
    
    Arguments:
        start (ephem.Date): the initial time
        stop (ephem.Date): the final time (will be included in the result)
        step (float): a step size in days (i.e. 15 minutes = 15 / (60 * 24))
        observe (ephem.Observer): pre-initialized ephem.Observer() object
            with location information set; it will be copied to prevent
            alteration of the original observer object's date attribute
        body_name (str): a title-case ephem body name, i.e. 'Sun' or 'Moon'
        
    Optional: append_NaN defaults to True, which will append a NaN value to
    the end of the result, to provide breaks between plotted line segments.
    
    Returns:
        times, heights
        times: a list of sequential timezone-naive datetimes (actually in UTC)
        heights: a list of floats, providing sin(altitude) of the body at
            each time
        len(times) == len(heights)
        
    Example:
    >>> barrow = ephem.Observer()
    >>> barrow.lat, barrow.lon = '71.36', '-156.7'
    >>> time1 = ephem.Date((2016, 4, 1, 12, 0, 0))
    >>> time2 = ephem.Date(time1 + 5)
    >>> ti, he = fill_in_heights(time1, time2, 0.1, barrow, 'Sun')
    >>> ti[0]
    datetime.datetime(2016, 4, 1, 12, 0)
    >>> he[0]
    -0.215011881685818
    >>> ti[-1]
    datetime.datetime(2016, 4, 6, 12, 0, 0, 864000)
    >>> he[-1]
    nan
    >>> ti[-2]
    datetime.datetime(2016, 4, 6, 12, 0)
    >>> he[-2]
    -0.18191711151931395
    """
    times = []
    heights = []
    obs = copy_ephem_observer(observe)
    obs.date = start
    body = eval('ephem.' + body_name + '(obs)')
    
    while obs.date < stop:
        times.append(obs.date.datetime())
        
        body.compute(obs) # compute new body position for the new observer time
        height_now = np.sin(body.alt) # sin(altitude) of the new body position
        heights.append(height_now)

        obs.date += step # observer moves forward one time step
        
    obs.date = stop  # observer moves to exact stopping time
    times.append(obs.date.datetime())

    body.compute(obs)
    height_now = np.sin(body.alt)
    heights.append(height_now)
                
    if append_NaN:
        times.append(ephem.Date(obs.date + 0.00001).datetime())
        heights.append(float('NaN'))
    
    assert(len(times) == len(heights))        
    return times, heights



class Astro:
    """A class with year- and location-specific rise/set/altitude for an
    astronomical object. Sun and Moon have additional special information.
    Provies all input required to graph sun, moon, or other astronomical body
    for a Sun * Moon * Tide calendar.
    """
    def __init__(self, latitude: str, longitude: str, timezone: str, year: str,
                 name: str):
        """Take the all necessary inputs and construct plot-ready astronomical
        object time series for calendar. Attributes are all set and ready for
        queries and plotting after __init__.
        
        Arguments: (all keyword-only)
        latitude = latitude in decimal degrees as a string, i.e. '36.9577'
        longitude = longitude in decimal degrees as a string, i.e. '-122.0402'
        timezone = tzdata/IANA time zone as a string, i.e. 'America/Los_Angeles'
        year = the year desired for the calendar, as a string, i.e. '2016'
        name = the name of the astronomical body as a string, first letter
               capitalized, i.e. 'Sun' or 'Moon'
        """
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self.year = year
        self.name = name
        
        observer = ephem.Observer()
        observer.lat = ephem.degrees(latitude)
        observer.long = ephem.degrees(longitude)
        observer.elevation = 0
        
        begin, end = utc_year_bounds(timezone, year)
        step = 15 * ephem.minute #resolution of full timeseries of body heights
        
        observer.date = begin
        body = eval('ephem.' + name + '(observer)')
        '''The body will need to be re-computed every time the observer's
            date changes. E.g. `body.compute(observer)` '''                
        
        '''BUILD THE rise_noon_set TIMESERIES ATTRIBUTE'''
        r_n_s_times = []
        r_n_s_labels = []        
        
        '''Until the end of the year, get each day's rise, noon/transit, set.'''
        while observer.date <= end:
            rns = [(body.rise_time, 'rise'),
                   (body.transit_time, 'noon'),
                   (body.set_time, 'set')]
            '''If any of these could not be computed, i.e. for the Sun above
            the Arctic Circle in winter or summer, the time will be None.'''
            for i, t in reversed(list(enumerate(rns))):
                if t[0] == None:
                    rns.remove(t)
            rns.sort()   # ensure chronological order
            for t in rns:
                r_n_s_times.append(t[0].datetime())
                r_n_s_labels.append(t[1])
            '''Step forward to the next day.'''
            observer.date += 1
            body.compute(observer)
     
        '''Convert to pandas timeseries with properly localized time index
        before saving the attribute.'''
        assert(len(r_n_s_labels) == len(r_n_s_times))
        RNS = pd.Series(r_n_s_labels, r_n_s_times)
        RNS.index = RNS.index.tz_localize('UTC')
        RNS.index = RNS.index.tz_convert(timezone)
        self.rise_noon_set = RNS
        
        '''BUILD THE heights TIMESERIES ATTRIBUTE'''
        alltimes = []
        allheights = []

        RNS.index = RNS.index.tz_convert('UTC') # back to UTC for calculations        
        allrises = RNS[RNS == 'rise']
        allsets = RNS[RNS == 'set']
                
        if allsets.index[0] < allrises.index[0]:
            '''Handle case of body already risen at begin time of the year.'''
            times, heights = fill_in_heights(begin, ephem.Date(allsets.index[0]),
                                             step, observer, name)
            alltimes.extend(times)
            allheights.extend(heights)
            allsets = allsets[1:]  # remove the first set time since unpaired
        
        if len(allrises) > len(allsets):
            allrises = allrises[:-1]  # remove the trailing rise time (unpaired)
            
        assert(len(allrises) == len(allsets))
        
        for rise_time, set_time in zip(allrises.index, allsets.index):
            rise_t = ephem.Date(rise_time)
            set_t = ephem.Date(set_time)
            times, heights = fill_in_heights(rise_t, set_t, step, observer, name)
            alltimes.extend(times)
            allheights.extend(heights)
        
        '''Convert to pandas timeseries with properly localized time index
        before saving the attribute.'''
        assert(len(allheights) == len(alltimes))
        HEI = pd.Series(allheights, alltimes)
        HEI.index = HEI.index.tz_localize('UTC')
        HEI.index = HEI.index.tz_convert(timezone)
        HEI = HEI[HEI >= 0] # get rid of any oddball slightly negative heights
        self.heights = HEI
     

if __name__ == "__main__":
    import doctest
    doctest.testmod()