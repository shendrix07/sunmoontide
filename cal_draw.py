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
import numpy as np

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

    pdf_out = PdfPages(file_name)

    for i in range(1,13): # for each month number
        this_month = tide_obj.year + "-" + "{:0>2}".format(i)
        monthfig = month_page(t[this_month], s[this_month], m[this_month],
                              t_min, t_max, place)
        print("Month " + str(i) + " figure created, now saving...")
        monthfig.savefig(pdf_out, format='pdf')
        print("Saved month " + str(i))
    
    pdf_out.close()
    
    
def month_page(month_of_tide, month_of_sun, month_of_moon, tide_min, tide_max,
               place_name):
    '''Takes monthly slices of all_tides, sun heights, and moon heights time
    series, as well as the tide's annual_min and annual_max and station_name,
    and returns a matplotlib.pyplot Figure object containing a month of the
    Sun * Moon * Tide calendar.
    '''
    # initialize figure
    fig = plt.figure(figsize=(8.5,11))
    
    # the zero lines for each variable to be plotted
    Tz = np.zeros(len(month_of_tide.index))
    Sz = np.zeros(len(month_of_sun.index))
    Mz = np.zeros(len(month_of_moon.index))
    
    year_month_prefix = month_of_tide.index[0].to_pydatetime().strftime('%Y-%m-')
    month_title = month_of_tide.index[0].to_pydatetime().strftime('%B')
    
    # ------------------- SNIP -------------------------
    def _plot_a_week(week_number, start_time, stop_time):
        '''Internal function. Works on pre-defined gridspec gs and assumes
        variables like tide_min, tide_max, month_of_tide/moon/sun already
        defined in outer scope.
        Week numbers start at 1 for the first week of the month and can go up
        to 6.'''
        
        if week_number == 1:
            gs_ind_1, gs_ind_2 = 0, 1
        elif week_number == 2:
            gs_ind_1, gs_ind_2 = 2, 3
        elif week_number == 3:
            gs_ind_1, gs_ind_2 = 4, 5
        elif week_number == 4:
            gs_ind_1, gs_ind_2 = 6, 7
        elif week_number == 5:
            gs_ind_1, gs_ind_2 = 8, 9
        elif week_number == 6:
            gs_ind_1, gs_ind_2 = 10, 11
        
        # sun and moon heights on top
        ax1 = plt.subplot(gs[gs_ind_1,0])
        ax1.fill_between(month_of_sun.index, month_of_sun, Sz,
                         color='#FFEB00', alpha=1)
        ax1.fill_between(month_of_moon.index, month_of_moon, Mz,
                         color='#D7A8A8', alpha=0.2)
        ax1.axis([start_time, stop_time, 0, 1])
        ax1.set_xticks([])
        ax1.set_yticks([])
        for axis in ['top','left','right']:
            ax1.spines[axis].set_linewidth(1.5)
        ax1.spines['bottom'].set_visible(False)
        
        # tide magnitudes below
        ax2 = plt.subplot(gs[gs_ind_2,0])
        ax2.fill_between(month_of_tide.index, month_of_tide, Tz,
                         color='#52ABB7', alpha=0.8)
        ax2.axis([start_time, stop_time, tide_min, tide_max])
        ax2.set_xticks([])
        ax2.set_yticks([])
        for axis in ['bottom','left','right']:
            ax2.spines[axis].set_linewidth(1.5)
        ax2.spines['top'].set_linewidth(0.5)
    
        
    gs = gridspec.GridSpec(8, 1, hspace=0.0)
    
    w1_first = year_month_prefix + '01 00:00'
    w1_last = year_month_prefix + '07 23:59'
    w2_first = year_month_prefix + '08 00:00'
    w2_last = year_month_prefix + '14 23:59'
    w3_first = year_month_prefix + '15 00:00'
    w3_last = year_month_prefix + '21 23:59'
    w4_first = year_month_prefix + '22 00:00'
    w4_last = year_month_prefix + '28 23:59'
    

    _plot_a_week(1, w1_first, w1_last)
    _plot_a_week(2, w2_first, w2_last)
    _plot_a_week(3, w3_first, w3_last)
    _plot_a_week(4, w4_first, w4_last)

    # ---------------------------------------------------
    fig.suptitle(month_title + ' in ' + place_name, fontsize='x-large',
                 fontname='Foglihten')
    return fig