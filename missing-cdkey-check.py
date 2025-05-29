#!/usr/bin/env python3
import requests
from requests.adapters import HTTPAdapter
import json
import os
import sys

if not os.environ.get('COOKIE') ==  "":
    cookie = os.environ.get('COOKIE')
else:
    print("Please set the COOKIE environment mariable to your gog-al token")
    sys.exit(1)

if cookie.startswith("gog-al=") and len(cookie) == 157:
    pass
elif not "=" in cookie and len(cookie) == 150:
    cookie = "gog-al=" + cookie
else:
    print("Problem parsing gog-al variable ): ", cookie)
    sys.exit(2)

def _getIdFromName(data, target_name):
    for item in data.get('tags', []):
        if item.get('name') == target_name:
            return item.get('id')
    return None

def _getPage(cookie, pageNumber, session):
    url = f'https://www.gog.com/account/getFilteredProducts?hiddenFlag=0&mediaType=1&page={pageNumber}&sortBy=title'
    headers = {'Cookie': cookie}
    r = session.get(url, headers=headers)
    page = json.loads(r.text)
    return page

def _checkGame(cookie, id, session):
    url = f'https://www.gog.com/account/gameDetails/{id}.json'
    headers = {'Cookie': cookie}
    r = session.get(url, headers=headers)
    game = json.loads(r.text)

    print ("Checking Game: ", game["title"])
    if game["cdKey"] == "" and game["textInformation"] == "Serial keys depleted":
        print ("\nSerial keys depleted: ", game["title"])
    elif game["cdKey"] != "":
        print ("Serial Keys Available: ", game["title"])
    elif game["cdKey"] == "" and game["textInformation"] == "":
        #print ("No Serial keys Required: ", game["title"])
        pass
    else:
        print ("\nERROR: ", game["title"])

def _checkPage(game):
    if game["tags"] != []:
        for tag in game["tags"]:
            if tag == noSerialKeys:
                gamesDict["drm-free"].append(game["id"])
                return
            elif tag == serialKeys:
                gamesDict["serial-keys"].append(game["id"])
                return
            elif tag == serialKeyDepleted:
                gamesDict["depleted"].append(game["id"])
                return

    #print ("NO TAGS")
    gamesDict["unknown"].append(game["id"])

session = requests.Session()
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10)
session.mount('https://', adapter)

page = _getPage(cookie, 1, session)

totalPages = page["totalPages"]
noSerialKeys = _getIdFromName(page, "NO SERIAL KEYS")
serialKeys = _getIdFromName(page, "SERIAL KEYS")
serialKeyDepleted = _getIdFromName(page, "SERIAL KEYS DEPLETED")

gamesDict = {}
gamesDict["drm-free"] = []
gamesDict["serial-keys"] = []
gamesDict["depleted"] = []
gamesDict["unknown"] = []

print ("Checking page: ", page["page"])
for game in page["products"]:
    _checkPage(game)

for pageNumber in range(2, totalPages + 1):
    page = _getPage(cookie, pageNumber, session)
    print ("Checking page: ", page["page"])
    for game in page["products"]:
        _checkPage(game)

for id in gamesDict["depleted"]:
    _checkGame(cookie, id, session)

for id in gamesDict["unknown"]:
    _checkGame(cookie, id, session)

session.close()

print ("DRM FREE:\n", gamesDict["drm-free"])
print ("SERIAL KEYS:\n", gamesDict["serial-keys"])
print ("SERIAL KEYS DEPLETED:\n", gamesDict["depleted"])
print ("UNKNOWN:\n", gamesDict["unknown"])