from flask import Flask, request, redirect
import sys
from YQL import YQL
import XMLGenerator

app = Flask(__name__)
sys.stdout.reconfigure(encoding='utf-8')
yql = YQL()

# Ignore these, testing :P
@app.route('/')
def hello_world():
    return "Sup"

# iOS 5 seems to use this endpoint, let's redirect to the regular function
@app.route('/v1/yql')
def legacyyql(): 
    print("Legacy app found!")
    return weatherEndpoint()

@app.route('/yql/weather/dgw', methods=["POST"])
def legacydgw():
    print("Pre iOS 5 app found!")
    sentXML = request.data.decode()
    reqType = sentXML[sentXML.index("y id=")+5:sentXML.index(" time")].replace('"', "")
    print(reqType)
    if reqType == "3":
        q = sentXML[sentXML.index("ase>")+4:sentXML.index("</phr")]
        if "|" in q:
            q = q.split("|")[1]
        return XMLGenerator.getXMLforSearchWithYQLLegacy(yql, q)
    if reqType == "30":
        q = sentXML[sentXML.index("id>")+3:sentXML.index("</id")]
        if "|" in q:
            q = q.split("|")[1]
        print("q = " + q)
        return XMLGenerator.getXMLforWeatherWithYQLLegacy(yql, q)
    return ""

# iOS 6 contacts this endpoint for all things weather
@app.route('/yql/weather')
def weatherEndpoint():
    # Get the request and set the request for the yql handling object
    q = request.args.get('q')
    print(q)
    if 'partner.weather.locations' and not 'yql.query.multi' in q:
        # Search Request
        q = q[q.index('query="')+7:q.index('" a')]
        return searchReq(q)
    elif 'partner.weather.forecasts' in q:
        # Weather Request
        return weatherReq(q)
    
def searchReq(q):
    return XMLGenerator.getXMLforSearchWithYQL(yql, q)

def weatherReq(q):
    return XMLGenerator.getXMLforWeatherWithYQL(yql, q)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002)