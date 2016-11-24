"""
Author Mike
"""
import traceback
from queue import Queue
from threading import Thread, Lock
from time import sleep


global num
num = 0;

def sleepLock(time, lock,locked):
    if not locked:
        lock.acquire()
    sleep(time)
    try:
        lock.release()
    except:
        pass

def getNum():
    global num
    num = num + 1
    return str(num)

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        Thread.__init__(self, name = tasks.name + ":T"+str(len(tasks.threads)+1))
        self.tasks = tasks
        self.daemon = True
        self.go = True
        self.start()
    
    def run(self):
        while self.go:
            func, args, kargs = self.tasks.get()
            try: func(*args, **kargs)
            except: traceback.print_exc()
            finally: self.tasks.task_done()
            
    def kill(self):
        self.go = False

class ThreadPool(Queue):
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads, name="ThreadPool-" + getNum()):
        super().__init__()
        self.threads = []
        self.name = name
        for _ in range(num_threads): 
            self.threads.append(Worker(self))
            
    def interuptableSleep(self, time, lock,locked=False):
        self.add_task(sleepLock,time,lock,locked)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.put((func, args, kargs))
        
    def list(self, func, arglist):
        runners = []
        for x in arglist:
            runner = Container(func,x)
            self.add_task(runner.exe)
            runners.append(runner)
        results = []
        for x in runners:
            results.append(x.getResult())
        return results
        
    def kill(self):
        for i in range(0,len(self.threads)):
            t = self.threads[i]
            t.kill()
        self.threads = []
        
class Container(object):
    
    def __init__(self, func, *args, **kargs):
        self.func = func
        self.args = args
        self.kargs = kargs
        self.lock = Lock()
        self.lock.acquire()
        
    def exe(self):
        try:
            self.res = self.func(*self.args, **self.kargs)
        except:
            self.res = None
        finally:
            self.lock.release()
        
    def getResult(self):
        self.lock.acquire()
        self.lock.release()
        return self.res