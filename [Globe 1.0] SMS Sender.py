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
smsGlobe = mydb["smsGlobe"]
smsSmart = mydb["smsSmart"]
globe = mydb["globe"]

def CheckMessage():
    smsCheck = globe.find_one({"Status":"Pending"})
    if smsCheck is None:
        print "No more messages."
        time.sleep(20)
def StartupGlobe():
    print ("Starting Globe")
    global modem
    portlist = list(serial.tools.list_ports.comports())
    for port in reversed(portlist):

        try:
            if "HUAWEI Mobile" == port[1]:
                print "Device connected.", port[1]
                modem = serial.Serial(port[1], 115200, timeout = 5)
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
    testSMS()
    
def testSMS():
    stat = True
    x = globe.find_one({"Status":"Pending"})
    penMessage = x['Message']
    
    if len(penMessage) <= 120:
        sender = x['Sender']
        num = x['Receiver']
        date1 = str(x['Date'])
        date2 = date1[0:19]
        modem.write(bytes('AT+CMGS="%s"\r\n' % num))
        time.sleep(0.5)
        modem.write(bytes('Message: "%s"\r\n' % penMessage))
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
            globe.update_one({"Status":"Pending"},{ "$set":{"Status":"Processed"}})    
        elif y.startswith('+CMS') or y.startswith('^RSSI'):
            print('Failed.')
            
    elif len(penMessage) <= 240:
        stat = True
        sender = x['Sender']
        num = x['Receiver']
        date1 = str(x['Date'])
        date2 = date1[0:19]
        v = len(penMessage)
        message1 = penMessage[0:137]
        message2 = penMessage[137:v]
        modem.write(bytes('AT+CMGS="%s"\r\n' % num))
        time.sleep(0.5)
        modem.write(bytes('(1 of 2) Message: "%s"\r\n' % message1))
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
        modem.write(bytes('(2 of 2) Message: "%s"\r\n' % message2))
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
            globe.update_one({"Status":"Pending"},{ "$set":{"Status":"Processed"}})    
        elif y.startswith('+CMS') or y.startswith('^RSSI'):
            print('Failed.')
        
        

def main():
  
    current_time = time.time()
    previous_time = time.ctime(current_time)
    while True:
        CheckMessage()
    modem.close()

if __name__ == '__main__':
    main()