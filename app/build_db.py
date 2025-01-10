# RACAMOJO -
# SoftDev
# P01
# 2024-12-03
# time spent: 1.5 hrs

import sqlite3
import csv
import os
import json
import requests
import hashlib

MEME_API_URL = "https://api.mememaker.com/v1/memes"
MEME_API_KEY = "your_api_key_here"  # Replace with your API key

def generate_meme(template_id, top_text, bottom_text):
    """
    Generates a meme using the Meme Maker API.

    Args:
        template_id (str): The ID of the meme template.
        top_text (str): The text to appear at the top of the meme.
        bottom_text (str): The text to appear at the bottom of the meme.

    Returns:
        str: URL of the generated meme if successful, or an error message.
    """
    headers = {
        "Authorization": f"Bearer {MEME_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "template_id": template_id,
        "text0": top_text,
        "text1": bottom_text
    }

    try:
        response = requests.post(MEME_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            meme_data = response.json()
            return meme_data.get("url")  # Return the generated meme URL
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
        
DB_FILE = "user.db"
db = sqlite3.connect(DB_FILE, check_same_thread=False)
c = db.cursor()

# Function to create a new database connection per request (Flask-friendly)
def get_db():
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    return db

# Makes tables in the database (run this once, or after changes)
def makeDb():
    db = get_db()
    c = db.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS memes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image TEXT,
            upvotes INTEGER,
            creatingUsername TEXT NOT NULL,
            FOREIGN KEY (creatingUsername) REFERENCES users (username)
        )
    """)
    db.commit()

# Registers a user with a username and password,returns false if username is already taken or is null, returns true otherwise
def addUser(u, p):
    print(f"Adding user: {u}, {p}")  # Debugging print
    try:
        db = get_db()
        c = db.cursor()
        c.execute("SELECT username FROM users WHERE username = ?", (u,))
        if c.fetchone() is not None:
            print("Username already exists.")  # Debugging print
            return False  # User already exists
        if u and p:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u, p))
            db.commit()
            return True
        print("Invalid input")  # Debugging print
        return False
    except Exception as e:
        print(f"Error in addUser: {e}")  # Error print
        return False


# Adds a meme to the database, returns False if meme or user is null, returns true otherwise
#the image should be stored as a string which links to the image
#parameters being string, string, with the first being the link to the image, and the second being the username
def addMeme(img, user):
    if(img is None or user is None):
        return False
    db = get_db()
    c = db.cursor()
    c.execute("SELECT username FROM users WHERE username = ?",(user,))
    if c.fetchone() is None:
        return False
    c.execute("INSERT INTO memes (image, upvotes, creatingUsername) VALUES (?,0,?)",(img,user,))
    exportMemes()
    db.commit()
    return True

# Gets a list of all memes created by a user, returns a list of all memes
#parameters: String which is the username
def getUserMemes(username):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT id, image, upvotes FROM memes WHERE creatingUsername = ?", (username,))
    return c.fetchall()

# Gets a specific meme based on id and returns it
#Parameters: integer which is the meme id
def getMeme(id):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT id, image, upvotes, creatingUsername FROM memes WHERE id = ?", (id,))
    return c.fetchone()  # This returns the first matching row, or None if no match is found

# checks the user's password, if it matches return true, else return false
#Parameters: String, String, with them being the username and password respectively
def checkPass(user, p):
    db = get_db()
    c = db.cursor()
    expected_password = c.execute("SELECT password FROM users WHERE username =  ?", (user,)).fetchone()[0]
    actual_password = hashlib.sha256(p.encode()).hexdigest()

    print("expected", expected_password, "actual", actual_password)
    return expected_password == actual_password

# Gets a list of all memes
def getAllMemes():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT id, image, upvotes, creatingUsername FROM memes")
    return c.fetchall()

# Deletes a meme, helper function only DO NOT CALL OUTSIDE
def deleteMeme(id):
    db = get_db()
    c = db.cursor()
    c.execute("DELETE FROM memes WHERE id = ?", (id,))
    exportMemes()
    db.commit()

# Deletes a user, returns false if user doesn't exist
#Parameters: String, which is the username
def deleteUser(user):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT username FROM users WHERE username= ?",(user,))
    if c.fetchone() is None:
        return False
    c.execute("SELECT * FROM memes WHERE creatingUsername = ?", (user,))
    allMemes = [row[0] for row in c.fetchall()]
    for meme in allMemes:
        deleteMeme(meme)
    c.execute("DELETE FROM users WHERE username = ?",(user,))
    exportUsers()
    db.commit()
    return True

#upvotes a meme, returns false if meme doesnt exist
#parameters: integer which is the meme id
def upvote(id):
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM memes WHERE id = ?", (id,))
    if c.fetchone() is None:
        return False
    else:
        c.execute("UPDATE memes SET upvotes = upvotes + 1 WHERE id = ?", (id,))
        db.commit()
        return True

def getRandomImage():
    # Read API key from file
    with open('app/keys/key_RandomImage.txt', 'r') as file:
        key = file.read().strip()

    api_url = f'https://api.api-ninjas.com/v1/randomimage?category=wildlife'

    response = requests.get(api_url, headers={'X-Api-Key': key})

    # Check if the response was successful
    if response.status_code == 200:
        image_url = response.text
        return image_url
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


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

def exportMemes():
    exportToCSV("SELECT * FROM memes", 'memes.csv')




#COMMENT THIS OUT LATER WHEN FINAL PRODUCT
#if os.path.exists("user.db"):
#    os.remove("user.db")





makeDb()

# Example usage
image_url = getRandomImage()
if image_url:
    # print(f"data:image/jpeg;base64, {image_url}")
    pass
else:
    print("Failed to get a random image URL.")



db.close()

