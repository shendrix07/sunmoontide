# calendar
## Sun * Moon * Tide Calendar Maker

<a href="http://cruzviz.com/"><img src="https://github.com/cruzviz/calendar/blob/master/graphics/logo.png" align="center" height="48"></a>

### What is a Sun * Moon * Tide Calendar? What does the code do?

This code produces a PDF file containing a Sun * Moon * Tide calendar, designed to be easily printable on a home or office printer (ideally color printer) with 8.5x11" paper. An example 2015 calendar for Santa Cruz, California is available [here](@@@) (~@@30 MB PDF file), and here are generic html versions of the [About page](@@) and [Technical Details](@@). The only input required is an annual tide prediction file. These tide predictions are produced by the U.S. National Oceanic and Atmospheric Administration for American coastal areas, including territories and neighboring islands. There are over 3,000 NOAA tide prediction stations.

The program reads in all the high and low tides and interpolates them to produce sinusoidal curve data. It parses the input file header for the station ID, which it uses to look up necessary information like location coordinates and placename. (This is the `tides.py` module.) Then it calculates sun and moon positions relative to that location over the whole year. (The `astro.py` module.) It creates a pretty calendar showing tidal fluctuations and sun and moon movements for each day of the year. (The `cal_draw.py` module - almost completely done in matplotlib.) It generates the front and back matter that contains the input's placename and other location-specific information, and puts it all together in a printable PDF (@@@). It can take a few minutes to run, mainly waiting for matplotlib to crank out the monthly pages. The resulting PDF output file is about @@50 MB. Overall, it's about @@1,000 lines of code divided between 4 modules, stitched together by `__main__.py`.

----------------------

### Requirements:
- Python 3.4
- Non-standard-library Packages: matplotlib, numpy, pandas, PIL, pyephem, pyPDF2, pytz, WeasyPrint
 
----------------------

The main input for the Sun * Moon * Tide calendar maker is a NOAA Tide Prediction annual text file. The user of the calendar maker must manually download the NOAA Tide Prediction annual text file for the station and year for which s/he wants to make a calendar. The NOAA tide predictions website has both map and text search features so you can find the station nearest to your place of interest.
http://tidesandcurrents.noaa.gov/tide_predictions.html

Or just google “NOAA tide predictions”.

The NOAA predictions can be updated over time. It is good to download the input file just before making the calendar, to be sure you are working with the most current data.

To make the calendar look right, you will need to install 3 fonts on your system, and make sure matplotlib knows where to find them. These fonts are included with the package download.

-------------

### Step by step instructions:

1. Make sure you have Python 3.4 installed along with all the packages listed in Requirements@@@(setup file??? venv??). Unzip the package and make sure the following relative directory structure has been retained:
   ```
   calendar/
     __init__.py
     __main__.py
     astro.py
     cal_draw.py
     example_noaa_file.TXT
     fonts/
        moon_phases/
          LICENSE.TXT
          moon_phases.ttf
        foglihten/
          Foglihten-068.otf
          FoglihtenNo01.otf
          SIL Open Font License.txt
     graphics/
        Sun.png ??????
        logo.png
   @@@@@@@ cover art, annotated legend file
     LICENSE
     README.md
     station_info.csv
     tides.py
   ```

2. Install the 3 fonts filed under the `fonts` folder: Moon Phases, FoglihtenNo01, and regular Foglihten.
  * You should be able to just double-click on each \*.otf or \*.ttf file and it will show you how to install the font on your system.
  * Once the fonts are installed on your system, make sure that your matplotlibrc defaults know about these fonts. For example, in a matplotlibrc file:
    * add `Foglihten` to the serif font list
    * add `moon phases` and `FoglihtenNo01` to the fantasy font list
    * make sure those rows are uncommented (delete #)
  * You may also need to delete `fontList.cache` and any similar cache files from your `$HOME/.matplotlib` directory in order to force matplotlib to actually search out the new fonts. This directory is also where the `matplotlibrc` file may be placed if you wish to update your defaults permanently.
  * See http://matplotlib.org/users/customizing.html for details on using a matplotlibrc file.

   If you don't install the fonts properly, the code will still run, but it won't look as good. In particular, the moon phase icons will be characters in a default font instead of moon phases.

3. Following the tips above, find your local NOAA tide station on the NOAA website, and download the Annual TXT format of the published tide tables. It must be the TXT format, not PDF or XML. Make sure it is the *ANNUAL* tide tables and not the 2-day predictions.

2. Move the NOAA annual text file into the parent directory of the calendar directory. Rename the NOAA file to a filename that contains no spaces - I will call it `your_filename` here. It doesn’t need to have a file extension, though \*.txt can be handy if you want to click open the file to look at it yourself.

3. Open a terminal and `cd` into the aforementioned parent directory. You are in the right place if `ls` shows you a directory named `calendar` and a file called `your_filename` (or whatever you named it). Now tell python to run `calendar your_filename`:

   `$ python calendar your_filename`

   Or depending on your defaults:

   `$ python3 calendar your_filename`

4. Output will update you on the progress of the program. It can take a few minutes to run, mostly spend drawing the month pages in matplotlib.

--------
### If NOAA file format changes:

Procedures that will probably need revision are in the tides.py module. Search for `&**&` to find places that I believe will need to be updated if the NOAA annual tide prediction text file format changes significantly. Generally speaking, the input just needs to contain a time series of high/low tide magnitude predictions for the entire year. But the module also needs to somehow figure out the location coordinates, placename, timezone, and other station info.

---------
