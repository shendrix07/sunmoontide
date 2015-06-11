# calendar
## Sun * Moon * Tide Calendar Maker

### Requirements:
- Python 3.4
- Packages: numpy, pandas, pyephem, matplotlib, pytz
 
----------------------

The main input for the Sun * Moon * Tide calendar maker is a NOAA Tide Prediction annual text file. In addition to the tidal highs and lows used to create tidal fluctuation curves, this file includes all the location information that is used to calculate sun and moon data, as well as details like the calendar’s year and place name.

The user of the calendar maker must manually download the NOAA Tide Prediction annual text file for the station and year for which s/he wants to make a calendar. 
http://tidesandcurrents.noaa.gov/tide_predictions.html
Or just google “NOAA tide predictions”.

The NOAA predictions can be updated over time. It is good to download the input file just before running the calendar maker, to be sure you are working with the most current data.

-------------

### Step by step instructions:

0. Make sure you have the correct version of python installed properly, along with all the packages listed in Requirements.

1. Following the links/tips above, find your NOAA tide station of interest, and download the Annual TXT format of the published tide tables. It must be the TXT format, not PDF or XML. Make sure it is the *ANNUAL* tide tables and not the 2-day predictions.

2. Move the file into the directory where the unzipped package (a folder named "calendar") is located. Rename the NOAA input file to a filename that contains no spaces. It doesn’t need to have a file extension, though .txt can be handy if you want to open it up easily to look at it yourself.

3. Open a terminal and cd into the aforementioned directory. You are in the right place if `ls` shows you a directory named `calendar` and a file called your_filename (whatever you named it). Now run calendar your_filename (either `python calendar <NOAA_input_filename` or `python3 calendar <NOAA_input_filename>` depending on your defaults).

--------
### If NOAA file format changes:

Procedures that will probably need revision are in the tides.py module. Search for `&**&` to find places that I believe will need to be updated if the NOAA annual tide prediction text file format changes significantly. Generally speaking, the input just needs to contain a time series of high/low tide magnitude predictions for the entire year.

---------
