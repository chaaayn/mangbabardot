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

testcount = 0

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

   for x in smscol.find():
       if x is None:
           return jsonify({"Messages": " Empty"})
       else:
           sms = [serial(item) for item in smscol.find()]
           return jsonify({'Messages': sms})
    
@app.route('/test1/sms', methods=['DELETE'])
def del_sms():

    del_sms = request.get_json()
    smscol.delete_one(del_sms)
    return redirect(url_for('get_sms'))
    
@app.route('/test1/sendsms', methods=['POST'])
def send_sms():
    cur_time = datetime.now()
    sms = {"Sender":request.json["Sender"],
           "Receiver":request.json["Receiver"],
           "Message":request.json["Message"],
           "Status": "Pending",
           "Date": cur_time
           }
    
    y = smscol.insert_one(sms)
    return jsonify({"Result":"Message Added to Pending."})

"""//DISPLAY CONTACTS//"""
@app.route('/test1/contacts', methods=['GET'])
def get_contacts():
   """ contacts = numcol.find()
    response = ["Contacts"]
    for contact in contacts:
        contact['_id'] = str(contact['_id'])
        response.append(contact) 
   return jsonify(response)"""
   """contactlist = mydb.numcol.countDocuments({})
   if contactlist == 0:
       return ("Contacts empty.")
   elif contactlist >= 1:"""
   for x in numcol.find():
        print(x)
        data = [serial(item) for item in numcol.find()]
        return jsonify({'Contacts': data})
    
"""///ADD CONTACT///"""

@app.route('/test1/contacts', methods=['POST'])
def add_contact():
    
    req_cont = {"Name":request.json["Name"],
                "Number":request.json["Number"]
                }
    numcol.insert_one(req_cont)
    return jsonify({"Result":"Contact Added"}),201
    
    
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
    get_sent = smscol.count_documents({"Status":"Processed"})
    get_pending = smscol.count_documents({"Status":"Pending"})
    return jsonify({"Sent messages ": get_sent,
                   "Unsent messages": get_pending})
    

if __name__ == '__main__':

    app.run(debug=True)
