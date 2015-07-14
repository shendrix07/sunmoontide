# -*- coding: utf-8 -*-
from tides import Tides
from astro import Astro
from cal_draw import generate_annual_calendar
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('filename',
                    help = 'Path to a NOAA annual tide prediction file.')
args = parser.parse_args()

if not os.path.isfile(args.filename):
    raise IOError('Cannot find {}'.format(args.filename))
print('Making Sun * Moon * Tide Calendar with input file \
{}.'.format(args.filename))

tides = Tides(args.filename)
print('{}, {}'.format(tides.station_name, tides.state))
sun = Astro(str(tides.latitude), str(tides.longitude),
            tides.timezone, tides.year, 'Sun')
print('Sun calculations complete.')
moon = Astro(str(tides.latitude), str(tides.longitude),
             tides.timezone, tides.year, 'Moon')
print('Moon calculations complete.')

print('Starting to draw calendar now.')
output_filename = 'SunMoonTide_{}_{}.pdf'.format(tides.year, tides.station_id)
generate_annual_calendar(tides, sun, moon, output_filename)
print('Calendar complete. Find output `{}` in the current working \
directory.'.format(output_filename))