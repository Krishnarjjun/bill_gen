from flask import Flask, request, jsonify
# from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
@app.route('/')
def index():    
    return "Welcome to the Flask API!"


if __name__ == '__main__':
    app.run(debug=True) 