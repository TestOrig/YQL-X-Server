# WeatherX-Server
## Setup
To run this server, you need python 3.10, flask, requests, geopy and iso3166.

To generate the database used with this server use genDatabase.py with geoplanet_places_7.10.0.tsv.

The database is used for WOEID mapping as Yahoo's servers are gone.

## Running
Just run main.py and point your weather client to your IP:5002.

Beware, geoDatabase.json is typically around 200MB and it is loaded into RAM for performance reasons!
