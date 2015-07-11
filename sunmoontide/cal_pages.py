# -*- coding: utf-8 -*-
"""
Module to make the About and Technical Details for the calendar. For use in
generate_annual_calendar function inside module cal_draw.py. These are the
pages that require more advanced text layout and formatting, so using HTML
templates and WeasyPrint instead of matplotlib.
"""
from io import BytesIO
import pkgutil
from string import Template
import weasyprint


def about(st_name):
    """Returns a pdf filename for the About page.
    """
    try:
        abouthtml = pkgutil.get_data('cal_pages', 'infopages/about.html')
    except Exception as e:
        print('Could not find the HTML template for the About the Calendar \
page. Expected: sunmoontide/infopages/about.html')
        raise IOError(e)

    def _my_fetcher(url): # locate svg/png image files in sunmoontide/graphics/
        if url.startswith('graph:') and url.endswith('png'):
            try:
                grb = pkgutil.get_data('cal_pages', 'graphics/{}'.format(url[6:]))
            except Exception as e:
                print('Could not find a graphic for the About the Calendar \
page. Expected: sunmoontide/graphics/{}'.format(url[6:]))
                raise IOError(e)
            return dict(string = BytesIO(grb).read(), mime_type = 'image/png')
        elif url.startswith('graph:') and url.endswith('svg'):
            try:
                grb = pkgutil.get_data('cal_pages', 'graphics/{}'.format(url[6:]))
            except Exception as e:
                print('Could not find a graphic for the About the Calendar \
page. Expected: sunmoontide/graphics/{}'.format(url[6:]))
                raise IOError(e)
            return dict(string = BytesIO(grb).read(),
                        mime_type = 'image/svg+xml')
        else:
            return weasyprint.default_url_fetcher(url)
    #html source: '<img src="graph:nameofimage.svg">'  <-- must be svg or png

    abouttemplate = Template(BytesIO(abouthtml).read().decode('utf-8'))
    abouthtml = abouttemplate.substitute(st_name = st_name)
    weasyprint.HTML(string = abouthtml,
         url_fetcher = _my_fetcher).write_pdf('about_tmp.pdf')
    return 'about_tmp.pdf'


def tech(tide):
    """Returns a pdf filename for the Technical Details section.
    """
    if tide.station_type == 'Subordinate':
        optstring = 'The predictions are referenced to {0.ref_station_name} \
(station ID: {0.ref_station_id}). High and low tide heights are \
{0.height_offset_high}% and {0.height_offset_low}% of the reference station \
high and low tide heights, respectively. Times are offset from the reference \
station high and low times by {0.time_offset_high} and {0.time_offset_low} \
minutes, respectively.</p>'.format(tide)
    else:
        optstring = '</p>'
    
    try:
        techhtml = pkgutil.get_data('cal_pages', 'infopages/tech.html')
    except Exception as e:
        print('Could not find the HTML template for the Technical Details \
section. Expected: sunmoontide/infopages/tech.html')
        raise IOError(e)

    argdict = { 'station_name': tide.station_name,
                'station_type': tide.station_type,
                'station_id'  : tide.station_id,
                'timezone'    : tide.timezone,
                'opt_string'   : optstring
    }

    techtemplate = Template(BytesIO(techhtml).read().decode('utf-8'))
    techhtml = techtemplate.substitute(argdict)
    weasyprint.HTML(string = techhtml).write_pdf('tech_tmp.pdf')
    return 'tech_tmp.pdf'