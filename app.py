# app.py
import os
from flask import Flask, jsonify, render_template
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Home route with HTML template rendering
@app.route('/')
def hello():
    app.logger.info("Home route accessed")
    return render_template('index.html')

# Example API route that returns JSON
@app.route('/api/greet', methods=['GET'])
def greet():
    app.logger.info("Greet API accessed")
    return jsonify(message="Hello from Docker and Kubernetes!")

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

# Load configuration from environment variables (if any)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
