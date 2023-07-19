import json
import re, time, requests
from iso3166 import countries
from geopy.geocoders import Nominatim, GeoNames
from Weather import *
from Stocks import *
n_geolocator = Nominatim(user_agent="iOSLegacyWeather", timeout=10)
m_geolocator = GeoNames("electimon")

# Actual XMLGenerator functions
# Weather
def getWeatherXMLWithYQLandLatLonginQ(yql, q):
  # Handle Lat and Long in query
  latlong = getLatLongForQ(q)
  lat = latlong[0]
  lng = latlong[1]
  try:
    location = (m_geolocator.reverse(f"{lat}, {lng}")).raw['address']
  except:
    location = (n_geolocator.reverse(f"{lat}, {lng}")).raw['address']
  try:
    city = location['town']
  except:
    try:
      city = location['region']
    except:
      city = location['city']
  woeid = yql.getWoeidFromName(city)   
  weather = getWeather(lat, lng, woeid)
  currTime = weatherDate(weather["current"]["dt"], weather["timezone_offset"])
  try:
    sunrise = weatherSunrise(weather["current"]["sunrise"], weather["timezone_offset"])
    sunset = weatherSunset(weather["current"]["sunset"], weather["timezone_offset"])
  except:
    sunrise = "00:00AM"
    sunset = "00:00AM"
  print("currTime = " + currTime)
  print("sunrise = " + sunrise)
  print("sunset = "+ sunset)
  days = dayArray()
  currentDayMoonPhase = moonPhase(float(weather['daily'][0]['moon_phase']))
  # Formatted for your viewing needs
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
                    <currently barometer="{weather['current']['pressure']}" feelsLike="{weather['current']['feels_like']}" moonfacevisible="{currentDayMoonPhase[0]}" moonphase={currentDayMoonPhase[1]}" sunrise24="{sunrise}" sunset24="{sunset}" temp="{weather['current']['temp']}" time24="{currTime}" timezone="GMT" windChill="0" windSpeed="{weather['current']['wind_speed']}">
                      <condition code="{weatherIcon(weather['current']['weather'][0]['id'], weather["current"]["sunset"])}" />
                    </currently>
                    <forecast>
                      <day dayOfWeek="{days[0]}" poP="{weatherPoP(weather['daily'][0]["pop"])}">
                        <temp high="{weather['daily'][0]['temp']['max']}" low="{round(float(weather['daily'][0]['temp']['min']))}" />
                        <condition code="{weatherIcon(weather['daily'][0]['weather'][0]['id'], weather["current"]["sunset"])}" />
                      </day>
                      <day dayOfWeek="{days[1]}" poP="{weatherPoP(weather['daily'][1]["pop"])}">
                        <temp high="{weather['daily'][1]['temp']['max']}" low="{round(float(weather['daily'][1]['temp']['min']))}" />
                        <condition code="{weatherIcon(weather['daily'][1]['weather'][0]['id'], weather["current"]["sunset"])}" />
                      </day>
                      <day dayOfWeek="{days[2]}" poP="{weatherPoP(weather['daily'][2]["pop"])}">
                        <temp high="{weather['daily'][2]['temp']['max']}" low="{round(float(weather['daily'][2]['temp']['min']))}" />
                        <condition code="{weatherIcon(weather['daily'][2]['weather'][0]['id'], weather["current"]["sunset"])}" />
                      </day>
                      <day dayOfWeek="{days[3]}" poP="{weatherPoP(weather['daily'][3]["pop"])}">
                        <temp high="{weather['daily'][3]['temp']['max']}" low="{round(float(weather['daily'][3]['temp']['min']))}" />
                        <condition code="{weatherIcon(weather['daily'][3]['weather'][0]['id'], weather["current"]["sunset"])}" />
                      </day>
                      <day dayOfWeek="{days[4]}" poP="{weatherPoP(weather['daily'][4]["pop"])}">
                        <temp high="{weather['daily'][4]['temp']['max']}" low="{round(float(weather['daily'][4]['temp']['min']))}" />
                        <condition code="{weatherIcon(weather['daily'][4]['weather'][0]['id'], weather["current"]["sunset"])}" />
                      </day>
                      <day dayOfWeek="{days[5]}" poP="{weatherPoP(weather['daily'][5]["pop"])}">
                        <temp high="{weather['daily'][5]['temp']['max']}" low="{round(float(weather['daily'][5]['temp']['min']))}" />
                        <condition code="{weatherIcon(weather['daily'][5]['weather'][0]['id'], weather["current"]["sunset"])}" />
                      </day>
                      <extended_forecast_url>https://1pwn.ixmoe.com</extended_forecast_url>
                    </forecast>
                  </location>
                </results>
                <results>
                  <location woeid="{woeid}">
                    <hourlyforecast>
                      <hour time24="{hourNext(0, weather["current"]["dt"], weather["timezone_offset"])}">
                        <condition code="{weatherIcon(weather['hourly'][0]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][0]['pop'])}" temp="{weather['hourly'][0]['temp']}" />
                      </hour>
                      <hour time24="{hourNext(1, weather["current"]["dt"], weather["timezone_offset"])}">
                        <condition code="{weatherIcon(weather['hourly'][1]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][1]['pop'])}" temp="{weather['hourly'][1]['temp']}" />
                      </hour>
                      <hour time24="{hourNext(2, weather["current"]["dt"], weather["timezone_offset"])}">
                        <condition code="{weatherIcon(weather['hourly'][2]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][2]['pop'])}" temp="{weather['hourly'][2]['temp']}" />
                      </hour>
                      <hour time24="{hourNext(3, weather["current"]["dt"], weather["timezone_offset"])}">
                        <condition code="{weatherIcon(weather['hourly'][3]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][3]['pop'])}" temp="{weather['hourly'][3]['temp']}" />
                      </hour>
                      <hour time24="{hourNext(4, weather["current"]["dt"], weather["timezone_offset"])}">
                        <condition code="{weatherIcon(weather['hourly'][4]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][4]['pop'])}" temp="{weather['hourly'][4]['temp']}" />
                      </hour>
                      <hour time24="{hourNext(5, weather["current"]["dt"], weather["timezone_offset"])}">
                        <condition code="{weatherIcon(weather['hourly'][5]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][5]['pop'])}" temp="{weather['hourly'][5]['temp']}" />
                      </hour>
                      <hour time24="{hourNext(6, weather["current"]["dt"], weather["timezone_offset"])}">
                        <condition code="{weatherIcon(weather['hourly'][6]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][6]['pop'])}" temp="{weather['hourly'][6]['temp']}" />
                      </hour>
                      <hour time24="{hourNext(7, weather["current"]["dt"], weather["timezone_offset"])}">
                        <condition code="{weatherIcon(weather['hourly'][7]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][7]['pop'])}" temp="{weather['hourly'][7]['temp']}" />
                      </hour>
                      <hour time24="{hourNext(8, weather["current"]["dt"], weather["timezone_offset"])}">
                        <condition code="{weatherIcon(weather['hourly'][8]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][8]['pop'])}" temp="{weather['hourly'][8]['temp']}" />
                      </hour>
                      <hour time24="{hourNext(9, weather["current"]["dt"], weather["timezone_offset"])}">
                        <condition code="{weatherIcon(weather['hourly'][9]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][9]['pop'])}" temp="{weather['hourly'][9]['temp']}" />
                      </hour>
                      <hour time24="{hourNext(10, weather["current"]["dt"], weather["timezone_offset"])}">
                        <condition code="{weatherIcon(weather['hourly'][10]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][10]['pop'])}" temp="{weather['hourly'][10]['temp']}" />
                      </hour>
                      <hour time24="{hourNext(11, weather["current"]["dt"], weather["timezone_offset"])}">
                        <condition code="{weatherIcon(weather['hourly'][11]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][11]['pop'])}" temp="{weather['hourly'][11]['temp']}" />
                      </hour>
                    </hourlyforecast>
                  </location>
                </results>
              </results>
            </query>'''
  finalR = re.sub('\s+(?=<)', '', xml)
  return finalR

def getWeatherXMLWithYQLandQ(yql, q):
  if "limit 1" in q:
    cities = yql.getNamesForWoeidsInQ(q, nameInQuery=True)
    woeids = [yql.getWoeidFromName(cities[0])]
  else:
    cities = yql.getNamesForWoeidsInQ(q)
    woeids = yql.getWoeidsInQuery(q)
  firstHalf =  '''<?xml version="1.0" encoding="UTF-8"?>
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
                    <results>'''
  forecastStart = "<results>"
  forecastMiddle = ""
  forecastEnd = "</results>"
  hourlyStart = "<results>"
  hourlyMiddle = ""
  hourlyEnd = "</results>"
  lastHalf = '''</results></query>'''
  for index, city in enumerate(cities):
    try:
      location = n_geolocator.geocode(city)
    except:
      location = m_geolocator.geocode(city)
    if not location:
      return "Failed to geocode this location"
    lat = location.latitude
    lng = location.longitude
      
    weather = getWeather(lat, lng, woeids[index])
    currTime = weatherDate(weather["current"]["dt"], weather["timezone_offset"])
    try:
      sunrise = weatherSunrise(weather["current"]["sunrise"], weather["timezone_offset"])
      sunset = weatherSunset(weather["current"]["sunset"], weather["timezone_offset"])
    except:
      sunrise = "00:00AM"
      sunset = "00:00AM"
    days = dayArray()
    currentDayMoonPhase = moonPhase(float(weather['daily'][0]['moon_phase']))
    # Formatted for your viewing needs
    print("post = " + str(float(weather['daily'][0]['moon_phase'])))
    print("moon phase = " + str(moonPhase(float(weather['daily'][0]['moon_phase']))))
    print("icon = " + str(weatherIcon(weather['current']['weather'][0]['id'], weather["current"]["sunset"])))
    print("currTime = " + currTime)
    print("sunrise = " + sunrise)
    print("sunset = "+ sunset)
    forecastMiddle += f'''
                    <location city="{city}" country="" latitude="{lat}" locationID="ASXX0075" longitude="{lng}" state="" woeid="{woeids[index]}">
                      <currently barometer="{weather['current']['pressure']}" feelsLike="{weather['current']['feels_like']}" moonfacevisible="{currentDayMoonPhase[0]}" moonphase="{currentDayMoonPhase[1]}" sunrise24="{sunrise}" sunset24="{sunset}" temp="{weather['current']['temp']}" time24="{currTime}" timezone="GMT" windChill="0" windSpeed="{weather['current']['wind_speed']}">
                        <condition code="{weatherIcon(weather['current']['weather'][0]['id'], weather["current"]["sunset"])}" />
                      </currently>
                      <forecast>
                        <day dayOfWeek="{days[0]}" poP="{weatherPoP(weather['daily'][0]["pop"])}">
                          <temp high="{weather['daily'][0]['temp']['max']}" low="{round(float(weather['daily'][0]['temp']['min']))}" />
                          <condition code="{weatherIcon(weather['daily'][0]['weather'][0]['id'], weather["current"]["sunset"])}" />
                        </day>
                        <day dayOfWeek="{days[1]}" poP="{weatherPoP(weather['daily'][1]["pop"])}">
                          <temp high="{weather['daily'][1]['temp']['max']}" low="{round(float(weather['daily'][1]['temp']['min']))}" />
                          <condition code="{weatherIcon(weather['daily'][1]['weather'][0]['id'], weather["current"]["sunset"])}" />
                        </day>
                        <day dayOfWeek="{days[2]}" poP="{weatherPoP(weather['daily'][2]["pop"])}">
                          <temp high="{weather['daily'][2]['temp']['max']}" low="{round(float(weather['daily'][2]['temp']['min']))}" />
                          <condition code="{weatherIcon(weather['daily'][2]['weather'][0]['id'], weather["current"]["sunset"])}" />
                        </day>
                        <day dayOfWeek="{days[3]}" poP="{weatherPoP(weather['daily'][3]["pop"])}">
                          <temp high="{weather['daily'][3]['temp']['max']}" low="{round(float(weather['daily'][3]['temp']['min']))}" />
                          <condition code="{weatherIcon(weather['daily'][3]['weather'][0]['id'], weather["current"]["sunset"])}" />
                        </day>
                        <day dayOfWeek="{days[4]}" poP="{weatherPoP(weather['daily'][4]["pop"])}">
                          <temp high="{weather['daily'][4]['temp']['max']}" low="{round(float(weather['daily'][4]['temp']['min']))}" />
                          <condition code="{weatherIcon(weather['daily'][4]['weather'][0]['id'], weather["current"]["sunset"])}" />
                        </day>
                        <day dayOfWeek="{days[5]}" poP="{weatherPoP(weather['daily'][5]["pop"])}">
                          <temp high="{weather['daily'][5]['temp']['max']}" low="{round(float(weather['daily'][5]['temp']['min']))}" />
                          <condition code="{weatherIcon(weather['daily'][5]['weather'][0]['id'], weather["current"]["sunset"])}" />
                        </day>
                        <extended_forecast_url>https://1pwn.ixmoe.com</extended_forecast_url>
                      </forecast>
                    </location>
                  '''
    hourlyMiddle +=  f'''<location woeid="{woeids[index]}">
                          <hourlyforecast>
                            <hour time24="{hourNext(0, weather["current"]["dt"], weather["timezone_offset"])}">
                              <condition code="{weatherIcon(weather['hourly'][0]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][0]['pop'])}" temp="{weather['hourly'][0]['temp']}" />
                            </hour>
                            <hour time24="{hourNext(1, weather["current"]["dt"], weather["timezone_offset"])}">
                              <condition code="{weatherIcon(weather['hourly'][1]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][1]['pop'])}" temp="{weather['hourly'][1]['temp']}" />
                            </hour>
                            <hour time24="{hourNext(2, weather["current"]["dt"], weather["timezone_offset"])}">
                              <condition code="{weatherIcon(weather['hourly'][2]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][2]['pop'])}" temp="{weather['hourly'][2]['temp']}" />
                            </hour>
                            <hour time24="{hourNext(3, weather["current"]["dt"], weather["timezone_offset"])}">
                              <condition code="{weatherIcon(weather['hourly'][3]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][3]['pop'])}" temp="{weather['hourly'][3]['temp']}" />
                            </hour>
                            <hour time24="{hourNext(4, weather["current"]["dt"], weather["timezone_offset"])}">
                              <condition code="{weatherIcon(weather['hourly'][4]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][4]['pop'])}" temp="{weather['hourly'][4]['temp']}" />
                            </hour>
                            <hour time24="{hourNext(5, weather["current"]["dt"], weather["timezone_offset"])}">
                              <condition code="{weatherIcon(weather['hourly'][5]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][5]['pop'])}" temp="{weather['hourly'][5]['temp']}" />
                            </hour>
                            <hour time24="{hourNext(6, weather["current"]["dt"], weather["timezone_offset"])}">
                              <condition code="{weatherIcon(weather['hourly'][6]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][6]['pop'])}" temp="{weather['hourly'][6]['temp']}" />
                            </hour>
                            <hour time24="{hourNext(7, weather["current"]["dt"], weather["timezone_offset"])}">
                              <condition code="{weatherIcon(weather['hourly'][7]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][7]['pop'])}" temp="{weather['hourly'][7]['temp']}" />
                            </hour>
                            <hour time24="{hourNext(8, weather["current"]["dt"], weather["timezone_offset"])}">
                              <condition code="{weatherIcon(weather['hourly'][8]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][8]['pop'])}" temp="{weather['hourly'][8]['temp']}" />
                            </hour>
                            <hour time24="{hourNext(9, weather["current"]["dt"], weather["timezone_offset"])}">
                              <condition code="{weatherIcon(weather['hourly'][9]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][9]['pop'])}" temp="{weather['hourly'][9]['temp']}" />
                            </hour>
                            <hour time24="{hourNext(10, weather["current"]["dt"], weather["timezone_offset"])}">
                              <condition code="{weatherIcon(weather['hourly'][10]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][10]['pop'])}" temp="{weather['hourly'][10]['temp']}" />
                            </hour>
                            <hour time24="{hourNext(11, weather["current"]["dt"], weather["timezone_offset"])}">
                              <condition code="{weatherIcon(weather['hourly'][11]['weather'][0]['id'], weather["current"]["sunset"])}" poP="{weatherPoP(weather['hourly'][11]['pop'])}" temp="{weather['hourly'][11]['temp']}" />
                            </hour>
                          </hourlyforecast>
                        </location>'''
  # I love destroying XML
  xml = firstHalf + forecastStart + forecastMiddle + forecastEnd + hourlyStart + hourlyMiddle + hourlyEnd + lastHalf
  finalR = re.sub('\s+(?=<)', '', xml)
  return finalR

def getLegacyWeatherXMLWithYQLandQ(yql, q):
  woeid = yql.getWoeidInQuery(q, formatted=True)
  city = yql.getWoeidName(q, formatted=True)
  try:
    location = n_geolocator.geocode(city)
  except:
    location = m_geolocator.geocode(city)
  lat = location.latitude
  lng = location.longitude
    
  weather = getWeather(lat, lng, woeid)
  currTime = weatherDate(weather["current"]["dt"], weather["timezone_offset"])
  print(currTime)
  sunrise = weatherSunrise(weather["current"]["sunrise"], weather["timezone_offset"])
  sunset = weatherSunset(weather["current"]["sunset"], weather["timezone_offset"])
  days = dayArray()
  print(weatherIcon(weather['daily'][1]['weather'][0]['icon']))
  # Formatted for your viewing needs
  print(days)
  xml = f'''<?xml version="1.0"?>
            <response>
              <result>
                <list>
                    <item>
                      <location city="{city}" id="{woeid}" />
                      <units temperature="F" />
                      <condition time="{currTime}" temp="{weather['current']['temp']}" code="{weatherIcon(weather['current']['weather'][0]['id'], weather["current"]["sunset"])}" />
                      <astronomy moonfacevisible="0" moonphase="0" sunrise="{sunrise}" sunset="{sunset}" />
                      <forecast>
                        <day dayofweek="{days[0]}" code="{weatherIcon(weather['daily'][0]['weather'][0]['id'], weather["current"]["sunset"])}" high="{weather['daily'][0]['temp']['max']}" low="{round(float(weather['daily'][0]['temp']['min']))}" />
                        <day dayofweek="{days[1]}" code="{weatherIcon(weather['daily'][1]['weather'][0]['id'], weather["current"]["sunset"])}" high="{weather['daily'][1]['temp']['max']}" low="{round(float(weather['daily'][1]['temp']['min']))}" />
                        <day dayofweek="{days[2]}" code="{weatherIcon(weather['daily'][2]['weather'][0]['id'], weather["current"]["sunset"])}" high="{weather['daily'][2]['temp']['max']}" low="{round(float(weather['daily'][2]['temp']['min']))}" />
                        <day dayofweek="{days[3]}" code="{weatherIcon(weather['daily'][3]['weather'][0]['id'], weather["current"]["sunset"])}" high="{weather['daily'][3]['temp']['max']}" low="{round(float(weather['daily'][3]['temp']['min']))}" />
                        <day dayofweek="{days[4]}" code="{weatherIcon(weather['daily'][4]['weather'][0]['id'], weather["current"]["sunset"])}" high="{weather['daily'][4]['temp']['max']}" low="{round(float(weather['daily'][4]['temp']['min']))}" />
                        <day dayofweek="{days[5]}" code="{weatherIcon(weather['daily'][5]['weather'][0]['id'], weather["current"]["sunset"])}" high="{weather['daily'][5]['temp']['max']}" low="{round(float(weather['daily'][5]['temp']['min']))}" />
                      </forecast>
                    </item>
                </list>
              </result>
            </response>'''
  finalR = re.sub('\s+(?=<)', '', xml)
  print(finalR)
  return xml

def getWeatherSearchXMLWithYQLandQ(yql, q):
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

def getLegacyWeatherSearchXMLWithYQLandQ(yql, q):
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

# Stocks
def getStocksXMLWithQandType(q, type):
  firstHalf = f'''<?xml version="1.0" encoding="UTF-8"?>
          <response>
            <result type="getchart" timestamp="{time.time()}">
              <list count="{len(q['symbols'])}" total="{len(q['symbols'])}">'''
  match type:
    case "getquotes":
      secondHalf = '''</list></result></response>'''
      middle = ""
      for symbol in q['symbols']:
        sanitizedSymbol = sanitizeSymbol(symbol)
        tickerInfo = getTickerInfo(symbol)
        if not tickerInfo:
          continue
        if not "open" in tickerInfo:
          tickerInfo['open'] = tickerInfo['regularMarketPrice']
        if not "volume" in tickerInfo:
          tickerInfo["volume"] = 0
        if not "marketCap" in tickerInfo:
          tickerInfo["marketCap"] = 0
        if not "dividendYield" in tickerInfo:
          tickerInfo["dividendYield"] = 0
        middle += f'''<quote>
                        <symbol>{sanitizedSymbol}</symbol>
                        <open>{tickerInfo['open']}</open>
                        <price>{tickerInfo['regularMarketPrice']}</price>
                        <change>{tickerInfo['change']}</change>
                        <changepercent>{tickerInfo['changepercent']}</changepercent>
                        <marketcap>{tickerInfo['marketCap']}</marketcap>
                        <high>{tickerInfo['regularMarketDayHigh']}</high>
                        <low>{tickerInfo['regularMarketDayLow']}</low>
                        <volume>{tickerInfo['volume']}</volume>
                        <averagedailyvolume>{tickerInfo['volume24Hr']}</averagedailyvolume>
                        <peratio>{tickerInfo['trailingPegRatio']}</peratio>
                        <yearrange>0</yearrange>
                        <dividendyield>{tickerInfo['dividendYield']}</dividendyield>
                        <link>https://1pwn.ixmoe.com</link>
                        <status>0</status>
                      </quote>'''
    case "getchart":
      if not "range" in q:
        return ""
      return ""
      secondHalf = '''</list></result></response>'''
      tickerInfo = getTickerInfo(q['symbols'][0])
      sanitizedSymbol = sanitizeSymbol(q['symbols'][0])
      print(f"https://query1.finance.yahoo.com/v8/finance/chart/{sanitizedSymbol}?interval={q['range']}")
      r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sanitizedSymbol}?interval={q['range']}")
      # middle = f'''<point>
      #               <timestamp>10000000</timestamp>
      #               <close>{tickerInfo['open']}</close>
      #               <volume>{tickerInfo['volume']}</volume>
      #              </point>'''
    case _:
      print("sadge")
      return ""

  xml = firstHalf+middle+secondHalf
  finalR = re.sub('\s+(?=<)', '', xml)
  return finalR
