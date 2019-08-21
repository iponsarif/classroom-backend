from flask import Flask, request, json, jsonify

from src.utils.crypt import encrypt, decrypt
from src.utils.file import readFile, writeFile
from src.utils.authorization import encode, decode, verify

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# file locations -----------------
usersFileLocation = 'src/data/users-file.json'
classesFileLocation = 'src/data/classes-file.json'
classworksFileLocation = 'src/data/classworks-file.json'

# routes -------------------------
@app.route('/')
def testConnection():
    return "connected"

@app.route('/register', methods=["POST"])
def register():
    response = {}
    response["message"] = ""

    body = request.json
    
    usersData = readFile(usersFileLocation)
    usernameOrEmailUsed = False
    for user in usersData:
        if user["username"] == body["username"] or user["email"] == body["email"]:
            usernameOrEmailUsed = True
            response["message"] = "Register failed. Username or Email is already used"

    if not usernameOrEmailUsed:
        body["classes_as_student"] = []
        body["classes_as_teacher"] = []
        body["password"] = encrypt(body["password"])
        usersData.append(body)

        writeFile(usersFileLocation, usersData)
        
        response["message"] = "Register successful"


    response["data"] = body
    del response["data"]["password"]
    return jsonify(response)

@app.route('/login', methods=["POST"])
def login():
    response = {}
    response["message"] = "Login failed. Username or password is wrong"
    response["data"] = {}

    body = request.json

    usersData = readFile(usersFileLocation)
    for user in usersData:
        if user["username"] == body["username"]:
            if decrypt(user["password"]) == body["password"]:
                response["message"] = "Login success, welcome {}".format(user["fullname"])
                response["data"] = user
                response["token"] = encode(response["data"]["username"])
                del response["data"]["password"]
            break

    return jsonify(response)

@app.route('/users', methods=["GET"])
def getAllUsers():
    usersData = readFile(usersFileLocation)

    return jsonify(usersData)

@app.route('/users/<int:id>', methods=["GET", "PUT"])
@verify
def getUpdateUser(id):
    if request.method == "GET":
        return getUser(id)
    elif request.method == "PUT":
        return updateUser(id)

def getUser(id):
    response = {}
    response["message"] = "User ID {} is not found".format(id)
    response["data"] = {}

    usersData = readFile(usersFileLocation)

    for user in usersData:
        if user["userid"] == id:
            response["message"] = "User Found"
            response["data"] = user
            break

    
    return jsonify(response)

def updateUser(id):
    body = request.json

    usersData = readFile(usersFileLocation)

    for user in usersData:
        if user["userid"] == id: # kalau user yang mau diupdate ketemu
            user["username"] = body["username"]
            user["password"] = body["password"]
            user["fullname"] = body["fullname"]
            user["email"] = body["email"]
            break

    writeFile(usersFileLocation, usersData)

    userData = getUser(id)
    return userData

@app.route('/class', methods=["POST"])
def createClass():
    body = request.json
    body["students"] = []
    body["classworks"] = []
    
    response = {}
    response["message"] = "Create Class Success"
    response["data"] = {}

    classesData = readFile(classesFileLocation)

    # check class id apakah sudah ada
    classidAlreadyExist = False
    for class_ in classesData:
        if class_["classid"] == body["classid"]:
            response["message"] = "Class ID {} is already exist".format(body["classid"])
            classidAlreadyExist = True
            break

    if not classidAlreadyExist:
        classesData.append(body)
        writeFile(classesFileLocation, classesData)

        usersData = readFile(usersFileLocation)
        for user in usersData:
            if user["userid"] == body["teacher"]:
                user["classes_as_teacher"].append(body["classid"])
        
        writeFile(usersFileLocation, usersData)

        response["data"] = body

    return jsonify(response)

@app.route('/class/<int:id>', methods=["GET", "PUT"])
def getUpdateClass(id):
    if request.method == "GET":
        return getClass(id)
    elif request.method == "PUT":
        return updateClass(id)

def getClass(id):
    response = {}
    response["message"] = "Class with classid {} is not found.".format(id)
    response["data"] = {}
    
    # nyari kelasnya
    classesData = readFile(classesFileLocation)
    classData = {}
    classFound = False
    for class_ in classesData:
        if class_["classid"] == id:
            classData = class_
            response["message"] = "Get Class Success"
            classFound = True
            break

    if classFound:
        classData["students"] = []
        classData["classworks"] = []

        # nyari muridnya
        usersData = readFile(usersFileLocation)
        for user in usersData:
            if id in user["classes_as_student"]:
                classData["students"].append(user["fullname"])
        
        
        # nyari classworknya
        classworksData = readFile(classworksFileLocation)
        for classwork in classworksData:
            if classwork["classid"] == id:
                classData["classworks"].append(classwork)

        response["data"] = classData

    return jsonify(response)

def updateClass(id):
    body = request.json

    classesData = readFile(classesFileLocation)

    for class_ in classesData:
        if class_["classid"] == id: # kalau user yang mau diupdate ketemu
            class_["classname"] = body["classname"]
            break

    writeFile(classesFileLocation, classesData)

    classData = getClass(id)
    return classData

@app.route('/classes', methods=["GET"])
def getAllClasses():
    classesData = readFile(classesFileLocation)

    return jsonify(classesData)

# ikut kelas sebagai student
@app.route('/joinClass', methods=["POST"])
def joinClass():
    body = request.json
 
    # nambahin userid ke classes-file
    classesData = readFile(classesFileLocation)

    for class_ in classesData:
        if class_["classid"] == body["classid"]: # kalau kelasnya ketemu
            if body["userid"] not in class_["students"]: # kalau belum join ke kelas ini sebelumnya
                class_["students"].append(body["userid"])
                break
    
    writeFile(classesFileLocation, classesData)

    # nambahin classid ke users-file
    usersData = readFile(usersFileLocation)

    for user in usersData:
        if user["userid"] == body["userid"]:
            if body["classid"] not in user["classes_as_student"]:
                user["classes_as_student"].append(body["classid"])
                break
    
    writeFile(usersFileLocation, usersData)

    # return data user setelah join
    thisClass = getClass(body["classid"])
    return thisClass

@app.route('/classwork', methods=["POST"])
def createClasswork():
    classworksData = readFile(classworksFileLocation)

    body = request.json
    body["answers"] = []

    classworksData.append(body)

    writeFile(classworksFileLocation, classworksData)

    classesData = readFile(classesFileLocation)

    for class_ in classesData:
        if class_["classid"] == body["classid"]:
            class_["classworks"].append(body["classworkid"])
    
    writeFile(classesFileLocation, classesData)

    return jsonify(body)

@app.route('/classwork/<int:id>', methods=["GET", "POST", "PUT", "DELETE"])
def getAssignUpdateDeleteClasswork(id):
    if request.method == "GET":
        return getClasswork(id)
    elif request.method == "POST":
        return assignClasswork(id)
    elif request.method == "PUT":
        return updateClasswork(id)
    elif request.method == "DELETE":
        return deleteClasswork(id)

def getClasswork(id):
    classworksData = readFile(classworksFileLocation)

    for classwork in classworksData:
        if classwork["classworkid"] == id:
            return jsonify(classwork)

    return "classwork ID {} is not found".format(id)

def assignClasswork(id):
    body = request.json

    classworksData = readFile(classworksFileLocation)

    studentAnswerFound = False
    for classwork in classworksData:
        if classwork["classworkid"] == id: # kalau ketemu classworknya
            for answer in classwork["answers"]: # cari apakah student udah pernah assign sebelumnya
                if answer["userid"] == body["userid"]: # kalau udah pernah assign, ganti answernya aja
                    answer["answer"] = body["answer"]
                    studentAnswerFound = True # jawaban student ketemu (pernah assign), break
                    break
            if not studentAnswerFound: # kalau student belum pernah assign
                classwork["answers"].append(body) # append ke answers
            break
    
    writeFile(classworksFileLocation, classworksData)

    thisClasswork = getClasswork(id) 
    return thisClasswork 

# update classwork hanya ganti question
def updateClasswork(id):
    body = request.json

    classworksData = readFile(classworksFileLocation)

    for classwork in classworksData:
        if classwork["classworkid"] == id:
            classwork["question"] = body["question"]

    writeFile(classworksFileLocation, classworksData)

    thisClasswork = getClasswork(id)
    return thisClasswork 

def deleteClasswork(id):
    ## delete di file classwork 
    classworksData = readFile(classworksFileLocation)
    for i in range(len(classworksData)):
        if classworksData[i]["classworkid"] == id:
            del classworksData[i] # hapus classwork
            break

    writeFile(classworksFileLocation, classworksData)

    ## delete classwork di class
    classesData = readFile('./classes-flie.json')
    for class_ in classesData:
        if id in class_["classworks"]:
            class_["classworks"].remove(id)
            break

    writeFile(classesFileLocation, classesData)

    return "Classwork ID {} has been deleted".format(id)

@app.route('/class/<int:id>/out', methods=["POST"])
def outFromClass(id):
    body = request.json

    # hapus student di kelas
    classesData = readFile(classesFileLocation)
    for class_ in classesData:
        if class_["classid"] == id:
            if body["userid"] in class_["students"]:
                class_["students"].remove(body["userid"])
                writeFile(classesFileLocation, classesData)
            else:
                return "User ID {} tidak ada di Class ID {}".format(body["userid"], id)
            break


    # hapus kelas di student
    usersData = readFile(usersFileLocation)
    for user in usersData:
        if user["userid"] == body["userid"]:
            user["classes_as_student"].remove(id)
            writeFile(usersFileLocation, usersData)
            break
    
    thisUser = getUser(body["userid"])
    return thisUser

@app.errorhandler(404)
def error404(e):
    messages = {
        "message": "The requested URL {} was not found in this server".format(request.path)
    }
    return jsonify(messages), 404

@app.errorhandler(401)
def error401(e):
    messages = {
        "message": "Token Invalid."
    }
    return jsonify(messages), 401

@app.errorhandler(403)
def error403(e):
    messages = {
        "message": str(e)
    }
    return jsonify(messages), 403