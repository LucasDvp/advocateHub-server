from flask import Flask, json, session
from flask import request
from flask import make_response
from flask_cors import CORS
from bson import json_util
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
from datetime import timezone
import time
import os

app = Flask(__name__)
CORS(app)
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "templates")
app.secret_key = 'SUPERSECRETEKEYOFMSADVOCATEHUB'

#
# Mongo db related
#
#mongoClient = MongoClient('localhost', 27017)
mongoClient = MongoClient('40.83.190.18', 27017)
db = mongoClient.advocateHub
advocators = db.advocators
meetings = db.meetings


#
# Functions
#

def jd(obj):
    return json_util.dumps(obj)

def normalizeMongoRecordToDict(record):
    for k, v in record.items():
        if type(v) is ObjectId:
            record[k] = str(v)
        elif type(v) is datetime:
            record[k] = int(v.replace(tzinfo=timezone.utc).timestamp()) * 1000

#
# Response
#

def response(data={}, code=200, errorMsg=""):
    resp = {
        "timestamp": int(round(time.time() * 1000)),
        "status": code,
        "data": data,
        "errorMessage": errorMsg
    }
    response = make_response(jd(resp))
    # response.headers['Status Code'] = resp['status']
    response.headers['Content-Type'] = "application/json"
    return response


#
# Error handing
#

@app.errorhandler(404)
def page_not_found(error):
    return response({}, 404)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/advocator/login/<advocatorId>', methods=['GET'])
def get_advocator(advocatorId):
    advocator = advocators.find_one({"id": advocatorId})
    if advocator:
        del advocator['_id']
        return response(advocator)
    else:
        return response({}, 404)

@app.route('/advocators')
def get_advocators():
    advocatorsInfo = list(advocators.find({}))
    for advocatorInfo in advocatorsInfo:
        del advocatorInfo['_id']
    return response(advocatorsInfo)

@app.route('/azure/infos')
def get_azureInfos():
    info = open(json_url + '/azureInfos.json')
    return response(json.load(info))

@app.route('/advocator/login', methods=['POST'])
def advocator_login():
    app.logger.info("Advocator Login Function Dealing...")
    advocatorInfo = request.get_json()
    advocatorId = advocatorInfo['id']
    session['id'] = advocatorId
    advocator = advocators.find_one({"id": advocatorId})
    if advocator:
        del advocator['_id']
        advocators.update_one({'id': advocatorId}, {'$set': advocatorInfo}, upsert=False)
        return response(True)
    else:
        advocators.insert_one(advocatorInfo)
        return response(True)

@app.route('/advocator/<advocatorId>')
def get_advocatorDetail(advocatorId):
    advocator = advocators.find_one({"id": advocatorId})
    if advocator:
        del advocator['_id']
        advocatorMeetings = list(meetings.find({"advocatorId": advocatorId}))
        for advocatorMeeting in advocatorMeetings:
            normalizeMongoRecordToDict(advocatorMeeting)
        advocator['meetings'] = advocatorMeetings
        return response(advocator)
    else:
        return response({}, 404)

@app.route('/meetings')
def get_meetings():
    meetingsInfo = list(meetings.find({}))
    for meetingInfo in meetingsInfo:
        normalizeMongoRecordToDict(meetingInfo)
        advocator = advocators.find_one({"id": meetingInfo['advocatorId']})
        del advocator['_id']
        meetingInfo['advocator'] = advocator
    return response(meetingsInfo)

@app.route('/meeting/create', methods=['POST'])
def meeting_create():
    meetingInfo = request.get_json()
    advocatorId = meetingInfo['advocatorId']
    advocator = advocators.find_one({"id": advocatorId})
    if advocator:
        del meetingInfo['advocator']
        meetingDate = meetingInfo.get['date']
        if meetingDate:
            meetingInfo['date'] = datetime.utcfromtimestamp(meetingDate / 1000.0)
        else:
            meetingInfo['date'] = datetime.utcnow()
        meetingId = meetingInfo.get('_id')
        if meetingId:
            del meetingInfo['_id']
            meetings.update_one({'_id': ObjectId(meetingId)}, {'$set': meetingInfo}, upsert=False)
            return response(True)
        else:
            meetings.insert_one(meetingInfo)
            return response(True)
    else:
        return response({}, 404, "Advocator Not Found")

@app.route('/meeting/<meetingId>', methods=['GET'])
def get_meeting(meetingId):
    if ObjectId.is_valid(meetingId):
        meetingInfo = meetings.find_one({"_id": ObjectId(meetingId)})
        if meetingInfo:
            normalizeMongoRecordToDict(meetingInfo)
            advocator = advocators.find_one({"id": meetingInfo['advocatorId']})
            del advocator['_id']
            meetingInfo['advocator'] = advocator
            return response(meetingInfo)
    return response({}, 404, "Meeting Not Found")


if __name__ == '__main__':
    app.run(host="10.0.0.4", port=13888)
