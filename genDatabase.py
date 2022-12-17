import json

tsv_file = open("geoplanet_places_7.10.0.tsv", "r")
json_file = open("geoDatabase.json", "w")
jsondict = {"small": {}, "state": {}, "country": {}, "city": {}, "woeid": {}}
for line in tsv_file:
    line_a = line.split("\t")
    woeid = line_a[0].replace('"', "")
    iso = line_a[1].replace('"', "")
    name = line_a[2].replace('"', "")
    type = line_a[4].replace('"', "")
    if type == "State":
        jsondict["state"].update({name: [woeid, iso]})
    if type == "City":
        jsondict["city"].update({name: [woeid, iso]})
    if type == "Town" or type == "County":
        jsondict["small"].update({name: [woeid, iso]})
    if type == "Country" or type == "Island":
        jsondict["country"].update({name: [woeid, iso]})
    jsondict["woeid"].update({woeid: name})
json.dump(jsondict, json_file, indent=2)
json_file.close()
