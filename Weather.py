import sys
import requests
import datetime
import time

## FILL THIS IN WITH YOUR OPENWEATHERMAP API KEY 
owmkey = sys.argv[1]

# This dictionary contains woeids and data for caching along with timestamps
woeidCache = {}

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
    # We will try to see if a cached response is in the dict, if so and the timestamp matches the hour
    # it was gotten, we will return that instead of abusing the API :)
    try:
      cachedResponse = woeidCache[woeid]
      if cachedResponse:
        if cachedResponse['timestamp'].strftime("%h") == datetime.datetime.now().strftime("%h"):
          print("Returning cached response")
          return cachedResponse['response']
    except:
      # Some error happened, go get the data from API
      pass
    uri = 'https://api.openweathermap.org/data/2.5/onecall'
    querystring = {"lat": lat, "lon": lng,
     "exclude": "alerts,minutely",
     "units": "metric",
     "appid": owmkey}
    response = (requests.request("GET", uri, params=querystring)).json()
    if response:
      # If woeid in cache, we replace, if not we add, easy!
      if woeid not in woeidCache:
        woeidCache.update({woeid: {"response": response, "timestamp": datetime.datetime.now()}})
      else:
        woeidCache[woeid] = {woeid: {"response": response, "timestamp": datetime.datetime.now()}}
      return response
    # TODO, None handling lmao
    return None

def dayOrNight(sunset):
  if (time.time() / 1000 < sunset):
    return True
  else:
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
def weatherIcon(id, sunset):
  day = dayOrNight(sunset)
  id = str(id)
  if id[0] == "2": # Thunderstorm
    return 0
  if id[0] == "3": # Drizzle 
    return 11
  if id[0] == "5": # Rain
    if not id[1] == "0": # Cloudy rain/Stormy
      return 9
    return 11
  if id[0] == "6": # Snow
    if id == "600": # Light snow
      return 13
    if id == "601" or id == "602": # Snowing
      return 15
    if id == "613" or id == "615" or id == "616": # Rain and snow
      return 35
    return 15
  if id[0] == "7": # Atmospheric Conditions
    if id == "701" or id == "721" or id == "741" or id == "711": # Mist/Haze/Fog/Smoke
      return 23
    return 23 # TODO change me
  if id[0] == "8": # Cloud Conditions
    if id == "800": # Clear sky
      return 32
    if id == "801" or id == "802" or id == "803": # Partly cloudy
      if day:
        return 34
      else:
        return 33
    if id == "804":
      return 27
  if id[0] == "9": # Extreme conditions
    if id[3] == "3": # COLD
      return 25
    if id[3] == "4": # HOT
      return 19
    if id[3] == "6": # HAIL
      return 17

def weatherPoP(pop):
  return int(float(pop)*100)

def weatherDate(dt, timezone_offset):
  currTime = time.gmtime(dt+timezone_offset)
  #return str(datetime.datetime.fromtimestamp(dt).time().strftime("%H:%M"))
  return f"{str(currTime.tm_hour)}:{str(currTime.tm_min)}"

def weatherSunrise(sunrise, timezone_offset):
  hourTime = time.gmtime(sunrise+timezone_offset)
  return f"{str(hourTime.tm_hour)}:{str(hourTime.tm_min)}"

def weatherSunset(sunset, timezone_offset):
  hourTime = time.gmtime(sunset+timezone_offset)
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

def hourNext(n, currTime, timezone_offset):
  hourTime = time.gmtime(currTime+timezone_offset+(3600*n))
  return "%s:00" % str(hourTime.tm_hour)

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
