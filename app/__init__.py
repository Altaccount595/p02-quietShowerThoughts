from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from game import *
from build_db import makeDb, addUser, checkPass, addGame, getUserGames, getAllGames

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
game_state = {}
makeDb()

@app.route('/')
def homepage():
    """Render the homepage with navigation buttons."""
    return render_template('homepage.html')


@app.route('/play')
def play():
    """Render the game page if the user is logged in, otherwise redirect to login."""
    if 'username' not in session:
        return redirect(url_for('login', error="Please log in to play."))

    # Initialize game state for the user
    state = startGame()  # Now it will correctly reference startGame
    if "error" in state:
        return render_template('game.html', error=state["error"])
    
    game_state[session['username']] = state
    
    # Pass the game state to the template
    return render_template('game.html', gameState=game_state[session['username']], target_hint="Guess the country!")





@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if checkPass(username, password):  # Validate credentials
            session['username'] = username
            return redirect(url_for('homepage'))
        else:
            return render_template('login.html', error="Invalid credentials.")

    error = request.args.get('error')
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if addUser(username, password):  # Add user to the database
            return redirect(url_for('homepage'))
        else:
            return render_template('register.html', error="Username already taken or invalid input.")

    return render_template('register.html')

@app.route('/scores')
def scores():
    """Render the scores page."""
    if 'username' not in session:
        return redirect(url_for('login', error="Please log in to view scores."))
    user_games = getUserGames(session['username'])
    return render_template('scores.html', games=user_games)

@app.route('/guess', methods=['POST'])
def guess():
    """Handle the user's guess and return the result."""
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    # Get the guess from the form data
    user_guess = request.form.get('guess')

    if not user_guess:
        return jsonify({"error": "No guess provided"}), 400

    game_state_for_user = game_state.get(session['username'])
    if not game_state_for_user:
        return jsonify({"error": "Game state not found"}), 404

    result = processGuess(game_state_for_user, user_guess)

    # Update the game state for the user
    game_state[session['username']] = game_state_for_user

    # If the guess was correct, return the success message
    return render_template('game.html', message=result['message'], gameState=game_state_for_user)


@app.route('/reset', methods=['POST'])
def reset():
    """Reset the game with a new target country."""
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    guesser.reset_game()
    return jsonify({"message": "Game reset successfully"})


@app.route('/logout')
def logout():
    """Log out the user and redirect to the homepage."""
    session.pop('username', None)
    return redirect(url_for('homepage'))

@app.route('/save_game', methods=['POST'])
def save_game():
    """Save the current game's guesses to the database."""
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    guesses = data.get('guesses')

    if not guesses or not isinstance(guesses, list):
        return jsonify({"error": "Invalid game data."}), 400

    if addGame(guesses, session['username']):
        return jsonify({"message": "Game saved successfully."})
    return jsonify({"error": "Failed to save game."}), 500

@app.route('/all_games')
def all_games():
    """Get all games (debug purposes)."""
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 403

    games = getAllGames()
    return jsonify(games)

if __name__ == '__main__':
    app.run(debug=True)

