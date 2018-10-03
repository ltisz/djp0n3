from ircbot import *
import os
import random
import datetime
import json
import threading

channels = ["#equestria","#kame-house"]
channel = ""
server = "irc.slashnet.org"
nickname = "d3rpyh00v3z"
pw = ""
timerEnd = datetime.datetime.fromtimestamp(99999999999)


irc = IRCBot()
irc.connect(server,channels,nickname,pw)


##TIMER FUNCTIONALITY
timenow = datetime.datetime.now().replace(microsecond=0)
delList = []
#Actual timer function, activated by threading
def timer(tyme, name, room, alert):
    irc.send (room, name + ', ' + tyme + ' is up: ' + alert)
    #Delete timer from json file after it goes off
    with open('/home/tiszenkel/timers.json', 'w') as g:
        del timersList[list(timersList.keys())[list(timersList.values()).index([[tyme,name,room,alert]])]]
        json.dump(timersList, g)

#Load timers from json file upon program start
with open('/home/tiszenkel/timers.json', 'r') as g:
    try:
        timersList = json.load(g)
        print(timersList)
    except ValueError:
        print("Timers error")
        timersList = {}

#Check for timers that didn't go off when they should have,
#Or timers that will go off in the future
for time in timersList.keys():
    timeDiff = datetime.datetime.strptime(time, "%m/%d/%y %H:%M:%S")-timenow
    #Missed timers due to downtime
    if timeDiff.days < 0:
        channel = timersList[time][0][2]
        name = timersList[time][0][1]
        alert = timersList[time][0][3]
        tyme = timersList[time][0][0]
        irc.send(channel,"Attention " + name + "! I am sorry but I missed your " + tyme + " timer - " + alert)
        #Need to put the timers in a list to delete after checking as dictionary can't change in size
        delList.append(time)
    #If timediff isn't negative, we need to queue up new timers
    else:
        print(time)
        print(timeDiff)
        timerlength = timeDiff.total_seconds()
        t = threading.Timer(timerlength, timer, timersList[time][0])
        t.start()
        print("Timer set for " + str(timerlength) + " from now.")

#Delete timers that were missed due to downtime
with open('/home/tiszenkel/timers.json', 'w') as g:
    for item in delList:
        del timersList[item]
        json.dump(timersList, g)

#MAIN LOOP
while True:
    timenow = datetime.datetime.now().replace(microsecond=0)

    text = irc.get_text()
    print(timenow.strftime("%m/%d/%y %H:%M:%S") + " - " + text)
    for chan in channels:
        if chan in text:
            channel = chan 

    if "PRIVMSG" in text and channel in text and ":hello" in text:
        irc.send(channel, "Hello!")

##TIMER FUNCTIONALITY
    if channel + " :$timer" in text:
        #Getting name, message, timer length
        message = text.rpartition("$timer ")[2]
        print("message: " + message)
        tyme = message.split()[0]
        alert = " ".join(message.split()[1:])
        name = text.rsplit("!")[0].lstrip(":")
        timerlength = irc.timecruncher(tyme)
        print(timerlength)
        #Timecruncher returns 0 if it cannot recognize length of time
        if timerlength == 0:
            irc.send (channel, "Unrecognized length of time. Please use s, m, h, d, w, y")
        #Writing timer information to json file so timer persists thru disconnects
        timerEnd = timenow+datetime.timedelta(seconds=timerlength)
        with open('/home/tiszenkel/timers.json', 'w') as f:
            timersList[timerEnd.strftime("%m/%d/%y %H:%M:%S")] = [[tyme,name,channel,alert]]
            print(timersList[timerEnd.strftime("%m/%d/%y %H:%M:%S")])
            json.dump(timersList, f)
        #Initiate timer. This timer WILL go away if program ends.
        t = threading.Timer(timerlength, timer, [tyme,name,channel,alert])
        t.start()
        irc.send(channel, "Timer set.")
        print("Timer set for " + str(timerlength) + " from now.")


