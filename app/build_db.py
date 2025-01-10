# RACAMOJO -
# SoftDev
# P01
# 2024-12-03
# time spent: 1.5 hrs

import sqlite3
import csv
import os

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
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT NOT NULL UNIQUE, password TEXT NOT NULL)")
    c.execute("CREATE TABLE IF NOT EXISTS memes (id INTEGER PRIMARY KEY AUTOINCREMENT, image TEXT, upvotes INTEGER, creatingUsername TEXT NOT NULL, FOREIGN KEY (creatingUsername) REFERENCES users (username))")
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
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u, p))
        exportUsers()
        db.commit()
        return True

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
    c.execute("SELECT password FROM users WHERE username =  ?",(user,))
    if c.fetchone() is p:
        return True
    else:
        return False

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

db.close()
