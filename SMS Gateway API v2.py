import pymongo, pprint, time, os
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from pymongo import MongoClient
from flask import Flask, jsonify, request, abort, make_response, redirect, url_for
import json, bson
from flask_apscheduler import APScheduler

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
report = mydb["report"]
reportM = mydb["reportM"]
reportY = mydb["reportY"]




def serial(dct):
    for k in dct:
        if isinstance(dct[k], bson.ObjectId):
            dct[k] = str(dct[k])                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    return dct

app = Flask(__name__)

@app.route('/home')
def home():
    return "SMS GATEWAY API HOME"

@app.route('/sms/<carrier>', methods=['GET', 'POST', 'DELETE'])
def get_sms(carrier):
    
    if carrier == 'globe':
        if request.method == 'GET':
            if globe.count_documents({}) == 0:
                return ("No message available.")
            else:
                for x in globe.find():
                   if globe.find() is None:
                       return jsonify({"Globe Messages": " Empty"})
                   else:
                       sms = [serial(item) for item in globe.find()]
                       return jsonify({'Globe Messages': sms})
    elif carrier == 'smart':
        if smart.count_documents({}) == 0:
            return ("No message available.")
        else:
            for x in smart.find():
               if smart.find() is None:
                   return jsonify({"Smart Messages": " Empty"})
               else:
                   sms = [serial(item) for item in smart.find()]
                   return jsonify({'Smart Messages': sms})
                
    elif carrier == 'all':
        if request.method == 'GET':
            if (smart.count_documents({}) == 0) and (globe.count_documents({}) == 0):
                return ("No message available.")
            else:
                sms = [serial(item) for item in smscol.find()]
                smart1 = [serial(item1) for item1 in smart.find()]
                globe1 = [serial(item1) for item1 in globe.find()]
                return jsonify({"Smart": smart1}, {"Globe": globe1})
            
        elif request.method == 'POST':
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

        elif request.method == 'DELETE':
            del_sms = request.get_json()
            for x in smart.find(del_sms):
                smart.delete_one(del_sms)
            for x in globe.find(del_sms):
                globe.delete_one(del_sms)
            return redirect(url_for('get_sms'))                
  

@app.route('/contacts', methods=['POST', 'DELETE', 'GET'])
def add_contact():
    if request.method == 'POST':
        if (request.json["Number"]) == 12: 
            req_cont = {"Name":request.json["Name"],
                        "Number":request.json["Number"]
                        }
            numcol.insert_one(req_cont)
            return jsonify({"Result":"Contact Added"}),201
        else:
            return jsonify({"Invalid Number"})
        
    elif request.method == 'GET':
       xy = numcol.count_documents({})
       if xy == 0:
           return ("Contacts empty.")
       else:
           for x in numcol.find():
            print(x)
            data = [serial(item) for item in numcol.find()]
            return jsonify({'Contacts': data})
        
    elif request.method == 'DELETE':
        del_cont = request.get_json()
        numcol.delete_one(del_cont)
        return redirect(url_for('get_contacts'))
                

@app.route('/reports/<carrier>/<period>', methods=['GET'])
def get_reports(carrier,period):
    
    oo = datetime.today()
    get_sentGlobe = globe.count_documents({"Status":"Processed"})
    get_sentSmart = smart.count_documents({"Status":"Processed"})
    get_pendingGlobe = globe.count_documents({"Status":"Pending"})
    get_pendingSmart = smart.count_documents({"Status":"Pending"})
    day2 = oo.replace(hour=23, minute=59, second=59, microsecond = 999999)
    day1 = oo.replace(hour=0, minute=0, second=0, microsecond = 0)
    month2 = oo.replace(month=oo.month+1, day=1,hour=23, minute=59, second=55, microsecond = 0) - timedelta(days=1)
    month1 = oo.replace(day=1,hour=0, minute=0, second=0, microsecond = 0)
    year2 = oo.replace(month=12,day=31,hour=23, minute=59, second=59, microsecond = 999999)
    year1 = oo.replace(month=1,day=1,hour=0, minute=0, second=0, microsecond = 0)
    
    ##ALL CARRIER
    if carrier == 'all':
        if period == 'total':
            return jsonify({"Sent Globe messages": get_sentGlobe,
                           "Unsent Globe messages": get_pendingGlobe,
                            "Sent Smart messages": get_sentSmart,
                            "Unsent Smart messages": get_pendingSmart,
                            "Total Sent messages": get_sentGlobe + get_sentSmart,
                            "zTime": oo})
        
        elif period == 'today':
            oo4 = smart.count_documents({"Status":"Processed","Date":{"$lt": day2, "$gt": day1}})
            oo6 = globe.count_documents({"Status":"Processed","Date":{"$lt": day2, "$gt": day1}})
            oo7 = oo4 + oo6
            return jsonify({"Smart Messages Today":oo4},{"Globe Messages Today":oo6},{"Total messages today":oo7},
                            {"zTime": oo})
        
        elif period == 'month':
            oo4 = smart.count_documents({"Date":{"$lt": month2, "$gt": month1}})
            oo6 = globe.count_documents({"Date":{"$lt": month2, "$gt": month1}})
            oo7 = oo4 + oo6
            return jsonify({"Smart Messages this month":oo4},{"Globe Messages this month":oo6},{"Total messages this month":oo7},
                            {"zTime": oo})
        elif period == 'year':

            oo4 = smart.count_documents({"Date":{"$lt": year2, "$gt": year1}})
            oo6 = globe.count_documents({"Date":{"$lt": year2, "$gt": year1}})
            oo7 = oo4 + oo6
            return jsonify({"Smart Messages this year":oo4},{"Globe Messages this year":oo6},{"Total messages this year":oo7},
                            {"zTime": oo})
    ##SMART CARRIER
    if carrier == 'smart':
        if period == 'total':
            return jsonify({"Sent Smart messages": get_sentSmart,
                            "Unsent Smart messages": get_pendingSmart,
                            "zTime": oo})
        if period == 'today':
            get_sentSmart = smart.count_documents({"Status":"Processed","Date":{"$lt": day2, "$gt": day1}})
            get_pendingSmart = smart.count_documents({"Status":"Pending"})
            return jsonify({"Sent Smart messages": get_sentSmart,
                            "Unsent Smart messages": get_pendingSmart,
                            "zTime": oo})
        if period == 'month':
            oo4 = smart.count_documents({"Date":{"$lt": month2, "$gt": month1}})
            return jsonify({"Smart Messages this month":oo4},
                            {"zTime": oo})
        if period == 'year':
            oo4 = smart.count_documents({"Date":{"$lt": year2, "$gt": year1}})
            return jsonify({"Smart Messages this year":oo4},
                            {"zTime": oo})
    ##GLOBE CARRIER
    if carrier == 'globe':
        if period == 'total':
            return jsonify({"Sent Globe messages": get_sentGlobe,
                            "Unsent Globe messages": get_pendingGlobe,
                            "zTime": oo})
        if period == 'today':
            return jsonify({"Sent Globe messages": get_sentGlobe,
                            "Unsent Globe messages": get_pendingGlobe,
                            "zTime": oo})
        if period == 'month':
            oo4 = globe.count_documents({"Date":{"$lt": month2, "$gt": month1}})
            return jsonify({"Globe Messages this month":oo4},
                            {"zTime": oo})
        if period == 'year':
            oo4 = globe.count_documents({"Date":{"$lt": year2, "$gt": year1}})
            return jsonify({"Globe Messages this year":oo4},
                            {"zTime": oo})
    
            
@app.route('/sms/globe/received/<status>', methods=['GET'])
def get_GreceivedSMS(status):
    oo = datetime.today()
    if status == 'all':
        if msgG.count_documents({}) == 0:
            return ("No messages available.")
        else:
            for x in msgG.find():
               if msgG.find() is None:
                   return jsonify({"Received Globe Messages": " Empty"})
               else: 
                   sms = [serial(item) for item in msgG.find()]           
                   return jsonify({'Received Globe Messages': sms},{"zTime": oo}), checkG()
    elif status == 'unread':
        if msgG.count_documents({"Status":"UNREAD"}) == 0:
            return ("No messages available.")
        else:
            for x in msgG.find({"Status":"UNREAD"}):
               if msgG.find({"Status":"UNREAD"}) is None:
                   return jsonify({"Unread Globe Messages": " Empty"})
               else: 
                   sms = [serial(item) for item in msgG.find({"Status":"UNREAD"})]           
                   return jsonify({'Unread Globe Messages': sms},{"zTime": oo}), checkG()
                
    elif status == 'read':
        if msgG.count_documents({"Status":"READ"}) == 0:
            return ("No messages available.")
        else:
            for x in msgG.find({"Status":"READ"}):
               if msgG.find({"Status":"READ"}) is None:
                   return jsonify({"Read Globe Messages": " Empty"})
               else: 
                   sms = [serial(item) for item in msgG.find({"Status":"READ"})]           
                   return jsonify({'Read Globe Messages': sms},{"zTime": oo})

                                   
@app.route('/sms/smart/received/<status>', methods=['GET'])
def get_SreceivedSMS(status):
    oo = datetime.today()
    if status == 'all':
        if msgS.count_documents({}) == 0:
            return ("No messages available.")
        else:
            for x in msgS.find():
               if msgS.find() is None:
                   return jsonify({"Received Smart Messages": " Empty"})
               else:
                   sms = [serial(item) for item in msgS.find()]
                   return jsonify({'Received Smart Messages': sms},{"zTime": oo}), checkS()
    elif status == 'unread':
        if msgS.count_documents({"Status":"UNREAD"}) == 0:
            return ("No messages available.")
        else:
            for x in msgS.find({"Status":"UNREAD"}):
               if msgS.find({"Status":"UNREAD"}) is None:
                   return jsonify({"Unread Smart Messages": " Empty"})
               else: 
                   sms = [serial(item) for item in msgS.find({"Status":"UNREAD"})]           
                   return jsonify({'Unread Smart Messages': sms},{"zTime": oo}), checkS()
    elif status == 'read':
        if msgS.count_documents({"Status":"READ"}) == 0:
            return ("No messages available.")
        else:
            for x in msgG.find({"Status":"READ"}):
               if msgS.find({"Status":"READ"}) is None:
                   return jsonify({"Read Smart Messages": " Empty"})
               else: 
                   sms = [serial(item) for item in msgS.find({"Status":"READ"})]           
                   return jsonify({'Read Smart Messages': sms},{"zTime": oo})
            
@app.errorhandler(500)
def error_500(error):
    return redirect(url_for('home'))
@app.errorhandler(405)
def error_405(error):
    return redirect(url_for('home'))

##DAILY,MONTHLY, AND YEARLY STORE IN DB
def report1():
    cur = datetime.today()
    oo2 = cur.replace(hour=0,minute=0,second=0,microsecond=0)
    oo1 = cur.replace(hour=23,minute=59,second=59,microsecond=999999)
    
    ##day
    if cur.hour == 23 and cur.minute == 59 and cur.second == 58:
        reportt = {"Date":cur, "Globe Sent": globe.count_documents({"Status":"Processed","Date":{"$lt": oo1, "$gt": oo2}}), "Smart Sent": smart.count_documents({"Status":"Processed","Date":{"$lt": oo1, "$gt": oo2}})}
        report.insert_one(reportt)
    ##month 
    o3 = cur.replace(day=1, hour=0, minute=0, second=0,microsecond=0)
    o4 = cur.replace(month=cur.month+1, day=1,hour=23, minute=59, second=58, microsecond = 0) - timedelta(days=1)
    if cur == o4:
        reportsm = {"Date":cur, "Globe Sent": globe.count_documents({"Status":"Processed","Date":{"$lt": o4, "$gt": o3}}), "Smart Sent": smart.count_documents({"Status":"Processed","Date":{"$lt": oo4, "$gt": oo3}})}
        reportM.insert_one(reportsm)
    ##year
    o5 = cur.replace(month=1,day=1, hour=0, minute=0, second=0,microsecond=0)
    o6 = cur.replace(month=12,day=31,hour=23,minute=59,second=58,microsecond=0)
    if cur == o6:
        reportsy = {"Date":cur, "Globe Sent": globe.count_documents({"Status":"Processed","Date":{"$lt": o6, "$gt": o5}}), "Smart Sent": smart.count_documents({"Status":"Processed","Date":{"$lt": oo6, "$gt": oo5}})}

    
def checkG():
    for x in msgG.find({"Status":"UNREAD"}):
        msgG.update_one({"Status":"UNREAD"},{"$set":{"Status":"READ"}})

def checkS():
    for x in msgS.find({"Status":"UNREAD"}):
        msgS.update_one({"Status":"UNREAD"},{"$set":{"Status":"READ"}})
    
if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.add_job(func=report1, trigger='interval', id='reports', seconds=1)
    scheduler.start()
    app.run(host='192.168.26.107',port='9000')
