from flask import Flask, request, json, jsonify
import os

app = Flask(__name__)

@app.route('/')
def testConnection():
    return "connected"

@app.route('/register', methods=["POST"])
def register():
    userData = []

    # kalau file users-file.json udah ada, di read dulu. kalau file ga ada, ga usah di read, langsung write
    if os.path.exists('./users-file.json'):
        userFile = open('./users-file.json', 'r')
        userData = json.load(userFile)

    body = request.json
    userData.append(body)

    # siapin file buat di write
    userFile = open('./users-file.json', 'w')
    userFile.write(json.dumps(userData))

    return jsonify(userData)

@app.route('/login', methods=["POST"])
def login():
    body = request.json

    # siapin file buat di read
    userFile = open('./users-file.json', 'r')
    userData = json.load(userFile)

    for user in userData:
        if body["username"] == user["username"]:
            if body["password"] == user["password"]:
                return "Login succes, welcome {}".format(user["fullname"])
            else:
                return "Login failed. Wrong password"
    
    return "Login failed. Username is not found"

@app.route('/users/<int:id>', methods=["GET"])
def getUser(id):
    # siapin file buat di read
    userFile = open('./users-file.json', 'r')
    userData = json.load(userFile)

    for user in userData:
        if id == user["userid"]:
            return jsonify(user)

    return "User ID {} is not found".format(id)

@app.route('/class', methods=["POST"])
def createClass():
    classesData = []

    if os.path.exists('./classes-file.json'):
        classesFile = open('./classes-file.json', 'r')
        classesData = json.load(classesFile)

    body = request.json
    classesData.append(body)

    # siapin file buat di write
    classesFile = open('./classes-file.json', 'w')
    classesFile.write(json.dumps(classesData))

    return jsonify(classesData)

@app.route('/class/<int:id>', methods=["GET"])
def getClass(id):
    # siapin file buat di read
    classesFile = open('./classes-file.json', 'r')
    classesData = json.load(classesFile)

    for class_ in classesData:
        if id == class_["classid"]:
            return jsonify(class_)

    return "User ID {} is not found".format(id)

