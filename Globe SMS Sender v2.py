#!/usr/bin/env python
import serial, csv, os, time, shutil, pprint, threading
import serial.tools.list_ports
from threading import Thread
from pymongo import MongoClient
from datetime import datetime

from curses import ascii

mongodb_host = os.environ.get('MONGO_HOST', 'localhost')
mongodb_port = int(os.environ.get('MONGO_PORT', '27017'))
myclient = MongoClient(mongodb_host, mongodb_port)
mydb = myclient["testdb"]
numcol = mydb["number"]
smscol = mydb["sms"]
smsGlobe = mydb["smsGlobe"]
simGlobe = mydb["simGlobe"]
globe = mydb["globe"]
msgG = mydb["messagesG"]



def CheckMessage():
    smsCheck = globe.find_one({"Status":"Pending"}) 
    if smsCheck is None:
        print "No more messages."
        print datetime.now()
        time.sleep(1)
    else:
        SMS()
        
def StartupGlobe():
    print ("Starting Globe")
    global modem
    portlist = list(serial.tools.list_ports.grep("HUAWEI Mobile"))
    for port in (portlist):
        print port[1]
        try:
            if "HUAWEI Mobile" == port [1]:
                print "Device connected.", port[1]
                modem = serial.Serial(port[0], 115200, timeout = 5)
                break 
            else:
                time.sleep(10)
                print "Device not detected."
                StartupGlobe().close()
                
                
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
    
def SMS():
    stat = True
    x = globe.find_one({"Status":"Pending"})
    penMessage = x['Message']
    
    if len(penMessage) <= 160:
        sender = x['Sender']
        num = x['Receiver']
        date1 = str(x['Date'])
        date2 = date1[0:19]
        modem.write(bytes('AT+CMGS="%s"\r\n' % num))
        time.sleep(0.5)
        modem.write(bytes(penMessage))
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

        print(y, 'Sent?')

        if y.startswith('OK'):
            print('Sent')
            print datetime.now()
            globe.update_one({"Status":"Pending"},{ "$set":{"Status":"Processed"}})    
        elif y.startswith('+CMS') or y.startswith('^RSSI'):
            print('Failed.')
            
    elif len(penMessage) > 160:
        stat = True
        sender = x['Sender']
        num = x['Receiver']
        date1 = str(x['Date'])
        date2 = date1[0:19]
        v = len(penMessage)
        modem.write(bytes('AT+CMGS="%s"\r\n' % num))
        time.sleep(0.5)
        modem.write(bytes(penMessage))
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

        print(y, 'Sent?')

        if y.startswith('OK'):
            print('Sent')   
        elif y.startswith('+CMS') or y.startswith('^RSSI'):
            print('Failed.')
        stat = True
        modem.write(bytes('AT+CMGS="%s"\r\n' % num))
        time.sleep(0.5)
        modem.write(bytes(penMessage[161:v]))
        time.sleep(0.5)
        modem.write(bytes('This automated message is from %s.\r\n' % sender))
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

            print(y, 'Sent?')

        if y.startswith('OK'):
            print('Sent')
            print datetime.now()
            globe.update_one({"Status":"Pending"},{ "$set":{"Status":"Processed"}})    
        elif y.startswith('+CMS') or y.startswith('^RSSI'):
            print('Failed.')

    elif len(penMessage) > 240:
        stat = True
        sender = x['Sender']
        num = x['Receiver']
        date1 = str(x['Date'])
        date2 = date1[0:19]
        v = len(penMessage)
        message1 = penMessage[0:137]
        message2 = penMessage[137:241]
        message3 = penMessage[241:v]
        modem.write(bytes('AT+CMGS="%s"\r\n' % num))
        time.sleep(0.5)
        modem.write(bytes('(1 of 3) Message: "%s"\r\n' % message1))
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

        print(y, 'Sent?')

        if y.startswith('OK'):
            print('Sent')
                
        elif y.startswith('+CMS') or y.startswith('^RSSI'):
            print('Failed.')

        stat = True
        modem.write(bytes('AT+CMGS="%s"\r\n' % num))
        time.sleep(0.5)
        modem.write(bytes('(2 of 3) Message: "%s"\r\n' % message2))
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

        print(y, 'Sent?')

        if y.startswith('OK'):
            print('Sent')
               
        elif y.startswith('+CMS') or y.startswith('^RSSI'):
            print('Failed.')    
        stat = True
        modem.write(bytes('AT+CMGS="%s"\r\n' % num))
        time.sleep(0.5)
        modem.write(bytes('(3 of 3) Message: "%s"\r\n' % message3))
        time.sleep(0.5)
        modem.write(bytes('Sender: %s\r\n' % sender))
        time.sleep(0.5)
        modem.write(bytes('Date: %s' % date2))
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

            print(y, 'Sent?')
    
        if y.startswith('OK'):
            print('Sent')
            print datetime.now()
            globe.update_one({"Status":"Pending"},{ "$set":{"Status":"Processed"}})    
        elif y.startswith('+CMS') or y.startswith('^RSSI'):
            print('Failed.')
            
def saveMessage():
    modem.write('AT+CPMS="SM"\r\n')
    time.sleep(0.5)
    xx = modem.readlines()
    xy = str(xx)
    if xy[31] == "1" or xy[31] == "2":    
        x = []
        modem.write('AT+CMGR=0\r\n')
        time.sleep(1)
        x = modem.readlines()
        time.sleep(1)
        y = str(x).split(",")
        numm = y[2]
        date1 = y[4]
        time1 = y[5]
        msgg = y[6]
        msg1 = len(msgg) - 5

        n = numm[1:14]
        d =  date1[1:9]
        t = time1[0:8]
        m = msgg[2:msg1]

        sms = {"Sender":n, "Date and Time": d + " " + t, "Message":m,"Status":"UNREAD"}
        msgG.insert_one(sms)
        time.sleep(0.5)
        print "OKAY"
        modem.write('AT+CMGD=0\r\n')
        time.sleep(0.5)

    else:
        print "No received messages."
def main():
    while True:
        CheckMessage()
        saveMessage()
        time.sleep(0.5)
    modem.close()

if __name__ == '__main__':
    StartupGlobe()
    time.sleep(0.5)
    main()
