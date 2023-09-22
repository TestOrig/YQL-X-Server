from flask import Flask, request, redirect
import sys, os, json
from YQL import YQL
from StocksQParser import *
from xml.etree import ElementTree
import XMLGenerator

app = Flask(__name__)
sys.stdout.reconfigure(encoding='utf-8')
yql = YQL()

# Ignore these, testing :P
@app.route('/')
def hello_world():
    return "Sup"

# Stocks
@app.route('/dgw', methods=["POST", "GET"])
def dgw():
    print("Legacy app found!")
    if request.method == 'GET':
        return "ok", 200
    sentXML = request.data.decode()
    root = ElementTree.fromstring(sentXML)
    type = root[0].attrib['type']
    api = root.attrib['api']
    print(sentXML)
    if api == "finance":
        print("Using finance")
        q = parseQuery(sentXML)
        return XMLGenerator.getStocksXMLWithQandType(q, type)
    elif api == 'weather':
        print("Using Weather")
        return legacyWeatherDGW()

# Weather

# iOS 5 seems to use this endpoint, let's redirect to the regular function
@app.route('/v1/yql')
def legacyWeatherYQL(): 
    print("Legacy app found!")
    return weatherEndpoint()

@app.route('/yql/weather/dgw', methods=["POST"])
def legacyWeatherDGW():
    print("Pre iOS 5 app found!")
    if request.data:
        sentXML = request.data.decode()
        reqType = sentXML[sentXML.index("y id=")+5:sentXML.index(" time")].replace('"', "")
        print(reqType)
        if reqType == "3":
            q = sentXML[sentXML.index("ase>")+4:sentXML.index("</phr")]
            if "|" in q:
                q = q.split("|")[1]
            return XMLGenerator.getLegacyWeatherSearchXMLWithYQLandQ(yql, q)
        if reqType == "30":
            q = sentXML[sentXML.index("id>")+3:sentXML.index("</id")]
            if "|" in q:
                q = q.split("|")[1]
            print("q = " + q)
            return XMLGenerator.getLegacyWeatherXMLWithYQLandQ(yql, q)
        return ""

# iOS 6 contacts this endpoint for all things weather
@app.route('/yql/weather')
def weatherEndpoint():
    # Get the request and set the request for the yql handling object
    q = request.args.get('q')
    if q:
        print(q)
        if 'partner.weather.locations' and not 'yql.query.multi' in q:
            # Search Request
            q = q[q.index('query="')+7:q.index('" a')]
            return searchReq(q)
        elif 'partner.weather.forecasts' in q:
            # Weather Request
            return weatherReq(q)

def searchReq(q):
    return XMLGenerator.getWeatherSearchXMLWithYQLandQ(yql, q)

def weatherReq(q):
    if "lat=" in q:
        return XMLGenerator.getWeatherXMLWithYQLandLatLonginQ(yql, q)
    return XMLGenerator.getWeatherXMLWithYQLandQ(yql, q)

if __name__ == '__main__':
    if not os.path.exists("generatedWoeids.json"):
        with open("generatedWoeids.json", "w") as database:
            database.write(json.dumps({}))
            database.close()
    app.run(host="0.0.0.0", port=5002)
