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

fig = plt.Figure()
fig.set_canvas(plt.gcf().canvas)

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

ax1 = plt.subplot(211)

plt.fill_between(s_jul.index, s_jul, Szj, color='#FFEB00', alpha=1)
plt.fill_between(m_jul.index, m_jul, Mzj, color='#D7A8A8', alpha=0.2)
plt.axis(['2015-07-17', '2015-07-19', 0, 1])
plt.title('July in Santa Cruz')
plt.ylabel('Height in Sky')
plt.setp(ax1.get_xticklabels(), visible=False)

ax2 = plt.subplot(212)
plt.fill_between(t_jul.index, t_jul, Tzj, color='#45B1C4', alpha=0.9)
plt.axis(['2015-07-17', '2015-07-19', mytides.annual_min, mytides.annual_max])
plt.ylabel('Tides')
plt.setp(ax2.get_xticklabels(), visible=False)

fig.savefig("foo3" + ".pdf", format='pdf')