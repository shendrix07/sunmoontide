# -*- coding: utf-8 -*-
from tide import Tides
from astro import Astro
#?? Graphics module import
import argparse
import os
import pickle

parser = argparse.ArgumentParser()
parser.add_argument('input_filename', type=argparse.FileType('r'))
args = parser.parse_args()

assert(os.path.exists(args.input_filename))
print('Making Sun*Moon*Tides Calendar with ' +
        'input file {}'.format(args.input_filename))
tides = Tides(args.input_filename)

sun = Astro(tides.latitude, tides.longitude, tides.timezone, tides.year, 'sun')
moon = Astro(tides.latitude, tides.longitude, tides.timezone, tides.year, 'moon')

# pickle sun, moon, tides
with open('sun_moon_tide_data.pickle', 'wb') as f:
    pickle.dump([sun, moon, tides], f, pickle.HIGHEST_PROTOCOL)
print('Computations complete, pickled in @@@wherever.')

print('Starting to draw calendar now.')
# Call graphics stuff to make the output
# @@@@@@@
#
#
print("Calendar complete. Find output in new folder, @@@@")