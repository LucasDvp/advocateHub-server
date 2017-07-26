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
mongoClient = MongoClient('localhost', 27017)
# mongoClient = MongoClient('40.83.190.18', 27017)
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


@app.route('/user')
def get_user():
    user = open(json_url + '/user.json')
    return response(json.load(user))


@app.route('/advocators')
def get_advocators():
    advocators = open(json_url + '/advocates.json')
    return response(json.load(advocators))

@app.route('/azure/infos')
def get_azureInfos():
    info = open(json_url + '/azureInfos.json')
    return response(json.load(info))


@app.route('/user/login', methods=['POST', 'GET'])
def user_login():
    app.logger.info("User Login Function Dealing...")
    if request.method == 'POST':
        userInfo = request.get_json()
        userId = userInfo['id']
        session['id'] = userId
        advocator = advocators.find_one({"id": userId})
        if advocator:
            print(userInfo)
            advocators.update_one({'id': userId}, {'$set': userInfo}, upsert=False)
            return response(True)
        else:
            advocators.insert_one(userInfo)
            return response(True)
    else:
        userId = request.args.get('userId')
        advocator = advocators.find_one({"id": userId})
        if advocator:
            del advocator['_id']
            return response(advocator)
        else:
            return response({}, 404)

@app.route('/user/detail')
def get_userDetail():
    userId = request.args.get('userId')
    advocator = advocators.find_one({"id": userId})
    if advocator:
        del advocator['_id']
        userMeetings = list(meetings.find({"advocatorId": userId}))
        for userMeeting in userMeetings:
            normalizeMongoRecordToDict(userMeeting)
        advocator['meetings'] = userMeetings
        return response(advocator)
    else:
        return response({}, 404)

@app.route('/meetings')
def get_meetings():
    meetingsInfo = list(meetings.find({}))
    for meetingInfo in meetingsInfo:
        normalizeMongoRecordToDict(meetingInfo)
    return response(meetingsInfo)


if __name__ == '__main__':
    app.run(host="10.0.0.4", port=13888)
