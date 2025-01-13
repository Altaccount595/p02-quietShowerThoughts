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
def startGame():
    randomCountry = getRandomCountry()
    if not randomCountry:
        return {"error": "Could not fetch a random country."}

    gameState = {
        "target": {
            "name": randomCountry["name"]["common"],
            "latlng": getLatLon(randomCountry)
        },
        "guessesLeft": 6
    }
    return gameState

def processGuess(gameState, userGuess):
    if gameState["guessesLeft"] <= 0:
        return {"message": "Game over", "distance": None}

    guessedCountry = getCountryByName(userGuess)
    if not guessedCountry:
        return {"message": "Invalid", "distance": None}

    guessedLatLon = getLatLon(guessedCountry)
    if guessedLatLon[0] is None:
        return {"message": "Invalid", "distance": None}

    targetLatLon = gameState["target"]["latlng"]
    distance = haversine(targetLatLon[0], targetLatLon[1], guessedLatLon[0], guessedLatLon[1])

    if userGuess.lower() == gameState["target"]["name"].lower():
        return {"message": "Correct!", "distance": None}

    gameState["guessesLeft"] -= 1
    if gameState["guessesLeft"] == 0:
        return {"message": "Game over", "distance": None}

    return {"message": None, "distance": round(distance, 2)}

c = getRandomCountry()
germany = getCountryByName("norway")
if c and germany:
    cCoor = getLatLon(c)
    germanyCoor = getLatLon(germany)
    if cCoor[0] is not None and germanyCoor[0] is not None:
        distance = haversine(cCoor[0], cCoor[1], germanyCoor[0], germanyCoor[1])
        print("Random Country:", c["name"]["common"])
        print("Norway:", germany["name"]["common"])
        print("Distance:", distance, "km")
    else:
        print("Could not retrieve coordinates for one of the countries.")
else:
    print("Failed to retrieve data for countries.")
