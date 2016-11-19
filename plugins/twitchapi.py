from components import abstracts, config
import json
from urllib import request
from datetime import datetime, timezone

defaults = {"Twitch": {"Client-ID": ""}}
cfg = config.load("twitchapi", defaults)
cid = str(cfg["Twitch"]["Client-ID"])

VERSION2 = 'application/vnd.twitchtv.v2+json'
VERSION3 = 'application/vnd.twitchtv.v3+json'
VERSION5 = 'application/vnd.twitchtv.v5+json'

def getUserData(name=None,userid=None):
    if userid:
        uid = userid
        ver = VERSION5
    elif name:
        uid = name
        ver = VERSION3
    else:
        return None
    try:
        req = request.Request("https://api.twitch.tv/kraken/users/%s"%uid,  headers={'Client-ID': cid, 'Accept': ver}) #LOOK AT ME IM TWITCH! I REQUIRE A FUCKING CLIENT ID NOW TO USE MY API
        return json.loads(request.urlopen(req).read().decode())
    except Exception as e:
        print(e)
        try:
            req = request.Request("https://api.twitch.tv/kraken/users/%s"%uid,  headers={'Client-ID': cid,'Accept': ver})
            return json.loads(request.urlopen(req).read().decode())
        except:
            return None
        
def getChannelData(name=None,userid=None):
    if userid:
        uid = userid
        ver = VERSION5
    elif name:
        uid = name
        ver = VERSION3
    else:
        return None
    try:
        req = request.Request("https://api.twitch.tv/kraken/channels/%s"%uid,  headers={'Client-ID': cid, 'Accept': ver}) #LOOK AT ME IM TWITCH! I REQUIRE A FUCKING CLIENT ID NOW TO USE MY API
        return json.loads(request.urlopen(req).read().decode())
    except Exception as e:
        print(e)
        try:
            req = request.Request("https://api.twitch.tv/kraken/channels/%s"%uid,  headers={'Client-ID': cid,'Accept': ver})
            return json.loads(request.urlopen(req).read().decode())
        except:
            return None
        
def parseDate(datestr):
    return datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

class Plugin(abstracts.Plugin):
    
    def getUser(self, **kw):
        return TwitchUser(**kw)
    
    def getChannel(self, **kw):
        return TwitchChannel(**kw)
        
        
class TwitchUser(object):
    
    def __init__(self, userid=None, name=None, displayname=None, acd=None, acds=None, utype=None, retrieve=False, **k):
        self.userid=userid
        self.name=name
        self.displayname = displayname
        if not name:
            self.name=displayname.lower()
        self.utype=utype
        if acd:
            self.acd = acd
        elif acds:
            self.acd = parseDate(acds)
        else:
            self.acd = None
        if retrieve:
            self.__retrieve__()
    
    def __retrieve__(self):
        try:
            data = getUserData(self.name, self.userid)
            self.name=data['name']
            self.userid=data['_id']
            self.displayname=data['display_name']
            self.acd=parseDate(data['created_at'])
        except:
            pass
    
    def getACD(self):
        if self.acd:
            return self.acd
        else:
            self.__retrieve__()
            return self.acd
        
    def getUserID(self):
        if self.userid:
            return self.userid
        else:
            self.__retrieve__()
            return self.userid
        
    def getUserAge(self):
        return (datetime.now(tz=timezone.utc)-self.getACD()).total_seconds()
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        if self.displayname:
            return "TwitchUser('%s')"%self.displayname
        elif self.name:
            return "TwitchUser('%s')"%self.name
        elif self.userid:
            return "TwitchUser(%d)"%self.userid
        else:
            return "TwitchUser()"
        
class TwitchChannel(object):
    
    def __init__(self, userid=None, name=None, retrieve=False, **k):
        self.userid=userid
        self.name=name
        if retrieve:
            self.__retrieve__()
    
    def __retrieve__(self):
        try:
            data = getChannelData(self.name, self.userid)
        except:
            pass
        
    def getUserID(self):
        if self.userid:
            return self.userid
        else:
            self.__retrieve__()
            return self.userid
        
    def getChatters(self):
        return json.loads((request.urlopen("http://tmi.twitch.tv/group/user/%s/chatters"%self.name).read().decode("utf-8")))["chatters"]["viewers"]
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        if self.name:
            return "TwitchUser('%s')"%self.name
        elif self.userid:
            return "TwitchUser(%d)"%self.userid
        else:
            return "TwitchUser()"
        