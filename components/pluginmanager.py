import os, sys
from imp import reload
from components import abstracts
from lib import threadpool


plugins = {}
mods = {}
resources = {}

handlers = {}
prio=range(0,5)

pool = threadpool.ThreadPool(5, "Tasker")

def initialize():
    for f in os.listdir("plugins/"):
        fname, ext = os.path.splitext(f)
        if ext == '.py':
            loadPlugin(fname)
            
def loadPlugin(name):
    sys.path.insert(0, "plugins/")
    mod = __import__(name)
    registerPlugin(mod, name)
    sys.path.pop(0)
    
def addresource(name, resource):
    resource[name]=resource
    
def registerPlugin(mod, name):
    try:
        mod = reload(mod)
        if issubclass(mod.Plugin, abstracts.Plugin):
            plug = mod.Plugin()
            mods[plug] = mod
            plugins[name] = plug
            for han in plug.handlers():
                addHandler(han)
        else:
            print(name + " is an invalid plugin!")
    except Exception as e: 
        print(name + " has errors on loading! "  + str(e))
        
def addHandler(handler):
    if handler.event not in handlers:
        handlers[handler.event]={0:[],1:[],2:[],3:[],4:[]}
    handlers[handler.event][handler.priority].append(handler)
    
def runEvent(event, *args, **kargs):
    pool.add_task(eventtask, event, args, kargs)
    
def eventtask(event, args, kargs):
    if event in handlers:
        ehandlers = handlers[event]
        for x in prio:
            for handler in ehandlers[x]:
                if handler.handle(args, kargs):
                    return