from components import abstracts, pluginmanager, config
import asyncio
from time import clock
import threading, pickle
from datetime import datetime, timezone, timedelta
from urllib import request
import json
from math import floor
import discord

defaults = {"Chat": {"Channel": "", "Client-ID": ""}}
cfg = config.load("chatanalytics", defaults)


class Checker(threading.Thread):
    
    def __init__(self, uname,dtime,cid):
        self.cid = cid
        self.uname = uname
        self.noob = True
        self.dtime = dtime
        threading.Thread.__init__(self, name="Check Time: %s"%uname)
        self.start()
        
    def run(self):
        try:
            if not (pluginmanager.plugins['twitchapi'].getUser(name=self.uname).getUserAge()<(self.dtime)):
                self.noob = False
        except:
            return
    
def getNooblist(channel, cid):
    name = channel.lstrip('#')
    
    cachename = "data/days.cache"
    
    try:
        pkl_file = open(cachename, 'rb')
        clearedlist = pickle.load(pkl_file)
        pkl_file.close()
    except:
        clearedlist=[]
    
    chatlist = getChatters(name, cfg['Chat']['Client-ID'])
    threadlist = []
    
    for user in chatlist:
        if user not in clearedlist:
            threadlist.append(Checker(user,43200,cid))
    
    nooblist = []
    
    for thread in threadlist:
        thread.join()
        if thread.noob:
            nooblist.append(thread.uname)
        else:
            clearedlist.append(thread.uname)
    
    output = open(cachename, 'wb')
    pickle.dump(clearedlist, output)
    output.close()

    return nooblist


cid = None

def getChatters(name, cid):
    return json.loads((request.urlopen("http://tmi.twitch.tv/group/user/%s/chatters"%name).read().decode("utf-8")))["chatters"]["viewers"]

class Plugin(abstracts.Plugin):
    
    def __init__(self):
        self.counter = 0
        self.running = True
        bot = pluginmanager.resources["DSC"]["BOT"]
        loop = pluginmanager.resources["DSC"]["LOOP"]
        asyncio.run_coroutine_threadsafe(self.trackloop(bot), loop)
    
    def handlers(self):
        return [abstracts.Handler('DSC:COMMAND:?NOOBLIST', self, self.nooblist),
                abstracts.Handler('DSC:COMMAND:?GETAGE', self, self.getage),
                abstracts.Handler('TWITCH:MSG', self, self.chatcount, priority=abstracts.Handler.PRIORITY_MONITOR)]
    
    def nooblist(self, message=None, **kw):
        if message.content.startswith('?nooblist'):
            bot = pluginmanager.resources["DSC"]["BOT"]
            loop = pluginmanager.resources["DSC"]["LOOP"]
            t = clock()
            nubs = getNooblist(cfg['Chat']['Channel'], cfg['Chat']['Client-ID'])
            if len(nubs) is 0:
                out = 'No noobs found in chat :smile:'
            else:
                out = str(nubs)
            asyncio.run_coroutine_threadsafe(bot.send_message(message.channel,'%s [%fs]'%(out,clock()-t)), loop)
    
    def getage(self, message=None, args=None, **kw):
        if len(args)>0:
            bot = pluginmanager.resources["DSC"]["BOT"]
            loop = pluginmanager.resources["DSC"]["LOOP"]
            asyncio.run_coroutine_threadsafe(bot.send_message(message.channel,'%s'%(str(timedelta(seconds=floor(pluginmanager.plugins['twitchapi'].getUser(name=args[0]).getUserAge()))))), loop)
            
    def chatcount(self, **kw):
        self.counter+=1
            
    async def trackloop(self, bot):
        await bot.wait_until_ready()
        while True:
            await bot.change_presence(game=discord.Game(name="Chat Speed: %d mpm"%self.counter))
            self.counter = 0
            await asyncio.sleep(60)
        
        
        
        
        
        