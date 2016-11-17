from components import abstracts, pluginmanager, config
from math import floor
from datetime import timedelta, datetime
import traceback, asyncio, re
import chatanalytics as nooblist
from socket import gethostbyname_ex as checkhost
from urllib.parse import urlparse
from time import clock

defaults = {"Reporting": {"Channel": ""}}
cfg = config.load("heuristicmod", defaults)

rlinkstring = '(?:(?:[a-z0-9$-_@.&+]{1,256})\.)+[a-z]{2,6}'
nbotpstr = '[a-zA-Z0-9]{1,25}\s->\s(?P<Name>[a-zA-Z0-9]{1,25})\shas\sbeen\sgranted\spermission\sto\spost\sa\slink\sfor\s60\sseconds\.'
regperm = re.compile(nbotpstr)
regaddr = re.compile('02481', re.IGNORECASE)
reglink = re.compile(rlinkstring, re.IGNORECASE)

permitcache = {}

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
    age = nooblist.getUserAge(nooblist.getUserDate(nooblist.getUserData(name, cid)))
    return age<43200, age

def containsAddress(message):
    if regaddr.search(message):
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
        links = containsLink(message)
        
        
    addr = containsAddress(message)
    if links or addr:
        noob, age = isNoob(name, cid)
        if noob:
            return True, addr, age
    return False, False, None

class Plugin(abstracts.Plugin):
    
    def handlers(self):
        return [abstracts.Handler('TWITCH:MSG', self, self.ircmsg),
                abstracts.Handler('DSC:MSG', self, self.dismsg)]
    
    def ircmsg(self, nick=None, target=None, data=None, **kw):
        cid = pluginmanager.resources["TWITCH"]["CLI-ID"]
        try:
            spam, special, age = isSpamBot(nick, data, cid)
            if spam:
                bot = pluginmanager.resources["TWITCH"]["BOT"]
                disbot = pluginmanager.resources["DSC"]["BOT"]
                loop = pluginmanager.resources["DSC"]["LOOP"]
                bot.privmsg(target, '.ban %s'%nick)
                if not special:
                    bot.privmsg(target, '.w %s Hello %s, you have been banned from this chat by our new experimental heuristics system. If you believe that you were wrongfully banned and would like to appeal please whisper one of the chat moderators. We are sorry for the inconvienence.'%(nick, nick))
                    bot.privmsg(target, '.w %s Do not reply to this whisper.'%nick)
                asyncio.run_coroutine_threadsafe(disbot.send_message(disbot.get_channel(str(cfg['Reporting']['Channel'])),'%s: "%s" (Age: %s) (Special: %s)'%(nick,data,str(timedelta(seconds=floor(age))),str(special))), loop)
        except:
            print('Error in spambot filter.\nUser: %s\nMessage: "%s"'%(nick,data))
            print(traceback.format_exc())
            return
        
    def dismsg(self, message):
        if message.content.startswith('?bancount'):
            disbot = pluginmanager.resources["DSC"]["BOT"]
            loop = pluginmanager.resources["DSC"]["LOOP"]
            args = str(message.content).split(' ')
            dtime = 1
            if len(args)>1:
                try:
                    dtime = float(args[1])
                except:
                    dtime = 1
            asyncio.run_coroutine_threadsafe(self.bancount(disbot, message.channel, dtime),loop)
                      
    async def bancount(self, disbot, channel, dtime):
        counter = 0
        async for m in disbot.logs_from(disbot.get_channel(str(cfg['Reporting']['Channel'])), limit=500, after=(datetime.utcnow()-timedelta(hours=dtime))):
            if m.author == disbot.user:
                counter += 1
        await disbot.send_message(channel, 'There have been %d automated bans in the past %s hour(s).'%(counter, dtime))
            
            
            
            
            
            
            