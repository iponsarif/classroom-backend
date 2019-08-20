from flask import json
import os

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