#!/usr/bin/env python
import serial, csv, os, time, shutil, pprint
import serial.tools.list_ports
from pymongo import MongoClient

from curses import ascii

mongodb_host = os.environ.get('MONGO_HOST', 'localhost')
mongodb_port = int(os.environ.get('MONGO_PORT', '27017'))
myclient = MongoClient(mongodb_host, mongodb_port)
mydb = myclient["testdb"]
numcol = mydb["number"]
smscol = mydb["sms"]

def Startup():
    print ("Start")
    global modem
##  global counter ##test
    portlist = list(serial.tools.list_ports.comports())
##    print portlist
    for port in reversed(portlist):
    ##    print port[0]
        try:

            print port[1]
            if "ZTE WCDMA Technologies MSM" == port[1]:
                print "Device connected.", port[1]
                modem = serial.Serial(port[0], 115200, timeout = 5)
                break
            elif "HUAWEI Mobile" == port[1]:
                print "Device connected.", port[1]
                modem = serial.Serial(port[0], 115200, timeout = 5)
                break 
            else:
                print None
                
        except Exception as e:
            print e

    if modem.isOpen():
        print "Device is open.", modem.isOpen()
        
    time.sleep(5)

    modem.write(bytes('AT\r\n')) 
    modem.readline()
    sPrint = modem.readline(modem.inWaiting())
    sPrint = sPrint.decode("UTF-8")
    sPrint = sPrint.rstrip('\r\n')

    modem.write(bytes('AT+CMGF=1\r\n')) 
    time.sleep(1)
    modem.readline()
    sPrint = modem.readline(modem.inWaiting())
    sPrint = sPrint.decode("UTF-8")
    sPrint = sPrint.rstrip('\r\n')
    
    print ("AT+CMGF=1: "+ sPrint)

def testSMS(counter):
    stat = True
    x = smscol.find_one({"Status":"Pending"})
    penMessage = x['Message']
    global num
    sender = x['Sender']
    num = x['Receiver']
    date1 = x['Date']
    modem.write(bytes('AT+CMGS="%s"\r\n' % num))
    time.sleep(0.5)
    modem.write(bytes('Message: "%s"\r\n' % penMessage))
    time.sleep(0.5)
    modem.write(bytes('Sender: %s\r\n' % sender))
    time.sleep(0.5)
    modem.write(bytes('Date: %s' % date1))
    time.sleep(0.5)
    modem.write(bytes(ascii.ctrl('z')))
    time.sleep(0.5)
    while stat:
        a = modem.readlines(modem.inWaiting())
        z = []
        y = ''

        for q in a:
            if q.startswith('OK') or q.startswith('+CMS') or q.startswith('^RSSI'):
                r = a.index(q)
                z.append(r)
                stat = False
            else: pass

        for q in z:
            y = a[q]

    print(y, 'sent?')

    if y.startswith('OK'):
        print('sent')
        smscol.update_one({"Status":"Pending"},{ "$set":{"Status":"Processed"}})    
    elif y.startswith('+CMS') or y.startswith('^RSSI'):
        print('failed')

def main():
  
    current_time = time.time()
    previous_time = time.ctime(current_time)
    counter = 0 ##test
    while True:
            testSMS(counter) ##test
            counter += 1 ##test
            print previous_time
            print(counter)
            print(num)
    modem.close()

if __name__ == '__main__':
    Startup()
    main()
