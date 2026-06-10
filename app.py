from flask import Flask

# Create a Flask application
app = Flask(__name__)

# Define the route for the homepage
@app.route('/')
def hello():
    return "Hello Freddie Mac from Flask and Oisin!"

# Run the application if this script is executed directly
if __name__ == '__main__':
    # Must bind to 0.0.0.0 (all interfaces) and port 8050 for proxies to work
    app.run(host='0.0.0.0', port=8050, debug=True)
