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

globe = [ "63904", "63905", "63906", "63915", "63916", "63917", "63926", "63927",
          "63935", "63936", "63937", "63945", "63956", "63965", "63966", "63967",
          "63975", "63976", "63977", "63978", "63979", "63994", "63995", "63997"]

smart = [ "63813", "63908", "63911", "63913", "63914", "63918", "63913", "63919",
          "63920", "63921", "63928", "63929", "63939", "63947", "63949", "63961",
          "63970", "63981", "63989", "63998", "63999"]

def CheckCarrier():
    simcheck = smscol.find_one({"Status":"Pending"})
    sim_number = simcheck['Receiver']
    sim_prefix = sim_number[0:5]
    if sim_prefix in globe:
        StartupGlobe()
    elif sim_prefix in smart:
        StartupSmart()
        
def StartupGlobe():
    print ("Start")
    global modem
    portlist = list(serial.tools.list_ports.comports())
    for port in reversed(portlist):

        try:
            if "HUAWEI Mobile" == port[1]:
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
    testSMS()

def StartupSmart():
    print ("Start")
    global modem
    portlist = list(serial.tools.list_ports.comports())
    for port in reversed(portlist):

        try:
            if "ZTE WCDMA Technologies MSM" == port[1]:
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
    testSMS()
    
def testSMS():
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

    print(y, 'Sent?')

    if y.startswith('OK'):
        print('Sent')
        smscol.update_one({"Status":"Pending"},{ "$set":{"Status":"Processed"}})    
    elif y.startswith('+CMS') or y.startswith('^RSSI'):
        print('Failed.')

def main():
  
    current_time = time.time()
    previous_time = time.ctime(current_time)
    counter = 0 ##test
    while True:
            CheckCarrier() ##test
            counter += 1 ##test
            print previous_time
            print(counter)
            print(num)
    modem.close()

if __name__ == '__main__':
    CheckCarrier()
    main()