# -*- coding: utf-8 -*-
"""
Module for drawing a Sun * Moon * Tide calendar using matplotlib. Main
function is generate_annual_calendar. Various helper functions may also be
useful in other applications.
"""
import matplotlib
matplotlib.use('PDF')
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
    # initialize figure and attach canvas to fig
    fig = plt.Figure()
    fig.set_canvas(plt.gcf().canvas)
    
    # the zero lines for each variable to be plotted
    Tz = np.zeros(len(month_of_tide.index))
    Sz = np.zeros(len(month_of_sun.index))
    Mz = np.zeros(len(month_of_moon.index))
    
    #take the first few days to begin
    year_month_prefix = month_of_tide.index[0].to_pydatetime().strftime('%Y-%m-')
    first_day = year_month_prefix + '15'
    last_day = year_month_prefix + '19'
    month_title = month_of_tide.index[0].to_pydatetime().strftime('%B')
    
    # ------------------- SNIP -------------------------
    # sun and moon heights on top
    ax1 = plt.subplot(211)
    plt.fill_between(month_of_sun.index, month_of_sun, Sz,
                     color='#FFEB00', alpha=1)
    plt.fill_between(month_of_moon.index, month_of_moon, Mz,
                     color='#D7A8A8', alpha=0.2)
    plt.title(month_title + ' 15-18 in ' + place_name)
    plt.axis([first_day, last_day, 0, 1])
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax1.get_yticklabels(), visible=False)
    
    # tide magnitudes below
    ax2 = plt.subplot(212)
    plt.fill_between(month_of_tide.index, month_of_tide, Tz,
                     color='#52ABB7', alpha=0.8)
    plt.axis([first_day, last_day, tide_min, tide_max])
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.setp(ax2.get_yticklabels(), visible=False)
    # ---------------------------------------------------

    return fig