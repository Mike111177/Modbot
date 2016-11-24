import json, traceback
from components import abstracts, config
from urllib import request
from datetime import datetime, timezone

defaults = {"Twitch": {"Client-ID": ""}}
cfg = config.load("twitchapi", defaults)
cid = str(cfg["Twitch"]["Client-ID"])

VERSION2 = 'application/vnd.twitchtv.v2+json'
VERSION3 = 'application/vnd.twitchtv.v3+json'
VERSION5 = 'application/vnd.twitchtv.v5+json'

def doubleJSONRequestTry(url, headers=None):
    try:
        req = request.Request(url, headers=headers)
        return json.loads(request.urlopen(req).read().decode())
    except:
        try:
            req = request.Request(url,headers=headers)
            return json.loads(request.urlopen(req).read().decode())
        except:
            return None

def getUserData(user):
    try:
        if user.userid:
            return doubleJSONRequestTry("https://api.twitch.tv/kraken/users/%s"%user.userid,  headers={'Client-ID': cid, 'Accept': VERSION5})
        elif user.name:
            return doubleJSONRequestTry("https://api.twitch.tv/kraken/users?login=%s"%user.name,  headers={'Client-ID': cid, 'Accept': VERSION5})['users'][0]
        else:
            return None
    except:
        return None
        
def getChannelData(channel):
    try:
        return doubleJSONRequestTry("https://api.twitch.tv/kraken/channels/%s"%channel.getUserID(),  headers={'Client-ID': cid, 'Accept': VERSION5})
    except:
        traceback.print_exc()
        return None
           
def getFollowData(user, channel):
    try:
        return doubleJSONRequestTry("https://api.twitch.tv/kraken/users/%s/follows/channels/%s"%(user.getUserID(), channel.getUserID()),  headers={'Client-ID': cid, 'Accept': VERSION5})
    except:
        traceback.print_exc()
        return None
        
        
def parseDate(datestr):
    return datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

class Plugin(abstracts.Plugin):
    
    def getUser(self, **kw):
        return TwitchUser(**kw)
    
    def getChannel(self, **kw):
        return TwitchChannel(**kw)
        
        
class TwitchUser(object):
    
    def __init__(self, userid=None, name=None, utype=None, retrieve=False, **k):
        self.userid=userid
        self.name=name
        self.displayname = None
        self.utype=utype
        self.acd = None
        if retrieve:
            self.__retrieve__()
    
    def __retrieve__(self):
        try:
            data = getUserData(self)
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
        
    def getUserName(self):
        if self.name:
            return self.name
        else:
            self.__retrieve__()
            return self.name
        
    def getUserAge(self):
        acd = self.getACD()
        if acd:
            return (datetime.now(tz=timezone.utc)-acd).total_seconds()
        else:
            return None
    
    def getFollowDate(self, channel):
        data = getFollowData(self, channel)
        if data and 'created_at' in data:
            return parseDate(data['created_at'])
        else:
            return None
    
    def getFollowAge(self, channel):#Seeing how long this user has been following a channel
        date = self.getFollowDate(channel)
        if date:
            return (datetime.now(tz=timezone.utc)-date).total_seconds()
        else:
            return None
                    
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
        
class TwitchChannel(TwitchUser):
    
    def __init__(self, userid=None, name=None, retrieve=False, **k):
        TwitchUser.__init__(self, userid=userid, name=name, retrieve=retrieve, **k)
    
    def __retrieve__(self):
        TwitchUser.__retrieve__(self)
        
    def getChatters(self):
        return json.loads((request.urlopen("http://tmi.twitch.tv/group/user/%s/chatters"%self.getUserName()).read().decode("utf-8")))["chatters"]["viewers"]
    
    def getFollowAge(self, user): #Seeing how long a user has been followed to this channel.
        return TwitchUser.getFollowAge(user, self)
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        if self.name:
            return "TwitchChannel('%s')"%self.name
        elif self.userid:
            return "TwitchChannel(%d)"%self.userid
        else:
            return "Channel()"
        