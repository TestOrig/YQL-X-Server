import sys
import requests
import datetime
import time

## FILL THIS IN WITH YOUR OPENWEATHERMAP API KEY 
#owmkey = sys.argv[1]
owmkey = "b4f215ca39fba72abf5e8b413859f1dd"

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

# TODO what are these values
def weatherIcon(n):
    if n in ['01d', '01n']:
        return 31
    elif n in ['02d', '02n']:
        return 33
    elif n in ['03d', '03n', '04d', '04n']: ## Cloudy
        return 27
    elif n in ['09d', '09n']:
        return 39
    elif n in ['10d', '10n']: ## Rain
        return 11
    elif n in ['11d', '11n']:
        return 37
    elif n in ['13d', '13n']:
        return 14
    elif n in ['50d', '50n']:
        return 20

def weatherPoP(pop):
  return int(float(pop)*100)

def weatherDate(dt, timezone_offset):
  currTime = time.gmtime(dt+timezone_offset)
  return str(datetime.datetime.fromtimestamp(dt).time())
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
  hourTime = time.gmtime(currTime+timezone_offset)
  return "%s:00" % str(hourTime.tm_hour+n)

# Mapping OWM moon phases
def moonPhase(phase):
  # New Moon
  if phase == 0 or phase == 1:
    return 1
  # First Quarter Moon
  elif phase == 0.25:
    return 7
  # Full Moon
  elif phase == 0.5:
    return 0
  # Last Quarter Moon
  elif phase == 0.75:
    return 19
  # Waning Crescent
  elif 0.75 <= phase <= 1:
    return 21
  # Waning Gibous
  elif 0.50 <= phase <= 0.75:
    return 17
  # Waxing Gibous
  elif 0.25 <= phase <= 0.50:
    return 9
  # Waxing Crescent
  elif 0 <= phase <= 0.50:
    return 4
