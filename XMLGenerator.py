import sys
import requests
import re
import datetime
from iso3166 import countries
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="iOSLegacyWeather")

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

def weatherDate(dt):
  return str(datetime.datetime.fromtimestamp(dt).time())

def weatherSunrise(sunrise):
  return str(datetime.datetime.fromtimestamp(sunrise).time())

def weatherSunset(sunset):
  return str(datetime.datetime.fromtimestamp(sunset).time())

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

def hourNext(n):
  return (datetime.datetime.now().replace(microsecond=0, second=0, minute=0)+datetime.timedelta(hours=n)).strftime("%H:%M")

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

# Actual XMLGenerator functions

def getXMLforWeatherWithYQL(yql, q):
  if not "lat=" in q:
    if "limit 1" in q:
      city = yql.getWoeidName(q, nameInQuery=True)
      woeid = yql.getWoeidFromName(city)
    else:
      city = yql.getWoeidName(q)
      woeid = yql.getWoeidInQuery(q)
    location = geolocator.geocode(city)
    lat = location.latitude
    lng = location.longitude
  else:
    latlong = getLatLongForQ(q)
    lat = latlong[0]
    lng = latlong[1]
    location = (geolocator.reverse(f"{lat}, {lng}")).raw['address']
    city = location.get('city', location.get('county', 'Placeholder'))
    woeid = yql.getWoeidFromName(city)
    
  weather = getWeather(lat, lng, woeid)
  currTime = weatherDate(weather["current"]["dt"])
  print(currTime)
  sunrise = weatherSunrise(weather["current"]["sunrise"])
  sunset = weatherSunset(weather["current"]["sunset"])
  days = dayArray()
  print(weatherIcon(weather['daily'][1]['weather'][0]['icon']))
  # Formatted for your viewing needs
  print(days)
  print("post = " + str(float(weather['daily'][0]['moon_phase'])))
  print("moon phase = " + str(moonPhase(float(weather['daily'][0]['moon_phase']))))
  xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<query xmlns:yahoo="http://www.yahooapis.com/v1/base.rng" yahoo:count="2" yahoo:created="2012-10-30T11:36:42Z" yahoo:lang="en-US">
  <meta>
      <meta>
         <weather>
            <yahoo_mobile_url>https://openweathermap.org/</yahoo_mobile_url>
            <twc_mobile_url>https://apps.apple.com/us/app/openweather/id1535923697</twc_mobile_url>
            <units distanceUnits="km" pressureUnits="mb" speedUnits="km/h" tempUnits="C" />
         </weather>
      </meta>
      <meta>
         <weather>
            <yahoo_mobile_url>https://openweathermap.org/</yahoo_mobile_url>
            <twc_mobile_url>https://apps.apple.com/us/app/openweather/id1535923697</twc_mobile_url>
            <units tempUnits="C" />
         </weather>
      </meta>
   </meta>
  <results>
    <results>
      <location city="{city}" country="" latitude="{lat}" locationID="ASXX0075" longitude="{lng}" state="" woeid="{woeid}">
        <currently barometer="{weather['current']['pressure']}" feelsLike="{weather['current']['feels_like']}" moonfacevisible="{moonPhase(weather['daily'][0]['moon_phase'])}" moonphase="{moonPhase(weather['daily'][0]['moon_phase'])}" sunrise24="{sunrise}" sunset24="{sunset}" temp="{weather['current']['temp']}" time24="{currTime}" timezone="GMT" windChill="0" windSpeed="{weather['current']['wind_speed']}">
          <condition code="{weatherIcon(weather['current']['weather'][0]['icon'])}" />
        </currently>
        <forecast>
          <day dayOfWeek="{days[0]}" poP="{weatherPoP(weather['daily'][0]["pop"])}">
            <temp high="{weather['daily'][0]['temp']['max']}" low="{round(float(weather['daily'][0]['temp']['min']))}" />
            <condition code="{weatherIcon(weather['daily'][0]['weather'][0]['icon'])}" />
          </day>
          <day dayOfWeek="{days[1]}" poP="{weatherPoP(weather['daily'][1]["pop"])}">
            <temp high="{weather['daily'][1]['temp']['max']}" low="{round(float(weather['daily'][1]['temp']['min']))}" />
            <condition code="{weatherIcon(weather['daily'][1]['weather'][0]['icon'])}" />
          </day>
          <day dayOfWeek="{days[2]}" poP="{weatherPoP(weather['daily'][2]["pop"])}">
            <temp high="{weather['daily'][2]['temp']['max']}" low="{round(float(weather['daily'][2]['temp']['min']))}" />
            <condition code="{weatherIcon(weather['daily'][2]['weather'][0]['icon'])}" />
          </day>
          <day dayOfWeek="{days[3]}" poP="{weatherPoP(weather['daily'][3]["pop"])}">
            <temp high="{weather['daily'][3]['temp']['max']}" low="{round(float(weather['daily'][3]['temp']['min']))}" />
            <condition code="{weatherIcon(weather['daily'][3]['weather'][0]['icon'])}" />
          </day>
          <day dayOfWeek="{days[4]}" poP="{weatherPoP(weather['daily'][4]["pop"])}">
            <temp high="{weather['daily'][4]['temp']['max']}" low="{round(float(weather['daily'][4]['temp']['min']))}" />
            <condition code="{weatherIcon(weather['daily'][4]['weather'][0]['icon'])}" />
          </day>
          <day dayOfWeek="{days[5]}" poP="{weatherPoP(weather['daily'][5]["pop"])}">
            <temp high="{weather['daily'][5]['temp']['max']}" low="{round(float(weather['daily'][5]['temp']['min']))}" />
            <condition code="{weatherIcon(weather['daily'][5]['weather'][0]['icon'])}" />
          </day>
          <extended_forecast_url>https://1pwn.ixmoe.com</extended_forecast_url>
        </forecast>
      </location>
    </results>
    <results>
      <location woeid="{woeid}">
        <hourlyforecast>
          <hour time24="{hourNext(0)}">
            <condition code="{weatherIcon(weather['hourly'][0]['weather'][0]['icon'])}" poP="{weatherPoP(weather['hourly'][0]['pop'])}" temp="{weather['hourly'][0]['temp']}" />
          </hour>
          <hour time24="{hourNext(1)}">
            <condition code="{weatherIcon(weather['hourly'][1]['weather'][0]['icon'])}" poP="{weatherPoP(weather['hourly'][1]['pop'])}" temp="{weather['hourly'][1]['temp']}" />
          </hour>
          <hour time24="{hourNext(2)}">
            <condition code="{weatherIcon(weather['hourly'][2]['weather'][0]['icon'])}" poP="{weatherPoP(weather['hourly'][2]['pop'])}" temp="{weather['hourly'][2]['temp']}" />
          </hour>
          <hour time24="{hourNext(3)}">
            <condition code="{weatherIcon(weather['hourly'][3]['weather'][0]['icon'])}" poP="{weatherPoP(weather['hourly'][3]['pop'])}" temp="{weather['hourly'][3]['temp']}" />
          </hour>
          <hour time24="{hourNext(4)}">
            <condition code="{weatherIcon(weather['hourly'][4]['weather'][0]['icon'])}" poP="{weatherPoP(weather['hourly'][4]['pop'])}" temp="{weather['hourly'][4]['temp']}" />
          </hour>
          <hour time24="{hourNext(5)}">
            <condition code="{weatherIcon(weather['hourly'][5]['weather'][0]['icon'])}" poP="{weatherPoP(weather['hourly'][5]['pop'])}" temp="{weather['hourly'][5]['temp']}" />
          </hour>
          <hour time24="{hourNext(6)}">
            <condition code="{weatherIcon(weather['hourly'][6]['weather'][0]['icon'])}" poP="{weatherPoP(weather['hourly'][6]['pop'])}" temp="{weather['hourly'][6]['temp']}" />
          </hour>
          <hour time24="{hourNext(7)}">
            <condition code="{weatherIcon(weather['hourly'][7]['weather'][0]['icon'])}" poP="{weatherPoP(weather['hourly'][7]['pop'])}" temp="{weather['hourly'][7]['temp']}" />
          </hour>
          <hour time24="{hourNext(8)}">
            <condition code="{weatherIcon(weather['hourly'][8]['weather'][0]['icon'])}" poP="{weatherPoP(weather['hourly'][8]['pop'])}" temp="{weather['hourly'][8]['temp']}" />
          </hour>
          <hour time24="{hourNext(9)}">
            <condition code="{weatherIcon(weather['hourly'][9]['weather'][0]['icon'])}" poP="{weatherPoP(weather['hourly'][9]['pop'])}" temp="{weather['hourly'][9]['temp']}" />
          </hour>
          <hour time24="{hourNext(10)}">
            <condition code="{weatherIcon(weather['hourly'][10]['weather'][0]['icon'])}" poP="{weatherPoP(weather['hourly'][10]['pop'])}" temp="{weather['hourly'][10]['temp']}" />
          </hour>
          <hour time24="{hourNext(11)}">
            <condition code="{weatherIcon(weather['hourly'][11]['weather'][0]['icon'])}" poP="{weatherPoP(weather['hourly'][11]['pop'])}" temp="{weather['hourly'][11]['temp']}" />
          </hour>
        </hourlyforecast>
      </location>
    </results>
  </results>
</query>'''
  finalR = re.sub('\s+(?=<)', '', xml)
  return finalR
    
def getXMLforWeatherWithYQLLegacy(yql, q):
  woeid = yql.getWoeidInQuery(q, formatted=True)
  city = yql.getWoeidName(q, formatted=True)
  location = geolocator.geocode(city)
  lat = location.latitude
  lng = location.longitude
    
  weather = getWeather(lat, lng, woeid)
  currTime = weatherDate(weather["current"]["dt"])
  print(currTime)
  sunrise = weatherSunrise(weather["current"]["sunrise"])
  sunset = weatherSunset(weather["current"]["sunset"])
  days = dayArray()
  print(weatherIcon(weather['daily'][1]['weather'][0]['icon']))
  # Formatted for your viewing needs
  print(days)
  xml = f'''<?xml version="1.0" encoding="UTF-8"?>
            <response>
              <result>
                <list>
                    <item>
                      <location city="{city}" id="{woeid}" />
                      <units temperature="F" />
                      <condition time="{currTime}" temp="{weather['current']['temp']}" code="{weatherIcon(weather['current']['weather'][0]['icon'])}" />
                      <astronomy moonfacevisible="0" moonphase="0" sunrise="{sunrise}" sunset="{sunset}" />
                      <forecast>
                        <day dayofweek="{days[0]}" code="{weatherIcon(weather['daily'][0]['weather'][0]['icon'])}" high="{weather['daily'][0]['temp']['max']}" low="{round(float(weather['daily'][0]['temp']['min']))}" />
                        <day dayofweek="{days[1]}" code="{weatherIcon(weather['daily'][1]['weather'][0]['icon'])}" high="{weather['daily'][1]['temp']['max']}" low="{round(float(weather['daily'][1]['temp']['min']))}" />
                        <day dayofweek="{days[2]}" code="{weatherIcon(weather['daily'][2]['weather'][0]['icon'])}" high="{weather['daily'][2]['temp']['max']}" low="{round(float(weather['daily'][2]['temp']['min']))}" />
                        <day dayofweek="{days[3]}" code="{weatherIcon(weather['daily'][3]['weather'][0]['icon'])}" high="{weather['daily'][3]['temp']['max']}" low="{round(float(weather['daily'][3]['temp']['min']))}" />
                        <day dayofweek="{days[4]}" code="{weatherIcon(weather['daily'][4]['weather'][0]['icon'])}" high="{weather['daily'][4]['temp']['max']}" low="{round(float(weather['daily'][4]['temp']['min']))}" />
                        <day dayofweek="{days[5]}" code="{weatherIcon(weather['daily'][5]['weather'][0]['icon'])}" high="{weather['daily'][5]['temp']['max']}" low="{round(float(weather['daily'][5]['temp']['min']))}" />
                      </forecast>
                    </item>
                </list>
              </result>
            </response>'''
  finalR = re.sub('\s+(?=<)', '', xml)
  return finalR

def getXMLforSearchWithYQL(yql, q):
  similarResults = yql.getSimilarName(q)
  middle = ""
  firstHalf = '''<?xml version="1.0" encoding="UTF-8"?>
<query
	xmlns:yahoo="http://www.yahooapis.com/v1/base.rng" yahoo:count="1" yahoo:created="2012-10-30T11:36:42Z" yahoo:lang="en-US">
	<results>'''
 
  for i in similarResults:
    #print(i)
    country = countries.get(i["iso"])
    match i["type"]:
      case "state":
        middle += f'''<location city="{i["name"]}" country="{country.name}" countryAbbr="{country.alpha3}" locationID="0000" woeid="{i["woeid"]}"/>'''
      case "country":
        middle += f'''<location city="{i["name"]}" country="{country.name}" countryAbbr="{country.alpha3}" locationID="0000" woeid="{i["woeid"]}"/>'''
      case "city":
        middle += f'''<location city="{i["name"]}" country="{country.name}" countryAbbr="{country.alpha3}" locationID="0000" woeid="{i["woeid"]}"/>'''
      case "small":
        middle += f'''<location city="{i["name"]}" country="{country.name}" countryAbbr="{country.alpha3}" locationID="0000" woeid="{i["woeid"]}"/>'''
  secondHalf = '''</results>
</query>'''
  xml = firstHalf+middle+secondHalf
  finalR = re.sub('\s+(?=<)', '', xml)
  return finalR

def getXMLforSearchWithYQLLegacy(yql, q):
  similarResults = yql.getSimilarName(q)
  middle = ""
  firstHalf = '''<?xml version="1.0" encoding="UTF-8"?><response><result><list>'''
  for i in similarResults:
    #print(i)
    country = countries.get(i["iso"])
    match i["type"]:
      case "state":
        middle += f'''<item><id>{i["woeid"]}</id><city>{i["name"]}</city><countryname>{country.name}</countryname></item>'''
      case "country":
        middle += f'''<item><id>{i["woeid"]}</id><city>{i["name"]}</city><countryname>{country.name}</countryname></item>'''
      case "city":
        middle += f'''<item><id>{i["woeid"]}</id><city>{i["name"]}</city><countryname>{country.name}</countryname></item>'''
      case "small":
        middle += f'''<item><id>{i["woeid"]}</id><city>{i["name"]}</city><countryname>{country.name}</countryname></item>'''
  secondHalf = '''</list></result></response>'''
  xml = firstHalf+middle+secondHalf
  finalR = re.sub('\s+(?=<)', '', xml)
  return finalR