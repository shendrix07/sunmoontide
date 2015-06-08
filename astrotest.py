from astro import Astro


# Point Barrow, Alaska
barrow_lat = '71.3889'
barrow_lon = '-156.4792'
barrow_tz = 'America/Anchorage'

cruz_lat, cruz_lon = '36.97', '-122.02'
cruz_tz = 'America/Los_Angeles'

#alaskasun = Astro(barrow_lat, barrow_lon, barrow_tz, '2015', 'Sun')
#he = alaskasun.heights

mymoon = Astro(cruz_lat, cruz_lon, cruz_tz, '2015', 'Moon')
for i in range(365):
    print(str(mymoon.phase_day_num.index[i].date()) + " : cycle day " +
        str(mymoon.phase_day_num[i]) + " : " + 
        str(round(mymoon.percent_illuminated[i]*100)) + "% illuminated")