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
        latitude = latitude in decimal degrees as a string, i.e. '-122.0402'
        longitude = longitude in decimal degrees as a string, i.e. '36.9577'
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
        
        begin, end = utc_year_bounds(timezone, year) #both have type ephem.Date
        step = (15 / 60) / 24  #15 minute step, in days, for ephem.Date math
        
        now = begin
        # observer's time position is set to the very beginning of the year
        observer.date = now
        body = eval('ephem.' + name + '()')
        risesettimes = []
        riseorset = []
        alltimes = []
        allheights = []
        if name == 'Sun':  # set horizon for civil twilight
            observer.horizon = '-6'
        
        '''If the body is already above the horizon at the first datetime of
        the year, we need to step through time and calculate all the altitude
        heights until after the first setting. Our loop for the main altitude
        calculations starts with the next rising event.
        '''
        initial_height = eval('np.sin(ephem.' + name + '(observer).alt)')
        if initial_height >= 0:
            next_set_time = observer.next_setting(body)
            if name == 'Sun': # civil twilight
                next_set_time = observer.next_setting(body, use_center=True)
            risesettimes.append(next_set_time.datetime())
            riseorset.append('set')
            while now <= next_set_time:
                height_now = eval('np.sin(ephem.' + name + '(observer).alt)')
                alltimes.append(now.datetime())
                allheights.append(height_now)
                now = ephem.Date(now + step)
                observer.date = now # observer moves forward one time step
            
            now = next_set_time
            observer.date = now  # observer moves to exact setting time
            height_now = eval('np.sin(ephem.' + name + '(observer).alt)')
            alltimes.append(now.datetime())
            allheights.append(height_now)
                    
            # append NaN so that plots will not draw line between set and rise
            alltimes.append(ephem.Date(now + 0.00001).datetime())
            allheights.append(float('NaN'))
                
        ''' MAIN ASTRO ALTITUDE CALCULATIONS LOOP
        Now we are ready to start at the first body rising event of the year.
        This loop exits after it has gone past the end of the year.
        FOR SUN: Rises and sets are computed with use_center flag set True and
        observer horizon = -6, to use civil dawn and dusk as rise and set.

        Outline of this loop body:
            - compute the next time the body rises, save in rise-set lists
            - move observer forward in time to body rise time
            - computer the next time the body sets, save in rise-set lists
            - step observer through from rise time to set time,
                calculating height of the body at each time step,
                saving in alltimes/allheights lists
            - repeat until observer has gone past the end of the year
        
        NaN (not a number) values are appended just after each setting time,
        so that plotted curves will break between each setting and next rising.
        Otherwise we would have ugly flat lines in between.
        '''
        print(observer)
        print(body)
        while now <= end:
            next_rise_time = observer.next_rising(body)
    ##@@@@@@@@@@@ BUGS.
            '''
            <ephem.Observer date='2016/1/1 08:00:00'>
ephem.NeverUpError: 'Sun' transits below the horizon at 2016/1/1 09:35:26
ephem.AlwaysUpError: 'Moon' is still above the horizon at 2016/1/1 15:05:52
            '''
            if name == 'Sun': # civil twilight
                next_rise_time = observer.next_rising(body, use_center=True)
            risesettimes.append(next_rise_time.datetime())
            riseorset.append('rise')
            now = next_rise_time
            observer.date = now  # observer moves forward in time to next rise
            next_set_time = observer.next_setting(body)
            if name == 'Sun': # civil twilight
                next_set_time = observer.next_setting(body, use_center=True)
            risesettimes.append(next_set_time.datetime())
            riseorset.append('set')
            
            # Loop to append all times/height between this rise and set
            while now <= next_set_time:
                height_now = eval('np.sin(ephem.' + name + '(observer).alt)')
                alltimes.append(now.datetime())
                allheights.append(height_now)
                now = ephem.Date(now + step)
                observer.date = now  # observer moves forward one time step
            
            # now we are slightly past the current setting time...
            # go back to the exact setting time and append its info
            now = next_set_time
            observer.date = now  # observer moves to exact setting time
            height_now = eval('np.sin(ephem.' + name + '(observer).alt)')
            alltimes.append(now.datetime())
            allheights.append(height_now)
            
            # append NaNs so that plots will not draw line between set and rise
            alltimes.append(ephem.Date(now + 0.000001).datetime())
            allheights.append(float('NaN'))

        '''Now we need to convert our lists with datetimes into a
        pandas timeseries. pandas.Series(values,times). Then save as attributes.
        We can't naively pass the ephem.Date objects into pandas index, it will
        save them as Float64Index. We also need to localize back to local timezone.
        '''
        assert(len(riseorset) == len(risesettimes))
        assert(len(allheights) == len(alltimes))
        self.rises_sets = pd.Series(riseorset, risesettimes)
        self.rises_sets.index = self.rises_sets.index.tz_convert(self.timezone)
        self.heights = pd.Series(allheights, alltimes)
        self.heights.index = self.heights.index.tz_convert(self.timezone)


if __name__ == "__main__":
    import doctest
    doctest.testmod()