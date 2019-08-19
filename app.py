from flask import Flask, request, json, jsonify
import os

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# ------------------ functions --------------------------------------
def readFile(filePath):
    thisData = []
    # kalau file *.json udah ada, di read. kalau file ga ada, return list kosong
    if os.path.exists(filePath) and os.path.getsize(filePath) > 0: # dan kalau isi filenya tidak kosong banget
        thisFile = open(filePath, 'r')
        thisData = json.load(thisFile)
        thisFile.close()
    
    return thisData

def writeFile(filePath, data):
    thisFile = open(filePath, 'w')
    thisFile.write(json.dumps(data))
    thisFile.close()

# ------------------ routes -----------------------------------------
@app.route('/')
def testConnection():
    return "connected"

@app.route('/register', methods=["POST"])
def register():
    response = {}
    
    usersData = readFile('./users-file.json')

    body = request.json
    body["classes_as_student"] = []
    body["classes_as_teacher"] = []
    usersData.append(body)

    writeFile('./users-file.json', usersData)

    response["message"] = "Register successful"
    response["data"] = body
    return jsonify(response)

@app.route('/login', methods=["POST"])
def login():
    response = {}
    response["message"] = "Login failed. Username or password is wrong"
    response["data"] = {}

    body = request.json

    usersData = readFile('./users-file.json')

    for user in usersData:
        if user["username"] == body["username"]:
            if user["password"] == body["password"]:
                response["message"] = "Login succes, welcome {}".format(user["fullname"])
                response["data"] = user
            break
    
    return jsonify(response)

@app.route('/users/<int:id>', methods=["GET"])
def getUser(id):
    response = {}
    response["message"] = "User ID {} is not found".format(id)
    response["data"] = {}

    usersData = readFile('./users-file.json')

    for user in usersData:
        if user["userid"] == id:
            response["message"] = "User Found"
            response["data"] = user
            break

    return jsonify(response)

@app.route('/users', methods=["GET"])
def getAllUsers():
    usersData = readFile('./users-file.json')

    return jsonify(usersData)

@app.route('/class', methods=["POST"])
def createClass():
    body = request.json
    body["students"] = []
    body["classworks"] = []
    
    response = {}
    response["message"] = "Create Class Success"
    response["data"] = {}

    classesData = readFile('./classes-file.json')

    # check class id apakah sudah ada
    classidAlreadyExist = False
    for class_ in classesData:
        if class_["classid"] == body["classid"]:
            response["message"] = "Class ID {} is already exist".format(body["classid"])
            classidAlreadyExist = True
            break

    if not classidAlreadyExist:
        classesData.append(body)
        writeFile('./classes-file.json', classesData)

        usersData = readFile('./users-file.json')
        for user in usersData:
            if user["userid"] == body["teacher"]:
                user["classes_as_teacher"].append(body["classid"])
        
        writeFile('./users-file.json', usersData)

        response["data"] = body

    return jsonify(response)

@app.route('/class/<int:id>', methods=["GET"])
def getClass(id):
    response = {}
    response["message"] = "Class with classid {} is not found.".format(id)
    response["data"] = {}
    
    # nyari kelasnya
    classesData = readFile('./classes-file.json')
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
        usersData = readFile('./users-file.json')
        for user in usersData:
            if id in user["classes_as_student"]:
                classData["students"].append(user["fullname"])
        
        
        # nyari classworknya
        classworksData = readFile('./classworks-file.json')
        for classwork in classworksData:
            if classwork["classid"] == id:
                classData["classworks"].append(classwork)

        response["data"] = classData

    return jsonify(response)

@app.route('/classes', methods=["GET"])
def getAllClasses():
    classesData = readFile('./classes-file.json')

    return jsonify(classesData)

# ikut kelas sebagai student
@app.route('/joinClass', methods=["POST"])
def joinClass():
    body = request.json
 
    # nambahin userid ke classes-file
    classesData = readFile('./classes-file.json')

    for class_ in classesData:
        if class_["classid"] == body["classid"]: # kalau kelasnya ketemu
            if body["userid"] not in class_["students"]: # kalau belum join ke kelas ini sebelumnya
                class_["students"].append(body["userid"])
                break
    
    writeFile('./classes-file.json', classesData)

    # nambahin classid ke users-file
    usersData = readFile('./users-file.json')

    for user in usersData:
        if user["userid"] == body["userid"]:
            if body["classid"] not in user["classes_as_student"]:
                user["classes_as_student"].append(body["classid"])
                break
    
    writeFile('./users-file.json', usersData)

    # return data user setelah join
    thisClass = getClass(body["classid"])
    return thisClass

@app.route('/users/<int:id>', methods=["PUT"])
def updateUser(id):
    body = request.json

    usersData = readFile('./users-file.json')

    for user in usersData:
        if user["userid"] == id: # kalau user yang mau diupdate ketemu
            user["username"] = body["username"]
            user["password"] = body["password"]
            user["fullname"] = body["fullname"]
            user["email"] = body["email"]
            break

    writeFile('./users-file.json', usersData)

    userData = getUser(id)
    return userData

@app.route('/class/<int:id>', methods=["PUT"])
def updateClass(id):
    body = request.json

    classesData = readFile('./classes-file.json')

    for class_ in classesData:
        if class_["classid"] == id: # kalau user yang mau diupdate ketemu
            class_["classname"] = body["classname"]
            break

    writeFile('./classes-file.json', classesData)

    classData = getClass(id)
    return classData

@app.route('/classwork', methods=["POST"])
def createClasswork():
    classworksData = readFile('./classworks-file.json')

    body = request.json
    body["answers"] = []

    classworksData.append(body)

    writeFile('./classworks-file.json', classworksData)

    classesData = readFile('./classes-file.json')

    for class_ in classesData:
        if class_["classid"] == body["classid"]:
            class_["classworks"].append(body["classworkid"])
    
    writeFile('./classes-file.json', classesData)

    return jsonify(body)

@app.route('/classwork/<int:id>', methods=["GET"])
def getClasswork(id):
    classworksData = readFile('./classworks-file.json')

    for classwork in classworksData:
        if classwork["classworkid"] == id:
            return jsonify(classwork)

    return "classwork ID {} is not found".format(id)

@app.route('/classwork/<int:id>', methods=["POST", "PUT"]) 
def assignClasswork(id):
    body = request.json

    classworksData = readFile('./classworks-file.json')

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
    
    writeFile('./classworks-file.json', classworksData)

    thisClasswork = getClasswork(id) 
    return thisClasswork 

# update classwork hanya ganti question
@app.route('/classwork/<int:id>', methods=["PUT"])
def updateClasswork(id):
    body = request.json

    classworksData = readFile('./classworks-file.json')

    for classwork in classworksData:
        if classwork["classworkid"] == id:
            classwork["question"] = body["question"]

    writeFile('./classworks-file.json', classworksData)

    thisClasswork = getClasswork(id)
    return thisClasswork 

@app.route('/class/<int:id>/out', methods=["POST"])
def outFromClass(id):
    body = request.json

    # hapus student di kelas
    classesData = readFile('./classes-file.json')
    for class_ in classesData:
        if class_["classid"] == id:
            if body["userid"] in class_["students"]:
                class_["students"].remove(body["userid"])
                writeFile('./classes-file.json', classesData)
            else:
                return "User ID {} tidak ada di Class ID {}".format(body["userid"], id)
            break


    # hapus kelas di student
    usersData = readFile('./users-file.json')
    for user in usersData:
        if user["userid"] == body["userid"]:
            user["classes_as_student"].remove(id)
            writeFile('./users-file.json', usersData)
            break
    
    thisUser = getUser(body["userid"])
    return thisUser

# @app.route('/class/<int:id>', methods=["DELETE"])
# def deleteClass(id):
#     classesData = readFile('./classes-file.json')

@app.route('/classwork/<int:id>', methods=["DELETE"])
def deleteClasswork(id):
    ## delete di file classwork 
    classworksData = readFile('./classworks-file.json')
    for i in range(len(classworksData)):
        if classworksData[i]["classworkid"] == id:
            del classworksData[i] # hapus classwork
            break

    writeFile('./classworks-file.json', classworksData)

    ## delete classwork di class
    classesData = readFile('./classes-flie.json')
    print(classesData)
    for class_ in classesData:
        if id in class_["classworks"]:
            class_["classworks"].remove(id)
            break

    writeFile('./classes-file.json', classesData)

    return "Classwork ID {} has been deleted".format(id)

@app.errorhandler(404)
def error404(e):
    messages = {
        "message": "URL nya ga ada coy"
    }
    return jsonify(messages), 404