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
simtest = mydb["simtest"]

"""x = smscol.find_one({"Status":"Pending"})
if x == None:
    print "No more messages."
smscol.update_one({"Status":"Pending"},
                  { "$set": {"Status":"Processed"}})"""
y = smscol.count_documents({"Status":"Processed"})
print "Sent messages:" + str(y)


x = smscol.count_documents({"Status":"Pending"})
print "Pending messages:" + str(x)
"""for y in x:
    xy = x['Receiver']
    xyz = xy[0:5]
    if xyz == "63905":
        sim = "globe"
        if sim == "globe":
            simcount = 0
            simcount += 1
            print simcount"""
