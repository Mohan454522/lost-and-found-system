from flask import Flask, render_template
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'terraform-production-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///lost_found.db')

# Simple route to test
@app.route('/')
def home():
    return "Lost & Found System - Hello World! Deployment Successful!"

@app.route('/health')
def health():
    return "OK", 200

# Remove these lines
#if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0', port=5000)