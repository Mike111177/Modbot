"""
Author Mike
"""

from queue import Queue
from threading import Thread
import traceback

global num
num = 0;

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

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.put((func, args, kargs))
        
    def kill(self):
        for i in range(0,len(self.threads)):
            t = self.threads[i]
            t.kill()
        self.threads = []