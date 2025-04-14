import os
import logging
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Configure secret key for sessions
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret')

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model for storing user data
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Home route with HTML template rendering
@app.route('/')
def hello():
    app.logger.info("Home route accessed")
    return render_template('index.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hash the password
        hashed_password = generate_password_hash(password, method='sha256')

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            app.logger.error(f"Username {username} already exists.")
            return "Username already exists", 400

        # Create a new user
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        app.logger.info(f"User {username} registered successfully.")
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            # Store the user session
            session['user_id'] = user.id
            app.logger.info(f"User {username} logged in successfully.")
            return redirect(url_for('profile'))
        else:
            app.logger.error(f"Invalid login attempt for {username}.")
            return "Invalid username or password", 401
    
    return render_template('login.html')

# Profile route (only accessible when logged in)
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', username=user.username)

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    app.logger.info("User logged out.")
    return redirect(url_for('login'))

# Health check route
@app.route('/health')
def health_check():
    app.logger.info("Health check route accessed")
    return jsonify(status='Healthy')

# Custom error handling
@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f"Error 404: {error}")
    return jsonify(error="Not found", message=str(error)), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Error 500: {error}")
    return jsonify(error="Internal Server Error", message=str(error)), 500

if __name__ == '__main__':
    # Create the database if it doesn't exist
    db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
