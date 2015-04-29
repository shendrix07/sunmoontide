# calendar
## Sun * Moon * Tide Calendar Maker

### Requirements:
- Python 3.4
- Packages: Numpy, pandas, pyephem, etc etc etc etc????
 
----------------------

The main input for the Sun * Moon * Tide calendar maker is a NOAA Tide Prediction annual text file. In addition to the tidal highs and lows used to create tidal fluctuation curves, this file includes all the location information that is used to calculate sun and moon data, as well as details like the calendar’s year and place name.

Rather than tie the code too closely to the URLs that worked at the time the calendar maker was first written, or redo the station search capabilities of the NOAA website, the user of the calendar maker must manually download the NOAA Tide Prediction annual text file for the station and year for which s/he wants to make a calendar. 
http://tidesandcurrents.noaa.gov/tide_predictions.html
Or just google “NOAA tide predictions”.

The NOAA predictions can be updated over time. It is good to download the input file just before running the calendar maker, to be sure you are working with the most current data.

-------------

### Step by step instructions:

0. Make sure you have the correct version of python installed properly, along with all the packages listed in Requirements.

1. Following the links/tips above, find your NOAA tide station of interest, and download the Annual TXT format of the published tide tables. It must be the TXT format, not PDF or XML. Make sure it is the *ANNUAL* tide tables and not the 2-day predictions.

2. Move the file into the folder where calendar_maker.py and associated files located. Rename it to a filename that contains no spaces. It doesn’t need to have a file extension, though .txt can be handy.

3. Open a terminal, cd into the aforementioned folder, and run calendar\_maker.py (either `python calendar_maker.py` or `python3 calendar_maker.py` depending on your defaults).

--------
### If NOAA file format changes:

Procedures that will probably need revision are @@@@@@, @@@@@@, and @@@@@. The calendar maker was designed to constrain all input-format-dependent routines to these procedures. Generally speaking, the input just needs to a. allow some way to set all the station metadata attributes - placename, latitude/longitude coordinates, etc.; and b. contain a time series of high/low tide magnitude predictions.

---------
