import requests
import json
import random
import math

r = 6371.0

def toRadians(degree):
    return degree * (math.pi / 180.0)

def haversine(lat1, lon1, lat2, lon2):
    lat1 = toRadians(lat1)
    lon1 = toRadians(lon1)
    lat2 = toRadians(lat2)
    lon2 = toRadians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c

def getRandomCountry():
    url = 'https://restcountries.com/v3.1/all?fields=name,flags,currencies,languages,latlng'
    response = requests.get(url)
    countries = response.json()
    if not countries or len(countries) == 0:
        return None
    return random.choice(countries)

def getCountryByName(countryName):
    url = f'https://restcountries.com/v3.1/name/{countryName}?fields=name,latlng'
    response = requests.get(url)
    countryData = response.json()
    if countryData:
        return countryData[0]
    return None

def getLatLon(country):
    if 'latlng' in country:
        lat = country['latlng'][0]
        lon = country['latlng'][1]
        return lat, lon
    return None, None



c = getRandomCountry()
germany = getCountryByName("germany")
if c and germany:
    cCoor = getLatLon(c)
    germanyCoor = getLatLon(germany)
    if cCoor[0] is not None and germanyCoor[0] is not None:
        distance = haversine(cCoor[0], cCoor[1], germanyCoor[0], germanyCoor[1])
        print("Random Country:", c["name"]["common"])
        print("Germany:", germany["name"]["common"])
        print("Distance:", distance, "km")
    else:
        print("Could not retrieve coordinates for one of the countries.")
else:
    print("Failed to retrieve data for countries.")
