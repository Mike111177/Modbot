import threading, pickle, twitch
from datetime import datetime, timezone


class Checker(threading.Thread):
    
    def __init__(self, uname,dtime,ntime,cid):
        self.cid = cid
        self.uname = uname
        self.noob = True
        self.dname = uname
        self.dtime = dtime
        self.ntime = ntime
        threading.Thread.__init__(self, name="Check Time: %s"%uname)
        self.start()
        
    def run(self):
        try:
            data = twitch.getUserData(self.uname, self.cid)
            self.dname = data['display_name']
            if not ((self.ntime-getUserDate(data)).total_seconds()<(self.dtime)):
                self.noob = False
        except:
            return

def getUserDate(data):
    return datetime.strptime(data['created_at'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

def getUserAge(date):
    return (datetime.now(tz=timezone.utc)-date).total_seconds()
    
def getNooblist(channel, cid):
    name = channel.lstrip('#')
    
    cachename = "days.cache"
    
    try:
        pkl_file = open(cachename, 'rb')
        clearedlist = pickle.load(pkl_file)
        pkl_file.close()
    except:
        clearedlist=[]
    
    now = datetime.now(tz=timezone.utc)
    chatlist = twitch.getChatters(name)
    threadlist = []
    
    for user in chatlist:
        if user not in clearedlist:
            threadlist.append(Checker(user,43200,now,cid))
    
    nooblist = []
    
    for thread in threadlist:
        thread.join()
        if thread.noob:
            nooblist.append(thread.dname)
        else:
            clearedlist.append(thread.uname)
    
    output = open(cachename, 'wb')
    pickle.dump(clearedlist, output)
    output.close()

    return nooblist