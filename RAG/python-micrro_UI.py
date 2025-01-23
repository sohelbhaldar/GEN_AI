from flask import Flask, jsonify, render_template, request
from flask_httpauth import HTTPBasicAuth
import os

# Initialize Flask app and basic auth
app = Flask(__name__)
auth = HTTPBasicAuth()

# Sample user data (this could be fetched from a database in a real app)
users = {
    "user1": "password1",
    "user2": "password2",
}

# Verify username and password
@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username
    return None

# Serve the login page
@app.route('/')
def index():
    return render_template('index.html')

# Protected endpoint (Authentication required)
@app.route('/protected')
@auth.login_required
def protected():
    return jsonify(message=f"Hello, {auth.current_user()}! You have accessed a protected endpoint."), 200

if __name__ == '__main__':
    app.run(debug=True)
