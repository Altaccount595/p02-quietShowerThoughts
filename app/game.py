import requests
import random
import math

RADIUS = 6371.0

def toRadians(degree):
    return degree * (math.pi / 180.0)

def haversine(lat1, lon1, lat2, lon2):
    lat1 = toRadians(lat1)
    lon1 = toRadians(lon1)
    lat2 = toRadians(lat2)
    lon2 = toRadians(lon2)
    dLat = lat2 - lat1
    dLon = lon2 - lon1
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(lat1) * math.cos(lat2) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return RADIUS * c

def getRandomCountry():
    url = 'https://restcountries.com/v3.1/all?fields=name,latlng'
    response = requests.get(url)
    countries = response.json()
    if not countries or len(countries) == 0:
        return None
    return random.choice(countries)

def getCountryByName(countryName):
    url = f'https://restcountries.com/v3.1/name/{countryName}?fields=name,latlng'
    response = requests.get(url)
    try:
        countryData = response.json()
        return countryData[0]
    except:
        return None

def getLatLon(country):
    if 'latlng' in country:
        lat = country['latlng'][0]
        lon = country['latlng'][1]
        return lat, lon
    return None, None

def startGame():
    randomCountry = getRandomCountry()
    if not randomCountry:
        return {"error": "Could not fetch a random country."}

    gameState = {
        "target": {
            "name": randomCountry["name"]["common"],
            "latlng": getLatLon(randomCountry)
        },
        "guessesLeft": 6,
        "cumulativeDistance": 0.0,
        "lastDistance": None
        }
    print(gameState["target"]["name"])  #for cheating
    return gameState

def processGuess(gameState, userGuess):
    if gameState["guessesLeft"] <= 0:
        return {"message": "Game over", "distance": gameState["lastDistance"], "cumulativeDistance": gameState["cumulativeDistance"]}

    guessedCountry = getCountryByName(userGuess)
    if not guessedCountry:
        return {"message": "Invalid country name.", "distance": None, "cumulativeDistance": gameState["cumulativeDistance"]}

    guessedLatLon = getLatLon(guessedCountry)
    if guessedLatLon[0] is None:
        return {"message": "Invalid country coordinates.", "distance": None, "cumulativeDistance": gameState["cumulativeDistance"]}

    targetLatLon = gameState["target"]["latlng"]
    distance = haversine(targetLatLon[0], targetLatLon[1], guessedLatLon[0], guessedLatLon[1])
    distance = round(distance, 2)
    gameState["lastDistance"] = distance
    gameState["cumulativeDistance"] += distance
    gameState["guessesLeft"] -= 1

    if userGuess.lower() == gameState["target"]["name"].lower():
        return {"message": "Correct!", "distance": gameState["lastDistance"], "cumulativeDistance": gameState["cumulativeDistance"]}

    if gameState["guessesLeft"] == 0:
        return {"message": "Game over", "distance": gameState["lastDistance"], "cumulativeDistance": gameState["cumulativeDistance"]}

    return {"message": "Wrong!", "distance": gameState["lastDistance"], "cumulativeDistance": gameState["cumulativeDistance"]}