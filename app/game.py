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
    try:
        return countryData[0]
    except:
        return "error"
print(getCountryByName("123"))
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
    d = 0
    if gameState["guessesLeft"] <= 0:
        return {"message": "Game over", "distance": "blah blah"}

    guessedCountry = getCountryByName(userGuess)
    if not guessedCountry:
        return {"message": "Invalid", "distance": "another test case"}

    guessedLatLon = getLatLon(guessedCountry)
    if guessedLatLon[0] is None:
        return {"message": "Invalid", "distance": "more test cases"}

    targetLatLon = gameState["target"]["latlng"]
    distance = haversine(targetLatLon[0], targetLatLon[1], guessedLatLon[0], guessedLatLon[1])

    if userGuess.lower() == gameState["target"]["name"].lower():
        return {"message": "Correct!", "distance": distance}

    gameState["guessesLeft"] -= 1
    if gameState["guessesLeft"] == 0:
<<<<<<< HEAD
        return {"message": "Game over", "distance": distance, "answer": gameState["target"]["name"]}
    printf(distance)
=======
        return {"message": "Game over", "distance": distance}
>>>>>>> 37fb462fdb3c482e1cce80c45d66b4b25e009f66
    return {"message": "Wrong!", "distance": round(distance, 2)}
