# sunmoontide
## Sun * Moon * Tide Calendar Maker

<a href="http://cruzviz.com/"><img src="https://github.com/cruzviz/sunmoontide/blob/master/sunmoontide/graphics/logo.png" align="center" height="48"></a>

### What is a Sun * Moon * Tide calendar? What does the code do?

This code produces a PDF file containing a Sun * Moon * Tide calendar, designed to be easily printable on a home or office printer (ideally color printer) with 8.5x11" paper. An example 2015 calendar for Santa Cruz, California is available [here](https://github.com/cruzviz/sunmoontide/blob/master/SampleCalendar.pdf) (~11 MB PDF file). The only external input required is a text file of published annual tide tables. These files are provided by the U.S. National Oceanic and Atmospheric Administration (NOAA) for American coastal areas, including territories and neighboring islands. There are over 3,000 NOAA tide prediction stations.

The program reads in all the high and low tides and interpolates them to produce sinusoidal curve data. It parses the input file header for the station ID, which is used to grab required information like location coordinates, time zone, and placename from a lookup file. (This is the `tides.py` module.) Then it calculates sun and moon positions relative to that location over the whole year, plus daily moon phases and solar equinoxes/solstices. (The `astro.py` module.) It creates a pretty calendar showing tidal fluctuations and sun and moon movements for each day of the year. (The `cal_draw.py` module - almost completely done in matplotlib.) It generates the front and back matter that contains the input's placename and other location-specific information, and puts it all together in a printable PDF (`cal_draw.py` for final PDF production and `cal_pages.py` for printing front and back matter from HTML templates). It can take a few minutes to run, mainly waiting for matplotlib to crank out the plots. The resulting PDF output file is about 15 to 20 MB. Overall, it's around 1,200 lines of code divided between 4 modules, stitched together into a package by `__init__.py` and `__main__.py`.

----------------------

### Requirements:
- Python 3.4.3
- Non-standard-library packages: ephem, matplotlib, numpy, pandas, pillow, pypdf2, pytz, weasyprint
- See requirements.txt and/or environment.yml for all dependencies
 
----------------------

The input for the Sun * Moon * Tide calendar maker is a NOAA Tide Prediction annual text file. The user of the calendar maker must manually download the NOAA Tide Prediction annual text file for the station and year for which s/he wants to make a calendar. The NOAA tide predictions website has both map and text search features so you can find the station nearest to your place of interest.
http://tidesandcurrents.noaa.gov/tide_predictions.html

To make the calendar look right, you will need to install a few fonts on your system. These fonts are included with the package download.

-------------

### Step by step instructions:

1. Download ("Download ZIP" button in sidebar) the package to your preferred location, unzip it, and check that the following relative directory structure has been retained:
   ```
   environment.yml
   example_noaa_file.TXT   
   LICENSE
   matplotlibrc
   README.md
   requirements.txt
   Sample_Calendar.pdf
   sunmoontide/
     __init__.py
     __main__.py
     astro.py
     cal_draw.py
     cal_pages.py
     fonts/
       alegreya/
         Alegreya-Regular.otf
         AlegreyaSC-Regular.otf
         SIL Open Font License.txt
       foglihten/
         FoglihtenNo01.otf
         SIL Open Font License.txt
       moon_phases/
         LICENSE.TXT
         moon_phases.ttf
   graphics/
       legend.svg
       logo.png
   infopages/
       about.html
       tech.html
   station_info.csv
   tides.py
   ```

1. Make sure you have Python 3.4 installed along with all the packages listed in Requirements. It is wise to do so in a virtual environment of some kind. Options include:
  * Use Anaconda distribution/conda and the environment.yml file to create a new environment and activate it. See http://conda.pydata.org/docs/using/envs.html - scroll down to "Use environment from file". Syntax varies by operating system.
  * Create and activate a new Python 3.4 virtual environment using any tool you prefer. Make sure you have pip installed in the environment, and then run the requirements.txt file to install everything needed to run the Sun * Moon * Tide calendar maker. `pip install -r requirements.txt`
  * If you work in Python 3.4 or are installing Python 3 for the first time, and you don't mind having these specific package versions installed on your main environment, you can also run `pip install -r requirements.txt` directly, but this is not preferred because of the potential for version conflicts.

2. Install the 3 fonts filed under the `sunmoontide/fonts` folder: Moon Phases, FoglihtenNo01, and Alegreya (both regular and SC - small caps).
  * Read the Licenses, especially for the moon phase font. This font is copyrighted by Curtis Clark and he specifies certain restrictions on its use. The other fonts are under SIL Open Font licenses.
  * You should be able to just double-click on each \*.otf or \*.ttf file and it will show you how to install the font on your system.
  * Keeping the matplotlibrc file where it is, in the root directory (the working directory where you run the program), should allow matplotlib to find the fonts properly.

   If you don't install the fonts to your system, the code will still run, but the calendar won't look right. In particular, the moon phase icons will be characters in a default font instead of moon phases.

3. Visit the NOAA Tide Predictions website, find your NOAA tide station, and download the Annual TXT published tide tables. It must be the TXT format, not PDF or XML; and it must be the annual tide tables, not the 2-day predictions. (Ctrl-F to find "published" may help.)

2. Move the NOAA annual text file into the root directory of the package. Rename the NOAA file to a filename that contains no spaces - I will call it `your_filename` here. It doesn’t need to have a file extension, though \*.txt can be handy if you want to easily click open the file and look at it yourself.

3. With your virtual environment activated, get a terminal/command prompt in the package root directory. You are in the right place if `ls` shows you a directory named `sunmoontide` and a file called `your_filename` (or whatever you named it), plus a few other files like `README.md` and `matplotlibrc`. Now tell python to run `sunmoontide your_filename`:

   `$ python sunmoontide your_filename`

4. Output will update you on the progress of the program. It can take a few minutes to run, mostly spend drawing the plot-heavy pages in matplotlib. When complete, your PDF calendar will appear in the current working directory. It will be named `SunMoonTide_{year}_{NOAA station ID}.pdf`.

--------
### Adapting to other input file formats:

Procedures that will need revision are in the `tides.py` module. Search for `&**&` to find places that will need to be updated (or at least carefully checked) if the NOAA annual tide prediction text file format changes, or in order to adapt the code to handle other file formats for tide predictions, e.g. another country's. Generally speaking, the input file just needs to contain a time series of high/low tide magnitude predictions for the entire year. But the `tides.py` module also needs to somehow figure out:
  * the station's time zone - required for tides to be interpolated properly, and then for everything to be presented in local time
  * the station's location coordinates (latitude/longitude) - required for calculating sun and moon altitudes
  * placename (station name and state) - for various text annotations
  * other station info for the Technical Details section - Technical Details may also need revision to maintain accuracy - see `infopages/tech.html` and the `cal_pages.py` module

Currently, some station information variables are set by parsing them from the header of the input file, but many essential ones (including location coordinates and timezone) are not available in NOAA annual tide tables files, so they are looked up in `station_info.csv`. This lookup file was created by web scraping the NOAA Tide Predictions site for location coordinates, and geocoding those coordinates to determine tzinfo/IANA time zones for each station.

---------
