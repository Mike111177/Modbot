import os, sys, traceback
from imp import reload
from components import abstracts
from lib import threadpool

plugins = {}
mods = {}
resources = {}

handlers = {}
prio=range(0,5)

pool = threadpool.ThreadPool(10, "Event Dispatch")

def initialize():
    for f in os.listdir("plugins/"):
        fname, ext = os.path.splitext(f)
        if ext == '.py':
            loadPlugin(fname)
    for plug in plugins:
        plugins[plug].load()
    
            
def loadPlugin(name):
    sys.path.insert(0, "plugins/")
    mod = __import__(name)
    registerPlugin(mod, name)
    sys.path.pop(0)
    
def addresource(name, resource):
    resources[name]=resource
    
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
        traceback.print_exc()
        
def unloadPlugin(name):
    if name in plugins:
        plug = plugins.pop(name)
        for event in handlers:
            for pri in handlers[event]:
                handlers[event][pri]=list(filter((lambda x: x.plugin is not plug),handlers[event][pri]))
        cleanHandlers()
        mod = mods.pop(plug)
        plug.unload()
        del plug
        return mod
    return None

def reloadPlugin(name):
    unloadPlugin(name)
    loadPlugin(name)
    plugins[name].load()
        
def addHandler(handler):
    if handler.event not in handlers:
        handlers[handler.event]={0:[],1:[],2:[],3:[],4:[]}
    handlers[handler.event][handler.priority].append(handler)
    
def cleanHandlers():
    empty = []
    for event in handlers:
        e = True
        for pri in handlers[event]:
            if len(handlers[event][pri]) != 0:
                e = False
                break
        if e:
            empty.append(event)
    for event in empty:
        handlers.pop(event)
    
def runEvent(event, *args, **kargs):
    pool.add_task(eventtask, event, args, kargs)
    
def eventtask(event, args, kargs):
    if event in handlers:
        ehandlers = handlers[event]
        for x in prio:
            for handler in ehandlers[x]:
                if handler.handle(args, kargs):
                    return