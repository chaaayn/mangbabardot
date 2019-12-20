from pymongo import MongoClient
import os, csv, time

current_time = time.time()
prev_time = time.ctime(current_time)
mongodb_host = os.environ.get('MONGO_HOST', 'localhost')
mongodb_port = int(os.environ.get('MONGO_PORT', '27017'))
myclient = MongoClient(mongodb_host, mongodb_port)
mydb = myclient["testdb"]
numcol = mydb["number"]
smscol = mydb["sms"]

x = smscol.find_one({"Status":"Pending"})
print(x['Message'])
print(x['Sender'])
print(x['Receiver'])
print(prev_time)
