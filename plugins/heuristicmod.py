import traceback, asyncio, re
from components import abstracts, pluginmanager, config
from math import floor
from datetime import timedelta, datetime
from socket import gethostbyname_ex as checkhost
from urllib.parse import urlparse
from time import clock, sleep
from threading import Lock

defaults = {"Reporting": {"AutoChannel": "", "ManualChannel": ""}, "SpecialCase": {"Regex": ""}, "Timeout_Logging":{"Ignore_Bots":"True"}}
cfg = config.load("heuristicmod", defaults)

rlinkstring = '(?:(?:[a-z0-9$-_@.&+]{1,256})\.)+[a-z]{2,6}'
nbotpstr = '[a-zA-Z0-9]{1,25}\s->\s(?P<Name>[a-zA-Z0-9]{1,25})\shas\sbeen\sgranted\spermission\sto\spost\sa\slink\sfor\s60\sseconds\.'
regflink = re.compile("@LINK@")
regperm = re.compile(nbotpstr)
regspecial = re.compile(str(cfg["SpecialCase"]["Regex"]), re.IGNORECASE)
reglink = re.compile(rlinkstring, re.IGNORECASE)

permitcache = {}

def containsFailedLink(message):
    if regflink.search(message):
        return True
    else:
        return False

def containsLink(message):
    links = reglink.findall(message)
    result = False
    if links:
        for x in links:
            try:
                if not x.startswith('http'): x = 'http://'+x
                url = urlparse(x)
                checkhost(url.hostname)
                result = True
                break
            except:
                continue
    return result

def isNoob(name, cid):
    age = pluginmanager.plugins['twitchapi'].getUser(name=name).getUserAge()
    return age<43200, age

def containsSpecial(message):
    if cfg["SpecialCase"]["Regex"]!='' and regspecial.search(message):
        return True
    else:
        return False

def isSpamBot(name, message, cid):
    if name.lower()=='nightbot':
        me = regperm.match(message)
        if me:
            permitcache[me.group('Name').lower()] = clock()
        return False, False, None
    
    if name.lower() in permitcache and clock()-permitcache[name.lower()]<300:
        links = False
    else:
        links = containsLink(message) or containsFailedLink(message)
        
        
    addr = containsSpecial(message)
    if links or addr:
        noob, age = isNoob(name, cid)
        if noob:
            return True, addr, age
    return False, False, None

class Plugin(abstracts.Plugin):
    
    def __init__(self):
        self.msglock = Lock()
        self.msglog = {}
        self.refreshtime = clock()
    
    def handlers(self):
        return [abstracts.Handler('TWITCH:MSG', self, self.ircmsg),
                abstracts.Handler('DSC:COMMAND:?BANCOUNT', self, self.bancnt),
                abstracts.Handler('TWITCH:MOD:TIMEOUT', self, self.timeout)]
    
    def timeout(self, created_by=None, args=None, **kw):
        if not (created_by.lower()=='nightbot' and cfg['Timeout_Logging']['Ignore_Bots'].lower()=='true'):
            sleep(.5) #10 Threads in the pool, not concerned. Go away with your best practices.
            bot = pluginmanager.resources["DSC"]["BOT"]
            loop = pluginmanager.resources["DSC"]["LOOP"]
            message = '`%s` timed out `%s` for `%s` seconds.'%(created_by,args[0],args[1])
            if len(args)>2:
                message = message + " Reason: `%s`"%args[2].replace('`','\'')
            with self.msglock:
                if args[0] in self.msglog:
                    message = message + " ```%s: %s```"%(args[0],self.msglog[args[0]].replace('`','\''))
            asyncio.run_coroutine_threadsafe(bot.send_message(bot.get_channel(str(cfg['Reporting']['ManualChannel'])),message), loop)
    
    def ircmsg(self, nick=None, target=None, data=None, **kw):
        cid = pluginmanager.resources["TWITCH"]["CLI-ID"]
        try:
            t = clock()
            spam, special, age = isSpamBot(nick, data, cid)
            if spam:
                bot = pluginmanager.resources["TWITCH"]["BOT"]
                disbot = pluginmanager.resources["DSC"]["BOT"]
                loop = pluginmanager.resources["DSC"]["LOOP"]
                bot.privmsg(target, '.ban %s'%nick)
                if not special:
                    bot.privmsg(target, '.w %s Hello %s, you have been banned from this chat by our new experimental heuristics system. If you believe that you were wrongfully banned and would like to appeal please whisper one of the chat moderators. We are sorry for the inconvienence.'%(nick, nick))
                    bot.privmsg(target, '.w %s Do not reply to this whisper.'%nick)
                asyncio.run_coroutine_threadsafe(disbot.send_message(disbot.get_channel(str(cfg['Reporting']['AutoChannel'])),'%s: "%s" (Age: %s) (Special: %s) [%fs]'%(nick,data,str(timedelta(seconds=floor(age))),str(special),clock()-t)), loop)
        except:
            print('Error in spambot filter.\nUser: %s\nMessage: "%s"'%(nick,data))
            print(traceback.format_exc())
        with self.msglock:
            if clock()-self.refreshtime>43200:
                self.msglog = {}
            self.msglog[nick] = data
        
        
    def bancnt(self, message=None, args=None, **kw):
        disbot = pluginmanager.resources["DSC"]["BOT"]
        loop = pluginmanager.resources["DSC"]["LOOP"]
        asyncio.run_coroutine_threadsafe(disbot.send_typing(message.channel), loop)
        dtime = 1
        if len(args)>0:
            try:
                dtime = float(args[0])
            except:
                dtime = 1
        asyncio.run_coroutine_threadsafe(self.bancount(disbot, message.channel, dtime),loop)
                
                      
    async def bancount(self, disbot, channel, dtime):
        counter = 0
        async for m in disbot.logs_from(disbot.get_channel(str(cfg['Reporting']['AutoChannel'])), limit=500, after=(datetime.utcnow()-timedelta(hours=dtime))):
            if m.author == disbot.user:
                counter += 1
        await disbot.send_message(channel, 'There have been %d automated bans in the past %s hour(s).'%(counter, dtime))