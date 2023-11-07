import sys
import requests
import datetime
import time
from cachetools import TTLCache

## FILL THIS IN WITH YOUR OPENWEATHERMAP API KEY
owmkey = sys.argv[1]

# Initialize a cache with a time-to-live (TTL) of 1 hour (3600 seconds)
woeidCache = TTLCache(maxsize=100, ttl=3600)

dateTable = {
  0: 1,
  1: 2,
  2: 3,
  3: 4,
  4: 5,
  5: 6,
  6: 7
}

# Helper Functions

def getLatLongForQ(q):
    latIndex1 = q.index('lat=')+4
    latIndex2 = q.index(' and')
    longIndex1 = q.index('lon=')+4
    longIndex2 = q.index(' and', latIndex2+3)
    lat = q[latIndex1:latIndex2]
    long = q[longIndex1:longIndex2-1]
    print("lat = " + lat)
    print("long = " + long)
    print("longIndex1 = " + q)
    return [lat, long]

def getWeather(lat, lng, woeid):
    # We will try to see if a cached response is in the cache, if so and the timestamp matches
    # we will return that instead of abusing the API :)
    if woeid in woeidCache:
        cachedResponse = woeidCache[woeid]
        if cachedResponse['timestamp'] == datetime.datetime.now().strftime("%Y-%m-%d %H"):
            print("Returning cached response")
            return cachedResponse['response']
    uri = 'https://api.openweathermap.org/data/2.5/onecall'
    querystring = {"lat": lat, "lon": lng,
     "exclude": "alerts,minutely",
     "units": "metric",
     "appid": owmkey}
    response = (requests.request("GET", uri, params=querystring)).json()
    if response:
      woeidCache[woeid] = {
          "response": response,
          "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H")
      }
      return response
    # TODO, None handling lmao
    return None
  
def dayOrNight(timestamp):
    global global_sunrise_time, global_sunset_time

    # Check if the global sunrise and sunset times have been set
    if global_sunrise_time is None or global_sunset_time is None:
        print("Global sunrise or sunset time has not been set.")
        return False  # Or handle the error as you see fit
    
    print("Forecast time (epoch):", timestamp)
    print("Sunrise time (epoch):", global_sunrise_time)
    print("Sunset time (epoch):", global_sunset_time)

    if global_sunrise_time < timestamp < global_sunset_time:
        print("DAYTIME for the forecast")
        return True
    else:
        print("NIGHTTIME for the forecast")
        return False


##
# 0 = lightning
# 6 = rain&snow
# 9 = rain&clouds
# 11 = rain
# 13 = flurries
# 15 = snow
# 17 = hail
# 19 = sun&haze
# 23 = haze
# 25 = ice
# 27 = Clouds/Cloudy
# 29 = moon&partlycloudy
# 30 = sun&partlycloudy
# 31 = moon
# 32 = sun
# 33 = mooncloud
# 34 = suncloud
# 35 = rain&snow
# 37 = sun&lightning
# 39 = sun&rain
# 42 = ice&snow
# 44 = sun&partlycloudy
# 46 = ice&snow
# 48 =

def weatherIcon(id, sunset, timestamp=None):  # timestamp is optional now
    day = True if timestamp is None else dayOrNight(timestamp)
    id = str(id)
    if id.startswith("2"):  # Thunderstorm
        return 0  # Lightning
    if id.startswith("3"):  # Drizzle
        return 9
    if id.startswith("5"):  # Rain
        if id == "500":  # Light rain
            return 39 if day else 9
        if id == "501":  # Moderate rain
            return 11
        if id in ["502", "503", "504"]:  # Heavy intensity rain
            return 11
        if id == "511":  # Freezing rain
            return 25
        if id.startswith("52"):  # Shower rain
            return 11
    if id.startswith("6"):  # Snow
        if id in ["600", "620"]:  # Light snow
            return 13
        if id in ["601", "621"]:  # Snow
            return 15
        if id in ["602", "622"]:  # Heavy snow
            return 46
        if id in ["611", "612", "613"]:  # Sleet
            return 6
        if id == "615" or id == "616":  # Rain and snow
            return 35
    if id.startswith("7"):  # Atmosphere (Mist, Smoke, Haze, etc.)
        if id == "781":  # Tornado
            return 0  # No specific icon for tornado, using lightning
        return 23  # Use the same icon for all misty conditions
    if id.startswith("8"):  # Clear and clouds
        if id == "800":  # Clear sky
            return 32 if day else 31
        if id == "801":  # Few clouds
            return 30 if day else 29
        if id == "802":  # Scattered clouds
            return 30 if day else 29
        if id == "803" or id == "804":  # Broken clouds, overcast clouds
            return 27
    # Additional codes for extreme weather conditions can be added here with proper mappings
    # As an example, adding a few more:
    if id.startswith("9"):  # Extreme
        if id == "900" or id == "901" or id == "902" or id == "962":  # Tornado + hurricanes
            return 0
        if id == "903":  # Cold
            return 25
        if id == "904":  # Hot
            return 19
        if id == "905":  # Windy
            return 23
        if id == "906":  # Hail
            return 17
    # Unknown or not assigned codes:
    return 48  # You can use this as a default 'unknown' code

def weatherPoP(pop):
  return int(float(pop)*100)

def hourNext(n, currTime, timezone_offset):
  hourTime = time.gmtime(currTime+timezone_offset+(3600*n))
  return "%s:00" % str(hourTime.tm_hour)

def weatherDate(dt, timezone_offset):
  currTime = time.gmtime(dt+timezone_offset)
  #return str(datetime.datetime.fromtimestamp(dt).time().strftime("%H:%M"))
  return f"{str(currTime.tm_hour)}:{str(currTime.tm_min)}"

def weatherSunrise(sunrise, timezone_offset):
    global global_sunrise_time
    global_sunrise_time = sunrise + timezone_offset
    hourTime = time.gmtime(global_sunrise_time)
    return f"{str(hourTime.tm_hour)}:{str(hourTime.tm_min)}"

def weatherSunset(sunset, timezone_offset):
    global global_sunset_time
    global_sunset_time = sunset + timezone_offset
    hourTime = time.gmtime(global_sunset_time)
    return f"{str(hourTime.tm_hour)}:{str(hourTime.tm_min)}"

# My brain is big for the next 2 functions
def dayNext(n):
  return dateTable[(datetime.datetime.now() + datetime.timedelta(days=(n))).weekday()]

def dayArray():
  return [
    dayNext(1),
    dayNext(2),
    dayNext(3),
    dayNext(4),
    dayNext(5),
    dayNext(6)
  ]

# Hour relatively to OWM output
# Hourly reported from OWM api goes like this,
# First hour: The Start of the current hour
# Second hour: Second hour and etc
# So if you retrieve the hourly data on 11:58PM
# The first hour reported would be 11:00PM



# Mapping OWM moon phases
def moonPhase(phase):
  # New Moon
  if phase == 0 or phase == 1:
    return [0, 0]
  # First Quarter Moon
  elif phase == 0.25:
    return [64, 1]
  # Full Moon
  elif phase == 0.5:
    return [108, 5]
  # Last Quarter Moon
  elif phase == 0.75:
    return [47, 5]
  # Waning Crescent
  elif 0.75 <= phase <= 1:
    return [16, 5]
  # Waning Gibous
  elif 0.50 <= phase <= 0.75:
    return [72, 5]
  # Waxing Gibous
  elif 0.25 <= phase <= 0.50:
    return [84, 1]
  # Waxing Crescent
  elif 0 <= phase <= 0.25:
    return [32, 1]
