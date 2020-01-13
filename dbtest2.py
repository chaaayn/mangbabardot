from pymongo import MongoClient
import os, csv, time, operator
from datetime import datetime, timedelta, date

current_time = time.time()
prev_time = time.ctime(current_time)
mongodb_host = os.environ.get('MONGO_HOST', 'localhost')
mongodb_port = int(os.environ.get('MONGO_PORT', '27017'))
myclient = MongoClient(mongodb_host, mongodb_port)
mydb = myclient["testdb"]
numcol = mydb["number"]
smscol = mydb["sms"]
simtest = mydb["simtest"]
globe = mydb["globe"]
smart = mydb["smart"]
simGlobe = mydb["simGlobe"]
simSmart = mydb["simSmart"]

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
"""xy = smscol.find({"Status":"Pending"}, {"_id": 0, "Status":0, "Receiver":0})
for i in xy:
    print str(i)
    xyz = len(str(i))
    print xyz - 24
    if (xyz -24) < 160:
        print "Nice" """
xy = smscol.find_one({"Status":"Processed"})
xx = str(xy['Date'])
xyy = xx[0:19]
print xyy

ab = xy['Receiver']
abc = ab[0:5]
abcd = ab[8:12]
print abc, abcd
globe = [ "63905", "63915" ]
if ab[0:5] in globe:
    print "Globe"

simtest.insert({"Globe": "Globe sent", "Number": 0})
simtest.update_one({"Globe": "Globe sent"}, { "$set": {"Number": 1}})
q = simtest.find_one()
print ("Sent messages: " + str(q["Number"]))

qw = xy['Message']
print qw
qwe = len(qw)
print qwe
qwer = qwe / 2
print qwer
qwert = qw[0:qwer]
print qwert
qwerty = qw[qwer:qwe]
print qwerty

print date.today()
ty = datetime.today().replace(day=1, month=1)
yx = timedelta(weeks=1)
print xy['Date'] - ty
print ty + yx

"""#report today
oo = datetime.today()
xl = datetime.time(datetime.now())
print xl.month()
oo1 = datetime.today() + timedelta()
oo2 = datetime.today() - timedelta(days=1)
print oo1
print oo2

o = oo.strftime("%H:%M")
print o"""

oo1 = datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond = 0)
oo2 = datetime.today().replace(day=31, minute=59, second=59, microsecond = 999999)
print oo1
print oo2



