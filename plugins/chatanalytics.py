from components import abstracts, pluginmanager, config
import asyncio
from time import clock
import threading, pickle
from datetime import timedelta
from math import floor
import discord

defaults = {"Chat": {"Channel": ""}}
cachename = "data/days.cache"
cfg = config.load("chatanalytics", defaults)
channel = cfg['Chat']['Channel'].lstrip('#')


class Checker(threading.Thread):
    
    def __init__(self, uname):
        self.uname = uname
        self.noob = True
        threading.Thread.__init__(self, name="Check Time: %s"%uname)
        self.start()
        
    def run(self):
        try:
            if not pluginmanager.plugins['twitchapi'].getUser(name=self.uname).getUserAge()<43200:
                self.noob = False
        except:
            return
    
def getNooblist(channel):
    name = channel.lstrip('#')
    
    try:
        pkl_file = open(cachename, 'rb')
        clearedlist = pickle.load(pkl_file)
        pkl_file.close()
    except:
        clearedlist=[]
    
    chatlist = set(pluginmanager.plugins['twitchapi'].getChannel(name=name).getChatters())-set(clearedlist)
    threadlist = []
    
    for user in chatlist:
        threadlist.append(Checker(user))
    
    nooblist = []
    
    for thread in threadlist:
        thread.join()
        if thread.noob:
            nooblist.append(thread.uname)
        else:
            clearedlist.append(thread.uname)
    
    with open(cachename, 'wb') as output:
        pickle.dump(clearedlist, output)

    return nooblist

def formattime(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    y, d = divmod(d, 365)
    fstring = '%02d:%02d:%02d'%(h,m,s)
    if d:
        if d == 1:
            fstring = '%d day, '%d + fstring
        else:
            fstring = '%d days, '%d + fstring
    if y:
        if y == 1:
            fstring = '%d year, '%y + fstring
        else:
            fstring = '%d years, '%y + fstring
            
    return fstring

class Plugin(abstracts.Plugin):
    
    def load(self):
        self.counter = [0,0,0,0]
        self.running = True
        self.clock = threading.Lock()
        bot = pluginmanager.resources["DSC"]["BOT"]
        loop = pluginmanager.resources["DSC"]["LOOP"]
        asyncio.run_coroutine_threadsafe(self.trackloop(bot), loop)
    
    def handlers(self):
        return [abstracts.Handler('DSC:COMMAND:?NOOBLIST', self, self.nooblist),
                abstracts.Handler('DSC:COMMAND:?GETAGE', self, self.getage),
                abstracts.Handler('DSC:COMMAND:?GETID', self, self.getid),
                abstracts.Handler('DSC:COMMAND:?FOLLOWAGE', self, self.getfollowage),
                abstracts.Handler('TWITCH:MSG', self, self.chatcount, priority=abstracts.Handler.PRIORITY_MONITOR)]
    
    def nooblist(self, message=None, **kw):
        bot = pluginmanager.resources["DSC"]["BOT"]
        loop = pluginmanager.resources["DSC"]["LOOP"]
        asyncio.run_coroutine_threadsafe(bot.send_typing(message.channel), loop)
        t = clock()
        nubs = getNooblist(cfg['Chat']['Channel'])
        if len(nubs) is 0:
            out = 'No noobs found in chat :smile:'
        else:
            out = str(nubs)
        asyncio.run_coroutine_threadsafe(bot.send_message(message.channel,'%s [%fs]'%(out,clock()-t)), loop)
    
    def getage(self, message=None, args=None, **kw):
        if len(args)>0:
            bot = pluginmanager.resources["DSC"]["BOT"]
            loop = pluginmanager.resources["DSC"]["LOOP"]
            asyncio.run_coroutine_threadsafe(bot.send_typing(message.channel), loop)
            asyncio.run_coroutine_threadsafe(bot.send_message(message.channel,'%s'%(str(formattime(floor(pluginmanager.plugins['twitchapi'].getUser(name=args[0]).getUserAge()))))), loop)
            
    def getfollowage(self, message=None, args=None, **kw):
        if len(args)>0:
            bot = pluginmanager.resources["DSC"]["BOT"]
            loop = pluginmanager.resources["DSC"]["LOOP"]
            asyncio.run_coroutine_threadsafe(bot.send_typing(message.channel), loop)
            chan = pluginmanager.plugins['twitchapi'].getChannel(name=channel)
            tseconds = pluginmanager.plugins['twitchapi'].getUser(name=args[0]).getFollowAge(chan)
            if tseconds:
                tdelta = formattime(seconds=floor(tseconds))
                asyncio.run_coroutine_threadsafe(bot.send_message(message.channel,'%s'%tdelta), loop)
            else:
                asyncio.run_coroutine_threadsafe(bot.send_message(message.channel,'%s is not following %s'%(args[0],channel)), loop)
            
    def getid(self, message=None, args=None, **kw):
        if len(args)>0:
            bot = pluginmanager.resources["DSC"]["BOT"]
            loop = pluginmanager.resources["DSC"]["LOOP"]
            asyncio.run_coroutine_threadsafe(bot.send_typing(message.channel), loop)
            asyncio.run_coroutine_threadsafe(bot.send_message(message.channel,'%s'%(str(pluginmanager.plugins['twitchapi'].getUser(name=args[0]).getUserID()))), loop)
            
    def chatcount(self, **kw):
        with self.clock:
            self.counter=[x+1 for x in self.counter]
            
    async def trackloop(self, bot):
        await bot.wait_until_ready()
        while True:
            for x in range(0,4):
                with self.clock:
                    count = self.counter[x]
                    self.counter[x] = 0
                await bot.change_presence(game=discord.Game(name="Chat Speed: %d mpm"%count))
                await asyncio.sleep(15)