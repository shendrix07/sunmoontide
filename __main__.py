# -*- coding: utf-8 -*-
from tides import Tides
from astro import Astro
#?? Graphics module import
import argparse
import os
#import pickle

parser = argparse.ArgumentParser()
parser.add_argument('filename',
                    help = 'Path to a NOAA annual tide prediction file.')
args = parser.parse_args()

if not os.path.isfile(args.filename):
    raise IOError('Cannot find ' + args.filename)
print('Making Sun * Moon * Tides Calendar with ' +
        'input file ' + args.filename)

tides = Tides(args.filename)
print(tides.station_name + ', ' + tides.state)
sun = Astro(tides.latitude, tides.longitude, tides.timezone, tides.year, 'Sun')
print('Sun calculations complete')
moon = Astro(tides.latitude, tides.longitude, tides.timezone, tides.year, 'Moon')
print('Moon calculations complete')

# pickle sun, moon, tides
#with open('sun_moon_tide_data.pickle', 'wb') as f:
#    pickle.dump([sun, moon, tides], f, pickle.HIGHEST_PROTOCOL)
#print('Computations complete, pickled in @@@wherever.')

print('@@@Starting to draw calendar now.')
# Call graphics stuff to make the output
# @@@@@@@
#
#
print('Calendar complete. Find output in new folder, @@@@')