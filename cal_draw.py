# -*- coding: utf-8 -*-
"""
Module for drawing a Sun * Moon * Tide calendar using matplotlib. Main
function is generate_annual_calendar. Various helper functions may also be
useful in other applications.
"""
import matplotlib
matplotlib.use('PDF')
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
plt.ioff()
from matplotlib.backends.backend_pdf import PdfPages

import calendar
import numpy as np
import pandas as pd


def days_in_month(year_month_string):
    '''Generator that takes year_month_string (i.e. '2015-07') and yields
    all the days of the month in order, also as strings (i.e. '2015-07-18').
    '''
    start_date = pd.to_datetime(year_month_string)
    _, days_in_month = calendar.monthrange(start_date.year, start_date.month)
    end_date = start_date + pd.DateOffset(days_in_month)
    current_date = start_date
    while current_date < end_date:
        yield current_date.to_pydatetime().strftime('%Y-%m-%d')
        current_date = current_date + pd.DateOffset()


def generate_annual_calendar(tide_obj, sun_obj, moon_obj, file_name):
    '''Take tide, sun, and moon objects and generate a PDF file named
    file_name, which is a complete annual Sun * Moon * Tide calendar. File is
    saved to current working directory. Verbose output since this is a slow
    function.
    
    Args:
    t: Tides object, s: Astro object (Sun), m: Astro object (Moon)
    file_name: string. ".pdf" will be appended to the file_name.
    '''
    t = tide_obj.all_tides
    s = sun_obj.heights
    m = moon_obj.heights
    t_min, t_max = tide_obj.annual_min, tide_obj.annual_max
    place = tide_obj.station_name + ", " + tide_obj.state
    tz = tide_obj.timezone

    pdf_out = PdfPages(file_name)

    for i in range(1,13): # for each month number
        this_month = tide_obj.year + "-" + "{:0>2}".format(i)
        monthfig = month_page(t[this_month], s[this_month], m[this_month],
                              t_min, t_max, place, tz)
        print("Month " + str(i) + " figure created, now saving...")
        monthfig.savefig(pdf_out, format='pdf')
        print("Saved month " + str(i))
    
    pdf_out.close()
    
    
def month_page(month_of_tide, month_of_sun, month_of_moon, tide_min, tide_max,
               place_name, time_zone):
    '''Takes monthly slices of all_tides, sun heights, and moon heights time
    series, as well as the tide's annual_min and annual_max and station_name,
    and returns a matplotlib.pyplot Figure object containing a month of the
    Sun * Moon * Tide calendar.
    '''
    # initialize figure
    fig = plt.figure(figsize=(8.5,11))
    
    year_month = month_of_tide.index[0].to_pydatetime().strftime('%Y-%m')
    month_title = month_of_tide.index[0].to_pydatetime().strftime('%B')
    year_title = month_of_tide.index[0].to_pydatetime().strftime('%Y')

    
    def _plot_a_date(grid_index, date):
        '''Internal function. Works on pre-defined gridspec gs and assumes
        variables like tide_min, tide_max, month_of_tide/moon/sun already
        defined in outer scope.
        Plots the two daily subplots for `date` in gridspec coordinates
        gs[gridx, gridy] for the sun/moon and gs[gridx, gridy + 1] for tide.
        `date` must be in a form pandas recognizes for datetime slicing.
        i.e. '2015-07-18'
        '''
        day_of_sun = month_of_sun[date]
        day_of_moon = month_of_moon[date]
        day_of_tide = month_of_tide[date]
        
        # convert indices to matplotlib-friendly datetime format
        Si = day_of_sun.index.to_pydatetime()
        Mi = day_of_moon.index.to_pydatetime()
        Ti = day_of_tide.index.to_pydatetime()
        
        # zeros for plotting the filled area under each curve
        Sz = np.zeros(len(Si))
        Mz = np.zeros(len(Mi))
        Tz = np.zeros(len(Ti))
        
        # x-limits from midnight to 11:59pm local time
        start_time = pd.to_datetime(date + ' 00:00').tz_localize(time_zone)
        start_time = matplotlib.dates.date2num(start_time.to_pydatetime())
        stop_time = pd.to_datetime(date + ' 23:59').tz_localize(time_zone)
        stop_time = matplotlib.dates.date2num(stop_time.to_pydatetime())
        
        # sun and moon heights on top
        ax1 = plt.subplot(gs[grid_index])
        ax1.fill_between(Si, day_of_sun, Sz, color='#FFEB00', alpha=1)
        ax1.fill_between(Mi, day_of_moon, Mz, color='#D7A8A8', alpha=0.2)
        ax1.set_xlim((start_time, stop_time))
        ax1.set_ylim((0, 1))
        ax1.set_xticks([])
        ax1.set_yticks([])
        for axis in ['top','left','right']:
            ax1.spines[axis].set_linewidth(1.5)
        ax1.spines['bottom'].set_visible(False)
        
        # tide magnitudes below
        ax2 = plt.subplot(gs[grid_index + 7])
        ax2.fill_between(Ti, day_of_tide, Tz, color='#52ABB7', alpha=0.8)
        ax2.set_xlim((start_time, stop_time))
        ax2.set_ylim((tide_min, tide_max))
        ax2.set_xticks([])
        ax2.set_yticks([])
        for axis in ['bottom','left','right']:
            ax2.spines[axis].set_linewidth(1.5)
        ax2.spines['top'].set_linewidth(0.5)
    
        
    gs = gridspec.GridSpec(12, 7, wspace = 0.0, hspace = 0.0)
    
    # call _plot_a_date in correct grid location
    gridnum = (pd.to_datetime(year_month + '-01').dayofweek + 1) % 6
    for day in days_in_month(year_month):
        _plot_a_date(gridnum, day)
        # dayofweek = The day of the week with Monday=0, Sunday=6
        if pd.to_datetime(day).dayofweek == 5: # if just plotted a Saturday
            gridnum += 8  # skip down a week to leave tide subplots intact
        else:
            gridnum += 1


    # add annotations and titles
    fig.suptitle(month_title + '   ' + year_title, size='72',
                 fontname='Foglihten')
    return fig