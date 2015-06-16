# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 11:03:04 2015

@author: sarahendrix
"""

""" RUN THIS CODE FIRST (in interactive prompt) - this does not have to be run
more than once, but the rest of this file is meant to be re-run frequently in
developing cal_draw functions.
------------
from astro import Astro
from tides import Tides

mytides = Tides('example_noaa_file.TXT')
sun = Astro(mytides.latitude, mytides.longitude, mytides.timezone, mytides.year, 'Sun')
moon = Astro(mytides.latitude, mytides.longitude, mytides.timezone, mytides.year, 'Moon')
--------------
"""
import matplotlib.pyplot as plt
import numpy as np

t = mytides.all_tides
t_jul = t['2015-07']
t_nov = t['2015-11']

Tzj = np.zeros(len(t_jul.index))
Tzn = np.zeros(len(t_nov.index))

m = mymoon.heights
s = mysun.heights

m_nov = m['2015-11']
m_jul = m['2015-07']
s_nov = s['2015-11']
s_jul = s['2015-07']

Mzj = np.zeros(len(m_jul.index))
Mzn = np.zeros(len(m_nov.index))
Szj = np.zeros(len(s_jul.index))
Szn = np.zeros(len(s_nov.index))

