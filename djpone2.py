from ircbot import *
import os
import random

#Testin this comment
channels = ["#equestria","#death"]
server = "irc.slashnet.org"
nickname = "d3rpyh00v3z"
pw = ""

irc = IRCBot()
irc.connect(server,channels,nickname,pw)

while True:
    text = irc.get_text()
    print(text)
    for chan in channels:
        if chan in text:
            channel = chan 
    if "PRIVMSG" in text and channel in text and "hello" in text:
        irc.send(channel, "Hello!")
    if "PRIVMSG" in text and channel in text and ":N" in text:
        irc.send(channel, "I")
