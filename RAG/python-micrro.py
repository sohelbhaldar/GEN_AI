from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth

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
    
# Public endpoint (No authentication required)
@app.route('/')
def home():
    return jsonify(message="Welcome to the public endpoint. Please log in to access protected resources."), 200

# Protected endpoint (Authentication required)
@app.route('/protected')
@auth.login_required
def protected():
    return jsonify(message=f"Hello, {auth.current_user()}! You have accessed a protected endpoint."), 200

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
