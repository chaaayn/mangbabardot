import pymongo, pprint, time, os
from datetime import datetime, timedelta
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
msgG = mydb["messagesG"]
msgS = mydb["messagesS"]
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

@app.route('/sms', methods=['GET'])
def get_sms():
    if (smart.count_documents({}) == 0) and (globe.count_documents({}) == 0):
        return ("No message available.")
    else:
        sms = [serial(item) for item in smscol.find()]
        smart1 = [serial(item1) for item1 in smart.find()]
        globe1 = [serial(item1) for item1 in globe.find()]
        return jsonify({"Smart": smart1}, {"Globe": globe1})
    
@app.route('/sms/globe', methods=['GET'])
def get_smsGlobe():
    if globe.count_documents({}) == 0:
        return ("No message available.")
    else:
        for x in globe.find():
           if globe.find() is None:
               return jsonify({"Globe Messages": " Empty"})
           else:
               sms = [serial(item) for item in globe.find()]
               return jsonify({'Globe Messages': sms})
  
            
@app.route('/sms/smart', methods=['GET'])
def get_smsSmart():
    if smart.count_documents({}) == 0:
        return ("No message available.")
    else:
        for x in smart.find():
           if smart.find() is None:
               return jsonify({"Smart Messages": " Empty"})
           else:
               sms = [serial(item) for item in smart.find()]
               return jsonify({'Smart Messages': sms})
  
@app.route('/sms', methods=['DELETE'])
def del_sms():

    del_sms = request.get_json()
    for x in smscol.find(del_sms):
        smscol.delete_one(del_sms)
    for x in smart.find(del_sms):
        smart.delete_one(del_sms)
    for x in globe.find(del_sms):
        globe.delete_one(del_sms)
    return redirect(url_for('get_sms'))

@app.route('/sms', methods=['POST'])
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
            return jsonify({"Result":"Message Added to Pending. (Globe)"})
    else:
        return jsonify({"Result":"Invalid Input. Check again.", "Guide":"Start number with country code. Ex. 63912-345-6789 and Maximum Sender character is 8."})

"""//DISPLAY CONTACTS//"""
@app.route('/contacts', methods=['GET'])
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

@app.route('/contacts', methods=['POST'])
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
@app.route('/contacts', methods=['DELETE'])
def del_contact():

    del_cont = request.get_json()
    numcol.delete_one(del_cont)
    return redirect(url_for('get_contacts'))

@app.route('/reports', methods=['GET'])
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
                    "zTime": cur_time})

@app.route('/reports/smart', methods=['GET'])
def get_reportsS():
    cur_time = datetime.now()
    get_sentSmart = smart.count_documents({"Status":"Processed"})
    get_pendingSmart = smart.count_documents({"Status":"Pending"})
    return jsonify({"Sent Smart messages": get_sentSmart,
                    "Unsent Smart messages": get_pendingSmart,
                    "zTime": cur_time})

@app.route('/reports/smart/today', methods=['GET'])
def get_reportsST():
    cur_time = datetime.now()
    oo1 = datetime.today().replace(hour=23, minute=59, second=59, microsecond = 999999)
    oo2 = datetime.today().replace(hour=0, minute=0, second=0, microsecond = 0)
    get_sentSmart = smart.count_documents({"Status":"Processed","Date":{"$lt": oo1, "$gt": oo2}})
    get_pendingSmart = smart.count_documents({"Status":"Pending"})
    return jsonify({"Sent Smart messages": get_sentSmart,
                    "Unsent Smart messages": get_pendingSmart,
                    "zTime": cur_time})

@app.route('/reports/globe', methods=['GET'])
def get_reportsG():
    cur_time = datetime.now()
    get_sentGlobe = globe.count_documents({"Status":"Processed"})
    get_pendingGlobe = globe.count_documents({"Status":"Pending"})

    return jsonify({"Sent Globe messages": get_sentGlobe,
                   "Unsent Globe messages": get_pendingGlobe,
                    "zTime": cur_time})
@app.route('/reports/globe/today', methods=['GET'])
def get_reportsGT():
    cur_time = datetime.now()
    oo1 = datetime.today().replace(hour=23, minute=59, second=59, microsecond = 999999)
    oo2 = datetime.today().replace(hour=0, minute=0, second=0, microsecond = 0)
    get_sentGlobe = globe.count_documents({"Status":"Processed","Date":{"$lt": oo1, "$gt": oo2}})
    get_pendingGlobe = globe.count_documents({"Status":"Pending"})

    return jsonify({"Sent Globe messages": get_sentGlobe,
                   "Unsent Globe messages": get_pendingGlobe,
                    "zTime": cur_time})

@app.route('/reports/today', methods=['GET'])
def get_reportsT():
    oo = datetime.today()
    oo1 = datetime.today().replace(hour=23, minute=59, second=59, microsecond = 999999)
    oo2 = datetime.today().replace(hour=0, minute=0, second=0, microsecond = 0)
    oo4 = smart.count_documents({"Status":"Processed","Date":{"$lt": oo1, "$gt": oo2}})
    oo6 = globe.count_documents({"Status":"Processed","Date":{"$lt": oo1, "$gt": oo2}})
    oo7 = oo4 + oo6
    return jsonify({"Smart Messages Today":oo4},{"Globe Messages Today":oo6},{"Total messages today":oo7},
                    {"zTime": oo})

@app.route('/reports/month', methods=['GET'])
def get_reportsM():
    oo = datetime.today()
    oo1 = datetime.today().replace(day=31,hour=0, minute=0, second=0, microsecond = 0)
    oo2 = datetime.today().replace(day=1,hour=23, minute=59, second=59, microsecond = 999999)
    oo4 = smart.count_documents({"Date":{"$lt": oo1, "$gt": oo2}})
    oo6 = globe.count_documents({"Date":{"$lt": oo1, "$gt": oo2}})
    oo7 = oo4 + oo6
    return jsonify({"Smart Messages this month":oo4},{"Globe Messages this month":oo6},{"Total messages this week":oo7},
                    {"zTime": oo})

@app.route('/reports/year', methods=['GET'])
def get_reportsY():
    oo = datetime.today()
    oo1 = datetime.today().replace(month=12,day=31,hour=0, minute=0, second=0, microsecond = 0)
    oo2 = datetime.today().replace(month=1,day=1,hour=23, minute=59, second=59, microsecond = 999999)
    oo4 = smart.count_documents({"Date":{"$lt": oo1, "$gt": oo2}})
    oo6 = globe.count_documents({"Date":{"$lt": oo1, "$gt": oo2}})
    oo7 = oo4 + oo6
    return jsonify({"Smart Messages this year":oo4},{"Globe Messages this year":oo6},{"Total messages this year":oo7},
                    {"zTime": oo})

@app.route('/sms/globe/received', methods=['GET'])
def get_GreceivedSMS():
    oo = datetime.today()
    if msgG.count_documents({}) == 0:
        return ("No messages available.")
    else:
        for x in msgG.find():
           if msgG.find() is None:
               return jsonify({"Received Globe Messages": " Empty"})
           else: 
               sms = [serial(item) for item in msgG.find()]           
               return jsonify({'Received Globe Messages': sms},{"zTime": oo}), checkG()
            
@app.route('/sms/globe/received/unread', methods=['GET'])
def get_GreceivedSMS1():
    oo = datetime.today()
    if msgG.count_documents({"Status":"UNREAD"}) == 0:
        return ("No messages available.")
    else:
        for x in msgG.find({"Status":"UNREAD"}):
           if msgG.find({"Status":"UNREAD"}) is None:
               return jsonify({"Unread Globe Messages": " Empty"})
           else: 
               sms = [serial(item) for item in msgG.find({"Status":"UNREAD"})]           
               return jsonify({'Unread Globe Messages': sms},{"zTime": oo}), checkG()

@app.route('/sms/globe/received/read', methods=['GET'])
def get_GreceivedSMS2():
    oo = datetime.today()
    if msgG.count_documents({"Status":"READ"}) == 0:
        return ("No messages available.")
    else:
        for x in msgG.find({"Status":"READ"}):
           if msgG.find({"Status":"READ"}) is None:
               return jsonify({"Read Globe Messages": " Empty"})
           else: 
               sms = [serial(item) for item in msgG.find({"Status":"READ"})]           
               return jsonify({'Read Globe Messages': sms},{"zTime": oo})
                                   
@app.route('/sms/smart/received', methods=['GET'])
def get_SreceivedSMS():
    oo = datetime.today()
    if msgS.count_documents({}) == 0:
        return ("No messages available.")
    else:
        for x in msgS.find():
           if msgS.find() is None:
               return jsonify({"Received Smart Messages": " Empty"})
           else:
               sms = [serial(item) for item in msgS.find()]
               return jsonify({'Received Smart Messages': sms},{"zTime": oo}), checkS()

@app.route('/sms/smart/received/unread', methods=['GET'])
def get_SreceivedSMS1():
    oo = datetime.today()
    if msgS.count_documents({"Status":"UNREAD"}) == 0:
        return ("No messages available.")
    else:
        for x in msgS.find({"Status":"UNREAD"}):
           if msgS.find({"Status":"UNREAD"}) is None:
               return jsonify({"Unread Smart Messages": " Empty"})
           else: 
               sms = [serial(item) for item in msgS.find({"Status":"UNREAD"})]           
               return jsonify({'Unread Smart Messages': sms},{"zTime": oo}), checkS()

@app.route('/sms/smart/received/read', methods=['GET'])
def get_SreceivedSMS2():
    oo = datetime.today()
    if msgS.count_documents({"Status":"READ"}) == 0:
        return ("No messages available.")
    else:
        for x in msgG.find({"Status":"READ"}):
           if msgS.find({"Status":"READ"}) is None:
               return jsonify({"Read Smart Messages": " Empty"})
           else: 
               sms = [serial(item) for item in msgS.find({"Status":"READ"})]           
               return jsonify({'Read Smart Messages': sms},{"zTime": oo})


def checkG():
    for x in msgG.find({"Status":"UNREAD"}):
        msgG.update_one({"Status":"UNREAD"},{"$set":{"Status":"READ"}})

def checkS():
    for x in msgS.find({"Status":"UNREAD"}):
        msgS.update_one({"Status":"UNREAD"},{"$set":{"Status":"READ"}})
    
if __name__ == '__main__':
    app.run(host='192.168.26.107',port='9000')
