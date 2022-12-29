import yfinance
from urllib.parse import unquote

def getTickerInfo(ticker):
    ticker = yfinance.Ticker(ticker)
    changes = getTickerChanges(ticker)
    info = ticker.info
    if not info:
        return None
    info.update(changes)
    return info

def getTickerChanges(ticker):
    try:
        print("Today for " + ticker.info['exchange'] + " = " + str(ticker.info['open']))
        print(ticker.info)
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