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
    url = 'https://restcountries.com/v3.1/all?fields=name,flags,currency,language,latlng'
    response = requests.get(url)
    countries = response.json()
    randomCountry = countries[4]

def getCountryByName(countryName):
    url = f'https://restcountries.com/v3.1/name/{countryName}'
    response = requests.get(url)
    countryData = response.json()
    if countryData:
        print(countryData)
    else:
        print("error getting country data")

def getLatLon(country):
    lat = country['latlng'][0] if 'latlng' in country else None
    lon = country['latlng'][1] if 'latlng' in country else None
    return lat, lon
c = getRandomCountry()
print(c)

