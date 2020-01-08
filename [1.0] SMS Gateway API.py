import pymongo, pprint, time, os
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import MongoClient
from flask import Flask, jsonify, request, abort, make_response, redirect, url_for
import json, bson

mongodb_host = os.environ.get('MONGO_HOST', 'localhost')
mongodb_port = int(os.environ.get('MONGO_PORT', '27017'))
myclient = MongoClient(mongodb_host, mongodb_port)
mydb = myclient["testdb"]
numcol = mydb["number"]
smscol = mydb["sms"]
globe = mydb["globe"]
smart = mydb["smart"]
simGlobe = mydb["simGlobe"]
simSmart = mydb["simSmart"]

def serial(dct):
    for k in dct:
        if isinstance(dct[k], bson.ObjectId):
            dct[k] = str(dct[k])
    return dct

app = Flask(__name__)

"""///TEST LOG IN PAGE///"""
@app.route('/test1/login')
def login():
    return ("Log in")

@app.route('/test1/sms', methods=['GET'])
def get_sms():
    if smscol.count_documents({}) == 0:
        return ("No message available.")
    else:
        for x in smscol.find():
           if smscol.find() is None:
               return jsonify({"Messages": " Empty"})
           else:
               sms = [serial(item) for item in smscol.find()]
               smart1 = [serial(item1) for item1 in smart.find()]
               globe1 = [serial(item1) for item1 in globe.find()]
               return jsonify({'Messages': sms}, {"Smart": smart1}, {"Globe": globe1})

@app.route('/test1/sms/globe', methods=['GET'])
def get_smsGlobe():
    if globe.count_documents({}) == 0:
        return ("No message available.")
    else:
        for x in globe.find():
           if globe.find() is None:
               return jsonify({"Messages": " Empty"})
           else:
               sms = [serial(item) for item in globe.find()]
               return jsonify({'Messages': sms})
  
            
@app.route('/test1/sms/smart', methods=['GET'])
def get_smsSmart():
    if smart.count_documents({}) == 0:
        return ("No message available.")
    else:
        for x in smart.find():
           if smart.find() is None:
               return jsonify({"Messages": " Empty"})
           else:
               sms = [serial(item) for item in smart.find()]
               return jsonify({'Messages': sms})
  
@app.route('/test1/sms', methods=['DELETE'])
def del_sms():

    del_sms = request.get_json()
    smscol.delete_one(del_sms)
    return redirect(url_for('get_sms'))

@app.route('/test1/sms', methods=['POST'])
def send_sms():
    cur_time = datetime.now()
    if len(request.json['Receiver']) == 12:
        sms = {"Sender":request.json["Sender"],
               "Receiver":request.json["Receiver"],
               "Message":request.json["Message"],
               "Status": "Pending",
               "Date": cur_time
               }
        c = request.json['Receiver']
        cd = c[0:5]
        for x in simSmart.find({"prefix": cd}):
            y = smart.insert_one(sms)
            return jsonify({"Result":"Message Added to Pending. (Smart)"})
        for x1 in simGlobe.find({"prefix": cd}):
            y1 = globe.insert_one(sms)
            return jsonify({"Globe":"Message Added to Pending. (Globe)"})
    else:
        return jsonify({"Result":"Invalid Number."})

"""//DISPLAY CONTACTS//"""
@app.route('/test1/contacts', methods=['GET'])
def get_contacts():
   xy = numcol.count_documents({})
   if xy == 0:
       return ("Contacts empty.")
   else:
       for x in numcol.find():
        print(x)
        data = [serial(item) for item in numcol.find()]
        return jsonify({'Contacts': data})
    
"""///ADD CONTACT///"""

@app.route('/test1/contacts', methods=['POST'])
def add_contact():
    if (request.json["Number"]) == 12: 
        req_cont = {"Name":request.json["Name"],
                    "Number":request.json["Number"]
                    }
        numcol.insert_one(req_cont)
        return jsonify({"Result":"Contact Added"}),201
    else:
        return jsonify({"Invalid Number"})
    
    
"""req_data = request.get_json()
    numcol.insert_one(req_data).inserted_id
    return ({'result':True}), 201"""

"""///DELETE CONTACT///"""
@app.route('/test1/contacts', methods=['DELETE'])
def del_contact():

    del_cont = request.get_json()
    numcol.delete_one(del_cont)
    return redirect(url_for('get_contacts'))

@app.route('/test1/reports', methods=['GET'])
def get_reports():
    cur_time = datetime.now()
    get_sentGlobe = globe.count_documents({"Status":"Processed"})
    get_sentSmart = smart.count_documents({"Status":"Processed"})
    get_pendingGlobe = globe.count_documents({"Status":"Pending"})
    get_pendingSmart = smart.count_documents({"Status":"Pending"})
    return jsonify({"Sent Globe messages": get_sentGlobe,
                   "Unsent Globe messages": get_pendingGlobe,
                    "Sent Smart messages": get_sentSmart,
                    "Unsent Smart messages": get_pendingSmart,
                    "Time": cur_time})
    

if __name__ == '__main__':

    app.run(host='192.168.0.98')
