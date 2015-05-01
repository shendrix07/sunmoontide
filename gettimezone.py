import geopy
import pytz


from geopy.geocoders import GoogleV3
geolocator = GoogleV3()

myplace = 'Santa Cruz, Monterey Bay, CA'  ## TODO - get this from file header StationName, State

def getTimeZone(placename):
    mygeocode = geolocator.geocode(myplace)
mygeocode
Location(Monterey Bay, United States, (36.8007413, -121.947311, 0.0))
    mypoint = geopy.Point(mygeocode.latitude, mygeocode.longitude)
    TZ_py = geolocator.timezone(mypoint)
    return TZ_py.zone
