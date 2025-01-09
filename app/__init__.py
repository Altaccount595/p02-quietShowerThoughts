
import sqlite3
from flask import Flask, render_template, session, request, redirect, url_for
#from db import makeDb, addUser, getPass, changeBalance


#makeDb()

app = Flask(__name__)  # Initialize the Flask app
app.secret_key = key.key()
