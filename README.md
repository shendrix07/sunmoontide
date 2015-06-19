# calendar
## Sun * Moon * Tide Calendar Maker

<a href="http://cruzviz.com/"><img src="https://github.com/cruzviz/calendar/blob/master/graphics/logo_details.svg" align="left" height="48"></a>

----------------------

### Requirements:
- Python 3.4 (or higher)
- Non-standard-library Packages: matplotlib, numpy, pandas, PIL, pyephem, pytz
 
----------------------

The main input for the Sun * Moon * Tide calendar maker is a NOAA Tide Prediction annual text file. In addition to the tidal highs and lows used to create tidal fluctuation curves, this file includes the station information that is used to look up the local time zone and location coordinates for calculating sun and moon heights, as well as providing the calendar’s year and place name.

The user of the calendar maker must manually download the NOAA Tide Prediction annual text file for the station and year for which s/he wants to make a calendar. 
http://tidesandcurrents.noaa.gov/tide_predictions.html

Or just google “NOAA tide predictions”.

The NOAA predictions can be updated over time. It is good to download the input file just before making the calendar, to be sure you are working with the most current data.

In order for the calendar to look right, you will need to install 3 fonts on your system, and make sure matplotlib knows where to find them. The fonts are included with this package download.

-------------

### Step by step instructions:

1. Make sure you have Python 3.4+ installed properly, along with all the packages listed in Requirements. Unzip the package and make sure the following relative directory structure has been retained:
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

2. Install the 3 fonts filed under the `fonts` folder. Usually you can just double-click on the \*.otf or \*.ttf file and it will show you how to install it on your system. Once it is installed on your system, make sure that your matplotlibrc defaults know about these fonts. I recommend adding `Foglihten` to the serif font list, and `moon phase` and `FoglihtenNo01` to the fantasy font list. You may also need to delete `fontList.cache` and any similar cache files from your `$HOME/.matplotlib` directory so that matplotlib has to actually look for the new fonts. This directory is also where a `matplotlibrc` file may be placed if you wish to update your defaults permanently. See http://matplotlib.org/users/customizing.html for details on using matplotlibrc.

   If you don't do this part, the code will still run, but it won't look as good. In particular, the moon phase icons will be junky looking letters instead of moon phases.


3. Following the tips above, find your local NOAA tide station on the NOAA website, and download the Annual TXT format of the published tide tables. It must be the TXT format, not PDF or XML. Make sure it is the *ANNUAL* tide tables and not the 2-day predictions.

2. Move the NOAA annual text file into the parent directory of the calendar directory. Rename the NOAA file to a filename that contains no spaces - I will call it `your_filename` here. It doesn’t need to have a file extension, though \*.txt can be handy if you want to click open the file to look at it yourself.

3. Open a terminal and `cd` into the aforementioned parent directory. You are in the right place if `ls` shows you a directory named `calendar` and a file called `your_filename` (or whatever you named it). Now tell python to run `calendar your_filename`:

   `$ python calendar your_filename`

   Or if you usually work in python 2, your defaults probably require:

   `$ python3 calendar your_filename`

4. Output will update you on the progress of the program. It can take a few minutes to run, most time being taken in drawing the PDF.

--------
### If NOAA file format changes:

Procedures that will probably need revision are in the tides.py module. Search for `&**&` to find places that I believe will need to be updated if the NOAA annual tide prediction text file format changes significantly. Generally speaking, the input just needs to contain a time series of high/low tide magnitude predictions for the entire year.

---------
