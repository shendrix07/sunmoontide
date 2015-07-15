# -*- coding: utf-8 -*-
"""
Module for drawing most of a Sun * Moon * Tide calendar using matplotlib. Main
function is generate_annual_calendar. Various helper functions may also be
useful in other applications.
"""
import matplotlib
matplotlib.use('PDF')
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
plt.ioff()

import calendar
import numpy as np
import pandas as pd
from PIL import Image
import pkgutil
from PyPDF2 import PdfFileMerger, PdfFileReader
from io import BytesIO
import os

import cal_pages


def days_in_month(year_month_string):
    '''Generator that takes year_month_string (i.e. '2015-07') and yields
    all the days of the month in order, also as strings (i.e. '2015-07-18').
    '''
    start_date = pd.to_datetime(year_month_string)
    _, days_in_month = calendar.monthrange(start_date.year, start_date.month)
    end_date = start_date + pd.DateOffset(days_in_month)
    current_date = start_date
    while current_date < end_date:
        yield current_date.strftime('%Y-%m-%d')
        current_date = current_date + pd.DateOffset()


def months_in_year(year_string):
    '''Generator that takes year_string (i.e. '2015') and yields all the months
    of the year in order, also as strings (i.e. '2015-07').
    '''
    start_date = pd.to_datetime(year_string + '-01')    
    end_date = start_date + pd.DateOffset(months = 12)
    current_date = start_date
    while current_date < end_date:
        yield current_date.strftime('%Y-%m')
        current_date = current_date + pd.DateOffset(months = 1)


def generate_annual_calendar(tide_obj, sun_obj, moon_obj, file_name):
    '''Take tide, sun, and moon objects and generate a PDF file named
    `file_name`, which is a complete annual Sun * Moon * Tide calendar. File is
    saved to current working directory. Verbose output since this is a slow
    function.
    
    Args:
    tide_obj: tides.Tides object
    sun_obj: astro.Astro object for 'Sun'
    moon_obj: astro.Astro object for 'Moon'
    file_name: string. ".pdf" will NOT be appended to the file_name so the .pdf
                extension ought to be included in file_name.
    '''
    with PdfPages('temp.pdf') as pdf_out:
        coverfig = cover(tide_obj)
        coverfig.savefig(pdf_out, format='pdf')
        yearviewfig = yearview(tide_obj, sun_obj, moon_obj)
        yearviewfig.savefig(pdf_out, format='pdf')
        print('Calendar cover and year-at-a-glance complete.')

        for month in months_in_year(tide_obj.year):
            monthfig = month_page(month, tide_obj, sun_obj, moon_obj)
            print(month + " figure created, now saving...")
            monthfig.savefig(pdf_out, format='pdf')
            print("Saved " + month)

    d = {}
    d['/Title'] = 'Sun * Moon * Tide {} Calendar'.format(tide_obj.year)
    d['/Author'] = 'Sara Hendrix, CruzViz'
    d['/Subject'] = '{}, {}'.format(tide_obj.station_name, tide_obj.state)
    d['/CreationDate'] = pd.Timestamp.now().to_pydatetime().strftime('%c')
    
    print('Merging front and back matter into calendar... \
(ignore PdfReadWarnings)')    
    about_pdf = cal_pages.about(tide_obj.station_name)
    tech_pdf = cal_pages.tech(tide_obj)
    merger = PdfFileMerger(strict = False)    
    with open('temp.pdf','rb') as cal:
        merger.append(PdfFileReader(cal))
    with open(about_pdf,'rb') as about:
        merger.merge(1, PdfFileReader(about))
    with open(tech_pdf,'rb') as tech:
        merger.append(PdfFileReader(tech))
    merger.addMetadata(d)
    merger.write(file_name)
                
    print('Cleaning up temporary files...')
    os.remove('temp.pdf')
    os.remove(about_pdf)
    os.remove(tech_pdf)
    
    
def month_page(month_string, tide_o, sun_o, moon_o):
    '''Builds an 8.5x11" matplotlib Figure for a month page of the
    Sun * Moon * Tide calendar.
    
    Arguments:
        month_string: string of the month to be drawn, i.e. '2015-07'
        tide_o: tides.Tides object
        sun_o: astro.Astro object for 'Sun'
        moon_o: astro.Astro object for 'Moon'
    
    Returns:
        fig: matplotlib.pyplot Figure object, ready for writing to PDF.
    '''
    fig = plt.figure(figsize=(8.5,11))
    
    # some renaming of things for readability
    tide_min, tide_max = tide_o.annual_min, tide_o.annual_max
    place_name = tide_o.station_name + ", " + tide_o.state
    month_title = pd.to_datetime(month_string).strftime('%B')
    year_title = tide_o.year

#------------------ daily plot creator function -------------------
    def _plot_a_date(grid_index, date):
        '''Internal function. Works on pre-defined gridspec gs and assumes
        variables like tide_min, tide_max, month_of_tide/moon/sun already
        defined in outer scope.
        
        Plots the two daily subplots for `date` in gridspec coordinates
        gs[grid_index] for the sun/moon and gs[grid_index + 7] for tide.
        `date` must be a string in %Y-%m-%d format, i.e. '2015-07-18'.
        
        Returns ax1, ax2 = sun/moon (ax1) and tide (ax2) subplot handles
        '''
        day_of_sun = sun_o.altitudes[date]
        day_of_moon = moon_o.altitudes[date]
        day_of_tide = tide_o.all_tides[date]
        
        # convert indices to matplotlib-friendly datetime format
        Si = day_of_sun.index.to_pydatetime()
        Mi = day_of_moon.index.to_pydatetime()
        Ti = day_of_tide.index.to_pydatetime()
        
        # zeros for plotting the filled area under each curve
        Sz = np.zeros(len(Si))
        Mz = np.zeros(len(Mi))
        Tz = np.zeros(len(Ti))
        
        # x-limits based on first and last tide interp time - this handles edge
        # cases where only have one or two hi/lo tides per day and interps are
        # somewhat sparse - no more odd cut offs near borders
        start_time = matplotlib.dates.date2num(Ti[0])
        stop_time = matplotlib.dates.date2num(Ti[-1])
        
        # sun and moon heights on top
        ax1 = plt.subplot(gs[grid_index])
        ax1.fill_between(Si, np.sin(day_of_sun), Sz, color = '#FFEB00',
                         alpha = 0.25)  # the sunlight intensity
        ax1.fill_between(Si, day_of_sun / (np.pi / 2), Sz, color = '#FFEB00',
                         alpha = 1)  # the altitude angle
        ax1.fill_between(Mi, day_of_moon / (np.pi / 2), Mz, color = '#D7A8A8',
                         alpha = 0.25)
        ax1.set_xlim((start_time, stop_time))
        ax1.set_ylim((0, 1))
        ax1.set_xticks([])
        ax1.set_yticks([])
        for side in ['top', 'left', 'right']:
            ax1.spines[side].set_linewidth(1.5)
        ax1.spines['bottom'].set_visible(False)
        # add date number
        plt.text(0.05, 0.73, day_of_sun.index[0].day, ha = 'left',
                 fontsize = 12, fontname='Foglihten',
                 transform = ax1.transAxes)
        # add moon phase icon
        moon_icon = '0ABCDEFGHIJKLM@NOPQRSTUVWXYZ'  # the dark part
        plt.text(0.96, 0.69, moon_icon[moon_o.phase_day_num[date]],
                 ha = 'right', fontsize = 12, color = '0.75',
                 fontname = 'moon phases', transform = ax1.transAxes)
        plt.text(0.96, 0.69, '*',   # the white part
                 ha = 'right', fontsize = 12, color = '#D7A8A8', alpha = 0.25,
                 fontname = 'moon phases', transform = ax1.transAxes)
        
        # tide magnitudes below
        ax2 = plt.subplot(gs[grid_index + 7])
        ax2.fill_between(Ti, day_of_tide, Tz, color = '#52ABB7', alpha = 0.8)
        ax2.set_xlim((start_time, stop_time))
        tide_margin = (tide_max - tide_min) / 60  # prevent overlap with spines
        ax2.set_ylim((tide_min - 1.5 * tide_margin, tide_max + tide_margin))
        ax2.set_xticks([])
        ax2.set_yticks([])
        for side in ['bottom', 'left', 'right']:
            ax2.spines[side].set_linewidth(1.5)
        ax2.spines['top'].set_linewidth(0.5)
        ax2.set_zorder(1500)
        
        return ax1, ax2
    
# ---------------- build grid of daily plots ---------------------
    gs = gridspec.GridSpec(12, 7, wspace = 0.0, hspace = 0.0)
    daily_axes = [] # daily_axes[i] = sun/moon axes for date i+1

    # dayofweek --> Monday=0, Sunday=6. Our week starts on Sunday.
    init_day = (pd.to_datetime(month_string + '-01').dayofweek + 1) % 7
    gridnum = init_day  # start daily plots on correct day of week
    for day in days_in_month(month_string):
        ax, _ = _plot_a_date(gridnum, day)
        daily_axes.append(ax)
        if pd.to_datetime(day).dayofweek == 5: # if just plotted a Saturday
            gridnum += 8  # skip down a full row to leave tide subplots intact
        else:
            gridnum += 1

    # give us some better margins
    fig.subplots_adjust(left = 0.05, right = 0.95, bottom = 0.1, top = 0.8,
                        hspace = 0.0, wspace = 0.0)

    # add solstice or equinox icon, if needed this month
    sun_icon_col = {
        'spring equinox':   '#CCFFCC',
        'summer solstice':  '#FFFFA3',
        'fall equinox':     '#D56F28',
        'winter solstice':  '#B4EAF4'
    }
    monthnum = pd.to_datetime(month_string).month
    if monthnum in sun_o.events.index.month:
        solar_event = sun_o.events[monthnum == sun_o.events.index.month]
        xloc = matplotlib.dates.date2num(solar_event.index[0].to_pydatetime())
        sol_color = sun_icon_col[solar_event[0]]
        sol_ax = daily_axes[solar_event.index[0].day - 1]
        sol_ax.scatter(xloc, 0.25, s=400, marker = (16, 1, 0),
                       facecolor = sol_color, linewidth = 0.5,
                       edgecolor = 'black', zorder = 300, clip_on = False)
        sol_ax.set_zorder(1000)

        

    # add empty date boxes, figure annotations and titles
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
                 'Friday', 'Saturday']
    for i in range(init_day, 7):  # day-of-week labels on top row subplots
        plt.text(0.5, 1.08, day_names[i],
                 horizontalalignment = 'center',
                 fontsize = 12, fontname = 'Foglihten',
                 transform = daily_axes[i - init_day].transAxes)
    for i in range(init_day):  # handle the blank boxes on top row
        temp_ax = plt.subplot(gs[i])
        temp2_ax = plt.subplot(gs[i + 7])
        temp_ax.set_xticks([])
        temp_ax.set_yticks([])
        temp2_ax.set_xticks([])
        temp2_ax.set_yticks([])
        for side in ['left', 'right']:
            temp_ax.spines[side].set_linewidth(0.5)
            temp2_ax.spines[side].set_linewidth(0.5)
        if i == 0:
            temp_ax.spines['left'].set_linewidth(1.5)
            temp2_ax.spines['left'].set_linewidth(1.5)
        if i == (init_day - 1):
            temp_ax.spines['right'].set_linewidth(1.5)
            temp2_ax.spines['right'].set_linewidth(1.5)
        temp_ax.spines['bottom'].set_linewidth(0.0)
        temp2_ax.spines['top'].set_linewidth(0.0)
        temp_ax.spines['top'].set_linewidth(1.5)
        temp2_ax.spines['bottom'].set_linewidth(1.5)
        plt.text(0.5, 1.08, day_names[i],     # doy-of-week labels on blanks
                     horizontalalignment = 'center',
                     fontsize = 12, fontname = 'Foglihten',
                     transform = temp_ax.transAxes)

    # title and footer text
    fig.text(0.08, 0.875, month_title, horizontalalignment = 'left',
             fontsize = '72', fontname = 'Foglihten')
    fig.text(0.92, 0.875, year_title, horizontalalignment = 'right',
             fontsize = '72', fontname = 'Foglihten')
    fig.text(0.92, 0.1, place_name, horizontalalignment = 'right',
             fontsize = '16', fontname = 'Foglihten')
    fig.text(0.92, 0.13, 'Sun * Moon * Tide', horizontalalignment = 'right',
             fontsize = '36', fontname = 'FoglihtenNo01')
    # cruzviz logo on footer
    try:
        logo = pkgutil.get_data('cal_draw', 'graphics/logo.png')
        im = Image.open(BytesIO(logo))
        im = np.array(im).astype(np.float) / 255
        fig.figimage(im, xo = 505, yo = 70)
    except Exception as e:
        print('Could not load logo image. Error: ' + e)  # no exception raised
    
    return fig


def cover(tide):
    """Returns a matplotlib.pyplot Figure object, ready to write to PDF.
    """
    
    R = 2         # main circle radius
    a = 0.1       # sine amplitude
    n = 8         # number of bumps

    theta = np.linspace(0, 2 * np.pi, 500)

    x = (R + a * np.sin(n * theta)) * np.cos(theta)
    y = (R + a * np.sin(n * theta)) * np.sin(theta)

    entire_lunar_cycle = '0ABCDEFGHIJKLM@NOPQRSTUVWXYZ'  # the dark part
    moon_icon = 'TUWX0CDFGHJK@PQS'   # subset of moon icons to plot radially
    moontheta = np.linspace(0, 2 * np.pi, 17)[:-1]
    o = 0.3      # offset for moon icons to account for right alignment

    fig = plt.figure(figsize=(8.5,11))
    ax = plt.subplot(111)
    for frac in np.linspace(0, 1, 20):
        ax.plot(frac * x, frac * y, '-', c = '#52ABB7', lw = 5, alpha = 0.5)
    #ax.plot(4 * cos(theta), 4 * sin(theta), '--', c = 'red')  #placement check
    for daynum in range(16):
        th = moontheta[daynum]
        mx = 2 * R * np.cos(th) + o
        my = 2 * R * np.sin(th) - o
        # the dark part
        ax.text(mx, my, moon_icon[daynum], ha = 'right', fontsize = 12,
                color = '0.75', fontname = 'moon phases')
        # the white part
        ax.text(mx, my, '*', ha = 'right', fontsize = 12, 
                color = '#D7A8A8', alpha = 0.25, fontname = 'moon phases')
    # the sun
    ax.scatter(0, 14, s=100000, marker = (128, 1, 0),
                           facecolor = '#FFEB00', linewidth = 0.05,
                           edgecolor = '#FFEB00')

    ax.axis([-R * 5, R * 5, -R * 5, R * 5])
    ax.axis('off')
    
    fig.subplots_adjust(left = 1.75/8.5, right = 1 - (1.75/8.5),
                        bottom = 3.5/11, top = 8.5/11)

    fig.text(0.5, 0.8, 'Sun * Moon * Tide', horizontalalignment = 'center',
             fontsize = '68', fontname = 'FoglihtenNo01')
    fig.text(0.5, 0.32, '{}'.format(tide.year), 
             horizontalalignment = 'center', fontsize = '96',
             fontname = 'FoglihtenNo01')
    fig.text(0.5, 0.25, 'Calendar',
             horizontalalignment = 'center', fontsize = '48',
             fontname = 'FoglihtenNo01')
    fig.text(0.5, 0.15, '{}, {}'.format(tide.station_name, tide.state),
             horizontalalignment = 'center', fontsize = '24',
             fontname = 'Foglihten')
    return fig
    

def yearview(tide, sun, moon):
    """Returns a matplotlib.pyplot Figure object, ready to write to PDF.
    """
    fig = plt.figure(figsize=(8.5,11))
    fig.text(0.5, 0.875, '{} at a Glance'.format(tide.year),
             horizontalalignment = 'center', fontsize = '64',
             fontname = 'Foglihten')
    
    return fig
