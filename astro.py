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

def round_datetime(dt):
   """Round a datetime object to the closest minute.
   Argument: dt - a datetime.datetime object.
   Returns another datetime.datetime object.
   """
   s = dt.second
   m = dt.microsecond
   if s < 30:
       return dt + datetime.timedelta(0, -s, -m)
   else:
       return dt + datetime.timedelta(0, 60 - s, -m)


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
    # make no assumptions about timezone offsets, even for similar day of year
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


def fill_in_heights(start, stop, step, observe, body_name, append_NaN = True):
    """Return sequential lists of times and heights between start and stop
    times, at given time step, for an astronomical body's altitude over time.
    
    Arguments:
        start (ephem.Date): the initial time (included in the result)
        stop (ephem.Date): the final time (included in the result)
        step (float): a step size in days (i.e. 15 minutes - `15 * ephem.minute`)
        observe (ephem.Observer): pre-initialized ephem.Observer() object
            with location information set; it will be copied to prevent
            alteration of the original observer object
        body_name (str): a title-case ephem body name, i.e. 'Sun' or 'Moon'
        
    Optional:
        append_NaN (Boolean, default = True): if True, append a NaN value to
            the end of the result, to provide breaks between plotted line
            segments.
    
    Returns:
        times, heights
        times: a list of sequential timezone-naive datetime.datetimes (in UTC)
        heights: a list of floats, providing sin(altitude) of the body at
            each time
        len(times) == len(heights)
        
    Example:
    >>> cruz = ephem.Observer()
    >>> cruz.lat, cruz.lon = '36.97', '-122.02'
    >>> time1 = ephem.Date('2015-05-15 19:00')   # local noon
    >>> time2 = time1 + ephem.hour
    >>> ti, he = fill_in_heights(time1, time2, 15 * ephem.minute, cruz, 'Sun')
    >>> for t,h in zip(ti, he):
    ...     print('{0} ... {1:7.3f}'.format(
    ...                    round_datetime(t).strftime('%Y-%m-%d %H:%M'), h))
    ... 
    2015-05-15 19:00 ...   0.921
    2015-05-15 19:15 ...   0.933
    2015-05-15 19:30 ...   0.942
    2015-05-15 19:45 ...   0.948
    2015-05-15 20:00 ...   0.951
    2015-05-15 20:00 ...     nan
    """
    times = []
    heights = []
    obs = copy_ephem_observer(observe)
    obs.date = start
    body = eval('ephem.' + body_name + '(obs)')
    
    while round(obs.date, 6) < round(stop, 6):
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
        times.append(ephem.Date(obs.date + step/100).datetime())
        heights.append(float('NaN'))
    
    assert(len(times) == len(heights))        
    return times, heights
    
    
def get_lunation_day(today, number_of_phase_ids=28):
    '''Given a date (of type ephem.Date), return a lunar cycle day ID number
    (integer in [0:(number_of_phase_ids - 1)]), corresponding to the lunation
    for the given date. 0 = new moon.
    
    Arguments:
        today (ephem.date): the date for which to get the lunation day number

    Optional:
        number_of_phase_ids (integer, default = 28): the number of unique
            lunar cycle day identifiers, e.g. the number of moon phase icons
            available to display the lunation each day.
            
    Returns:
        integer in range(0, number_of_phase_ids - 1), today's lunation phase
            ID number.
    
    The lunation day is calibrated to the quarter phases
    calculated by pyephem, but it does not always agree exactly with
    percent illumination, which is a different calculation entirely.'''
    last_new = ephem.previous_new_moon(today)
    next_new = ephem.next_new_moon(today)
    num = number_of_phase_ids - 1
    first_approx = round((today - last_new) / (next_new - last_new) * num)
    if first_approx < np.ceil(num / 4):
        next_fq = ephem.next_first_quarter_moon(last_new)
        if today < next_fq:
            return round((today - last_new) / (next_fq - last_new)
                        * (num / 4))
    if first_approx < np.ceil(num / 2):
        next_full = ephem.next_full_moon(last_new)
        if today < next_full:
            return round((today - last_new) / (next_full - last_new)
                        * (num / 2))
    if first_approx < np.ceil(num * 3 / 4):
        next_lq = ephem.next_last_quarter_moon(last_new)
        if today < next_lq:
            return round((today - last_new) / (next_lq - last_new)
                        * (num * 3 / 4))
    return first_approx



class Astro:
    """A class with year- and location-specific rise, set, and altitude for an
    astronomical body. Sun and Moon have additional special information.
    Purpose is to calculate and then store the various input required to graph
    sun, moon, or other astronomical body for a Sun * Moon * Tide calendar.
    """
    def __init__(self, latitude: str, longitude: str, timezone: str, year: str,
                 name: str):
        """Take the all necessary location/year/body name information and
        construct plot-ready astronomical body time series for calendar.
        Attributes are all set and ready for queries/plotting after __init__.
        
        Arguments:
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
        step = 10 * ephem.minute #resolution of full timeseries of body heights
        
        alltimes, allheights = fill_in_heights(begin, end, step,
                                             observer, name, append_NaN=False)        
        '''Convert to pandas timeseries and localize the time index.'''
        assert(len(allheights) == len(alltimes))
        hei = pd.Series(allheights, alltimes)
        hei.index = hei.index.tz_localize('UTC')
        hei.index = hei.index.tz_convert(timezone)
        self.heights = hei

# ----------------- Special attributes for Sun and Moon ----------------

        '''Equinox and solstice events for Sun'''
        if name == 'Sun':
            spring = ephem.next_spring_equinox(year)
            summer = ephem.next_summer_solstice(year)
            fall = ephem.next_fall_equinox(year)
            winter = ephem.next_winter_solstice(year)
            event_times = [spring.datetime(), summer.datetime(), 
                           fall.datetime(), winter.datetime()]
            event_names = ['spring equinox', 'summer solstice', 'fall equinox',
                           'winter solstice']
            events = pd.Series(event_names, event_times)
            events.index = events.index.tz_localize('UTC')
            events.index = events.index.tz_convert(timezone)
            self.events = events

        '''Daily phase (% illuminated, 28-day icon ID) for Moon'''
        if name == 'Moon':
            moon = ephem.Moon()
            illuminated = []
            observer.date = begin + 22 * ephem.hour  # 10 pm local time Jan 1
            moon.compute(observer)
            while observer.date < end:
                illuminated.append(moon.moon_phase)
                observer.date += 1
                moon.compute(observer)
            daily_times = pd.date_range(year + '-01-01', year + '-12-31', 
                                      tz = timezone)
            assert(len(illuminated) == len(daily_times))
            self.percent_illuminated = pd.Series(illuminated, daily_times)
            
            cycle_days = []            
            moon_day = begin + 22 * ephem.hour   # 10 pm local time Jan 1
            while moon_day < end:
                    cycle_days.append(get_lunation_day(moon_day))
                    moon_day += 1
            assert(len(cycle_days) == len(daily_times))
            self.phase_day_num = pd.Series(cycle_days, daily_times)



if __name__ == "__main__":
    import doctest
    doctest.testmod()