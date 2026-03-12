from flask import Flask, jsonify
app = Flask(__name__)
@app.route('/')
def home():
 return "Welcome to my Flask API!"
@app.route('/student')
def student():
 return jsonify({
 "name": "Charlie Tadlas Goro Jr",
 "grade": 90,
 "section": "Zechariah"
 })
