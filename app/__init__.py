
import sqlite3
from flask import Flask, render_template, session, request, redirect, url_for
#from db import makeDb, addUser, getPass, changeBalance



def get_db():
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    return db

def addUser(username, password):
    db = get_db()
    c = db.cursor()
    existing_users = c.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if existing_users is not None:
        return False  # Username already exists

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    db.commit()

    return True

@app.route("/", methods=['GET', 'POST'])
def home():
    if 'username' in session:
        return redirect(url_for('homepage'))
    return render_template("login.html")

@app.route("/game", methods=['GET', 'POST'])
def game():
    if 'username' in session:
        return redirect(url_for('game'))
       flash("Please login first", "error")
    return render_template("homepage.html")
    

def checkPass(user, p):
    db = get_db()
    c = db.cursor()
    expected_password = c.execute("SELECT password FROM users WHERE username =  ?", (user,)).fetchone()[0]
    actual_password = hashlib.sha256(p.encode()).hexdigest()

    print("expected", expected_password, "actual", actual_password)
    return expected_password == actual_password

@app.route("/auth", methods=['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    success = checkPass(username, password)

    if success:
        session['username'] = username
        redirect(url_for('homepage'))

    flash("Wrong password!", "error")
    return redirect(url_for("homepage"))

@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html')
app = Flask(__name__)  # Initialize the Flask app
app.secret_key = key.key()
