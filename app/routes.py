from flask import Blueprint, jsonify, request

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return jsonify({"message": "Welcome to Flask!"})

@main.route('/api/greet', methods=['POST'])
def greet():
    data = request.get_json()
    name = data.get('name', 'Guest')
    return jsonify({"message": f"Hello, {name}!"})
