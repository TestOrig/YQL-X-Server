import yfinance, datetime
from urllib.parse import unquote

# Cache responses per hour so we don't abuse the API and also for performance reasons.
cachedResponses = {}

def getTickerInfo(ticker):
    if ticker in cachedResponses and cachedResponses[ticker]['timestamp'] == datetime.datetime.now().strftime("%h"):
        print("Returning cached response for ticker %s" % ticker)
        return cachedResponses[ticker]
    else:
        print("Getting real response for ticker %s" % ticker)
        return getTickerInfoReal(ticker)
                    
def getTickerInfoReal(tickerName):
    ticker = yfinance.Ticker(tickerName)
    changes = getTickerChanges(ticker)
    info = ticker.info
    if not info:
        return None
    info.update(changes)
    info.update({"timestamp": datetime.datetime.now().strftime("%h")})
    if not ticker in cachedResponses:
        cachedResponses.update({tickerName: info})
    else:
        cachedResponses[ticker] = {tickerName: info}
    return info

def getTickerChanges(ticker):
    try:
        print("Today for " + ticker.info['exchange'] + " = " + str(ticker.info['open']))
    except:
        pass
    try:
        return {"change": abs(round(ticker.info['regularMarketPreviousClose'] - ticker.info['regularMarketPrice'], 2)), "changepercent": calculateChange(ticker.info['regularMarketPreviousClose'], ticker.info['regularMarketPrice'])}
    except:
        return {"change": 0, "changepercent": "0"}

def calculateChange(current, previous):
    sign = "+"

    if current == previous:
        return "0%"
    elif current < previous:
        sign = "-"
    try:
        return sign + format((abs(current - previous) / previous) * 100.0, '.2f') + "%"
    except ZeroDivisionError:
        return "x%"

def sanitizeSymbol(s):
    return unquote(s)