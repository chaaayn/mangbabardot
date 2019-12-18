import pymongo, pprint, time, os
from bson.objectid import ObjectId
from pymongo import MongoClient
from flask import Flask, jsonify, request, abort, make_response
import json, bson

mongodb_host = os.environ.get('MONGO_HOST', 'localhost')
mongodb_port = int(os.environ.get('MONGO_PORT', '27017'))
myclient = MongoClient(mongodb_host, mongodb_port)
mydb = myclient["testdb"]
numcol = mydb["number"]

cur_time = time.time()
prev_time = time.ctime(cur_time)

def serial(dct):
    for k in dct:
        if isinstance(dct[k], bson.ObjectId):
            dct[k] = str(dct[k])
    return dct



app = Flask(__name__)

@app.route('/test1/contacts', methods=['GET'])
def get_contacts():
   """ contacts = numcol.find()
    response = ["Contacts"]
    for contact in contacts:
        contact['_id'] = str(contact['_id'])
        response.append(contact)
    return jsonify(response)"""
   """contactlist = mydb.numcol.count()
   if contactlist == 0:
       return ("Contacts empty.")"""
   for x in numcol.find():
           print(x)
           data = [serial(item) for item in numcol.find()]
           return jsonify({'Contacts': data})
    
@app.route('/test1/contacts', methods=['POST'])
def add_contact():
    req_cont = {"Name":request.json["Name"],
                "Number":request.json["Number"]
                }
    numcol.insert_one(req_cont)
    return jsonify({"Result":True}),201
    
"""req_data = request.get_json()
    numcol.insert_one(req_data).inserted_id
    return ({'result':True}), 201"""

@app.route('/test1/contacts', methods=['DELETE'])
def del_contact():
    del_cont = request.get_json()
    numcol.delete_one(del_cont)
    return ({'result':True})

if __name__ == '__main__':
    app.run(debug=True)

"""post = {"author" : "test",
        "text": "test",
        "tags": ["test", "test1", "test2"],
        "date": datetime.datetime.utcnow()}

posts = mydb.posts
post_id = posts.insert_one(post).inserted_id
post_id

mydb.list_collection_names()
[u'posts']"""

