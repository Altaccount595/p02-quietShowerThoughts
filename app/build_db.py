# quietShowerThoughts -
# SoftDev
# P01
# 2024-12-03
# time spent: 1.5 hrs

import sqlite3
import csv
import os
import json

DB_FILE = "user.db"
db = sqlite3.connect(DB_FILE)
c = db.cursor()

# Function to create a new database connection per request (Flask-friendly)
def get_db():
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    return db

# Makes tables in the database (run this once, or after changes)
def makeDb():
    db = get_db()
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT NOT NULL UNIQUE, password TEXT NOT NULL, avg REAL DEFAULT 0)")
    c.execute("CREATE TABLE IF NOT EXISTS games (id INTEGER PRIMARY KEY AUTOINCREMENT, guesses TEXT, creatingUsername TEXT NOT NULL, FOREIGN KEY (creatingUsername) REFERENCES users (username))")
    db.commit()

# Registers a user with a username and password,returns false if username is already taken or is null, returns true otherwise
def addUser(u, p):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT username FROM users WHERE username = ?", (u,))
    if c.fetchone() is not None:  # If the username already exists
        return False  # Return False
    else: #else add user
        if(u is None or p is None):
            return False
        c.execute("INSERT INTO users (username, password, avg) VALUES (?, ?, 0)", (u, p))
        exportUsers()
        db.commit()
        return True

# Adds a game to the database, returns False if game or user is null, returns true otherwise
#parameters being array[string], string, with the first being an array of the guesses, and the second being the username
def addGame(guesses, user):
    if(guesses is None or user is None or len(guesses) == 0):
        return False
    db = get_db()
    c = db.cursor()
    c.execute("SELECT username FROM users WHERE username = ?",(user,))
    if c.fetchone() is None:
        return False
    #INSERT CODE UPDATING THE USERS AVERAGE
    updateAvg(guesses,user)
    guesses_json = json.dumps(guesses)
    c.execute("INSERT INTO games (guesses, creatingUsername) VALUES (?,?)",(guesses_json,user,))
    exportGames()
    db.commit()
    return True

def updateAvg(guesses, user):
    db = get_db()
    c = db.cursor()
    games = getUserGames(user)
    total = 0
    for game in games:
        #print(game["guesses"])
        total+= len(game["guesses"])
    avg=(total+len(guesses))/(len(games)+1)
    c.execute("SELECT username FROM users WHERE username = ?",(user,))
    if c.fetchone() is None:
        return False
    c.execute("UPDATE users SET avg = ? WHERE username = ?", (avg,user,))
    exportUsers()
    db.commit()
    return True

# returns the user's avg as double/float? one of those 2, returns -1 if the user doesn't exist
#Parameters: String, with it being the username 
def getAvg(user):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT avg FROM users WHERE username =  ?",(user,))
    temp=c.fetchone()
    if(temp is None):
        return -1
    return temp[0]

# Gets a list of all games played by a user, returns a list of all games
#parameters: String which is the username
def getUserGames(username):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM games WHERE creatingUsername = ?", (username,))
    rows = c.fetchall()
    # Process each row to convert JSON-encoded guesses into a Python list
    games = []
    for row in rows:
        gameId, guessesJson, creatingUsername = row
        guesses = json.loads(guessesJson)
        games.append({
            "id": gameId,
            "guesses": guesses,
            "creatingUsername": creatingUsername
        })
    return games

# Gets a specific game based on id and returns it
#Parameters: integer which is the game id
def getGame(id):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM games WHERE id = ?", (id,))
    row = c.fetchone()  # Fetch one row from the result set
    if row:
        gameId, guessesJson, creatingUsername = row
        guesses = json.loads(guessesJson)  # Convert JSON string back to Python list
        return {
            "id": gameId,
            "guesses": guesses,
            "creatingUsername": creatingUsername
        }
    else:
        return None
    #returns none if no id found

# checks the user's password, if it matches return true, else return false
#Parameters: String, String, with them being the username and password respectively
def checkPass(user, p):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT password FROM users WHERE username =  ?",(user,))
    temp=c.fetchone()
    if(temp is None):
        return False
    password=temp[0]
    return password==p

# Gets a list of all games
def getAllGames():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM games")
    rows = c.fetchall()
    # Process each row to convert JSON-encoded guesses into a Python list
    games = []
    for row in rows:
        game_id, guesses_json, creating_username = row
        guesses = json.loads(guesses_json)
        games.append({
            "id": game_id,
            "guesses": guesses,
            "creatingUsername": creating_username
        })
    return games

# Gets a list of all users
def getAllUsers():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM users")
    return c.fetchall()
#gets the 5 lowest averages, returns [{username:user1,avg:avg1},{username:user2,avg:avg2}...]
def get5LowestAvg():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT username, avg FROM users ORDER BY avg ASC LIMIT 5")
    return c.fetchall()

# Deletes a game, helper function only DO NOT CALL OUTSIDE
def deleteGame(id):
    db = get_db()
    c = db.cursor()
    c.execute("DELETE FROM games WHERE id = ?", (id,))
    exportGames()
    db.commit()

# Deletes a user, returns false if user doesn't exist
#Parameters: String, which is the username
def deleteUser(user):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT username FROM users WHERE username= ?",(user,))
    if c.fetchone() is None:
        return False
    c.execute("SELECT * FROM games WHERE creatingUsername = ?", (user,))
    allGames = [row[0] for row in c.fetchall()]
    for game in allGames:
        deleteGame(game)
    c.execute("DELETE FROM users WHERE username = ?",(user,))
    exportUsers()
    db.commit()
    return True

# Helper function to export data to CSV
def exportToCSV(query, filename):
    db = get_db()
    c = db.cursor()
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        c.execute(query)
        writer.writerow([i[0] for i in c.description])  # Write header
        writer.writerows(c.fetchall())  # Write data

def exportUsers():
    exportToCSV("SELECT * FROM users", 'users.csv')

def exportGames():
    exportToCSV("SELECT * FROM games", 'games.csv')

makeDb()


#print(getAvg("ooga"))
#print(getAvg("steve"))
#print(addGame(["Italy","japan"],"ooga"))
#print(getAvg("ooga"))
#print(addGame(["usa","germany","russia"],"ooga"))
#print(addGame(["Mexico","South Africa","India"],"ooga"))
#print(getAvg("ooga"))


#LEAVE THIS IN!!!!!!!!!!!!
addUser("ooga","booga")
addGame(["Italy","japan","japan","japan","japan"],"ooga")
addUser("123","456")
addGame(["Italy","japan","japan","japan","japan","USA","USA","USA","USA","USA","USA","USA"],"123")
addUser("abc","def")
addGame(["Italy","japan","japan","japan","japan","USA","USA","USA","USA","USA","USA","USA"],"abc")
addUser("chopped","chin")
addGame(["Italy","japan","japan","japan","japan","USA","USA","USA","USA","USA","USA","USA","France","France","France","France","France","France"],"chopped")
addUser("test","case")
addGame(["Italy","japan","japan","japan","japan","USA","USA","USA","USA","USA","USA","USA","Germany","Germany","Germany","Germany","Germany","Germany","Germany","Germany"],"test")
addUser("Dweeb","Password")
addGame(["Italy","japan","japan","japan","japan","USA","USA","USA","USA","Prussia","Prussia","Prussia","Prussia","Prussia","Prussia","Prussia","Germany","Prussia","Prussia","Prussia","Prussia","Prussia","Prussia","Prussia"],"Dweeb")

db.close()