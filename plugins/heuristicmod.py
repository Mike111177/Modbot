import traceback, asyncio, re, argparse, pickle
from components import abstracts, pluginmanager, config
from math import floor
from datetime import timedelta, datetime
from socket import gethostbyname_ex as checkhost
from urllib.parse import urlparse
from time import clock, sleep
from threading import Lock
from discord import MessageType

defaults = {"Reporting": {"Channel": ""}, "SpecialCase": {"Regex": ""}, "Timeout_Logging":{"Ignore_Bots":"True"}}
cfg = config.load("heuristicmod", defaults)

rlinkstring = '(?:(?:[a-z0-9$-_@.&+]{1,256})\.)+[a-z]{2,6}'
permitstr = '^!permit\s\@?(?P<nick>[^\s]+)'
regperm = re.compile(permitstr)
regspecial = re.compile(str(cfg["SpecialCase"]["Regex"]), re.IGNORECASE)
reglink = re.compile(rlinkstring, re.IGNORECASE)

permitcache = {}

revokeparse = argparse.ArgumentParser(description='Manage users revoked from posting links.', add_help=False, prog='?revoke')
subparsers = revokeparse.add_subparsers(dest='cmd')
addparse = subparsers.add_parser('add', help='Add a user to revoke list.')
addparse.add_argument('user', type=str, help='The user.')
remparse = subparsers.add_parser('remove', help='Remove a user to revoke list.')
remparse.add_argument('user', type=str, help='The user.')
subparsers.add_parser('list', help='List the users on the revoke list.')

def saveRevokeList():
    with open(revokelistname, 'wb') as output:
        pickle.dump(revokelist, output)
revokelistname="data/revokelist"
try:
    with open(revokelistname, 'rb') as file:
        revokelist = pickle.load(file)
except:
    revokelist = set()
    saveRevokeList()

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
    return age<21600, age

def containsSpecial(message):
    if cfg["SpecialCase"]["Regex"]!='' and regspecial.search(message):
        return True
    else:
        return False
    
def permitCheck(name):
    return name.lower() in permitcache and clock()-permitcache[name.lower()]<70

def isSpamBot(name, message, cid):
    if permitCheck(name):
        links = False
    else:
        links = containsLink(message)
        
    addr = containsSpecial(message)
    if links or addr:
        noob, age = isNoob(name, cid)
        if noob:
            return True, age
    return False, None

class Plugin(abstracts.Plugin):
    
    def __init__(self):
        self.msglock = Lock()
        self.msglog = {}
        self.refreshtime = clock()
        self.rejectmsg = {}
        self.rejectmsglock = Lock()
        self.pinlock = Lock()
        self.pins = {}
    
    def handlers(self):
        return [abstracts.Handler('TWITCH:MSG', self, self.ircmsg),
                abstracts.Handler('DSC:COMMAND:?REVOKE', self, self.revoke, parse=revokeparse),
                abstracts.Handler('TWITCH:MOD:TWITCHBOT_REJECTED', self, self.twitchbot_rejected),
                abstracts.Handler("DSC:MSG", self, self.logmessage),
                abstracts.Handler('TWITCH:MOD', self, self.mod_action, priority=abstracts.Handler.PRIORITY_MIN)]

    
    def lastmsg(self, user, set=None):
        with self.msglock:
            if clock()-self.refreshtime>43200:
                self.msglog = {}
                self.refreshtime = clock()
            if set:
                self.msglog[user] = set
            return self.msglog.get(user)
    
    def mod_action(self, moderation_action=None, **kw):
        bot = pluginmanager.resources["DSC"]["BOT"]
        loop = pluginmanager.resources["DSC"]["LOOP"]
        message = None
        if moderation_action=='twitchbot_rejected':
            sleep(30)
            with self.rejectmsglock:
                if kw['msg_id'] in self.rejectmsg:
                    user=kw['args'][0]
                    userid = pluginmanager.plugins['twitchapi'].getUser(name=user).getUserID()
                    message = '`%s (%s)`:```%s````Denied` by `%s`'%(user, userid, self.lastmsg(user, kw['args'][1]), self.rejectmsg.pop(kw['msg_id']))
        elif moderation_action=='denied_twitchbot_message':
            if not kw['created_by'].lower()==pluginmanager.plugins['twitchconnector'].nick().lower():
                with self.rejectmsglock:
                    self.rejectmsg[kw['msg_id']]=kw['created_by']
        elif moderation_action=='timeout':
            if not (kw['created_by'].lower()=='nightbot' and cfg['Timeout_Logging']['Ignore_Bots'].lower()=='true'):
                sleep(.5)
                user = kw['args'][0]
                userid = kw['target_user_id']
                message = '`%s (%s)`:```%s````Timed out (%ss)` by `%s`'%(user, userid, self.lastmsg(user), kw['args'][1], kw['created_by'])
                if len(kw['args'])>2:
                    message = message + " Reason: `%s`"%kw['args'][2].replace('`','\'')
        elif moderation_action=='ban':
            sleep(.5)
            user = kw['args'][0]
            userid = kw['target_user_id']
            message = '`%s (%s)`:```%s````Banned` by `%s`'%(user, userid, self.lastmsg(user), kw['created_by'])
            if len(kw['args'])>1:
                message = message + " Reason: `%s`"%kw['args'][1].replace('`','\'')
        if message:    
            asyncio.run_coroutine_threadsafe(bot.send_message(bot.get_channel(str(cfg['Reporting']['Channel'])),str(message)), loop)
    
    def twitchbot_rejected(self, msg_id=None, args=None, twitchchannel=None, **kw):
        if self.ircmsg(nick=args[0], target=twitchchannel, data=args[1]):
            pluginmanager.plugins['twitchapi'].denyMessage(msg_id)
    
    def ircmsg(self, nick=None, target=None, data=None, **kw):
        cid = pluginmanager.resources["TWITCH"]["CLI-ID"]
        if 'tags' in kw and 'mod' in kw['tags'] and kw['tags']['mod']=='1':
            me = regperm.match(data)
            if me:
                permitcache[me.group('nick').lower()] = clock()
            return False
        try:
            if not permitCheck(nick):
                spam, age = isSpamBot(nick, data, cid)
                if spam:
                    bot = pluginmanager.resources["TWITCH"]["BOT"]
                    bot.privmsg(target, '.ban %s Spambot Detected'%nick)
                elif nick.lower() in revokelist and containsLink(data):
                    bot = pluginmanager.resources["TWITCH"]["BOT"]
                    bot.privmsg(target, '.timeout %s 60 Link privileges revoked'%nick)                
        except:
            print('Error in spambot filter.\nUser: %s\nMessage: "%s"'%(nick,data))
            print(traceback.format_exc())
        self.lastmsg(nick, data)
            
    def logmessage(self, message):
        bot = pluginmanager.resources["DSC"]["BOT"]
        loop = pluginmanager.resources["DSC"]["LOOP"]
        if str(message.channel.id)==cfg['Reporting']['Channel'] and message.author!=bot.user:
            if message.type==MessageType.pins_add:
                pinned_messages = asyncio.run_coroutine_threadsafe(bot.pins_from(message.channel), loop).result()
                with self.pinlock:
                    self.pins[message.author] = pinned_messages[0]
                    for msg in pinned_messages:
                        unused=True
                        for user in self.pins:
                            if msg==self.pins[user]:
                                unused=False
                        if unused:
                            asyncio.run_coroutine_threadsafe(bot.unpin_message(msg), loop)
            elif message.type==MessageType.default:
                with self.pinlock:
                    if message.author in self.pins:
                        msg = self.pins.pop(message.author)
                        asyncio.run_coroutine_threadsafe(bot.edit_message(msg, new_content=msg.content+' `(%s)`'%message.content), loop)
                        asyncio.run_coroutine_threadsafe(bot.unpin_message(msg), loop)
            asyncio.run_coroutine_threadsafe(bot.delete_message(message), loop)
        
        
    def revoke(self, message=None, pargs=None,**kw):
        msg = None
        if pargs['cmd']=='list':
            msg = '```'+str(list(revokelist))+'```'
        elif pargs['cmd']=='add':
            revokelist.add(pargs['user'].lower())
            saveRevokeList()
            msg = '%s is now on the revoke list.'%pargs['user']
        elif pargs['cmd']=='remove':
            revokelist.remove(pargs['user'].lower())
            saveRevokeList()
            msg = '%s is now not on the revoke list.'%pargs['user']
        if msg:
            bot = pluginmanager.resources["DSC"]["BOT"]
            loop = pluginmanager.resources["DSC"]["LOOP"]
            asyncio.run_coroutine_threadsafe(bot.send_message(message.channel, msg), loop)