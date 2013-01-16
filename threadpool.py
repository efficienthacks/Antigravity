from socket import gethostbyaddr
from threading import *
import thread
from Queue import *

lock = thread.allocate_lock()	#for printing to be atomic
def doTask(q, myMethod):
      while True:
            params = q.get()
            myMethod(*params)
            q.task_done()

class ThreadPool:
    def __init__(self, theMethod, numthreads = 400):
        self.myMethod = theMethod
        self.numthreads = numthreads
        self.q = Queue(numthreads*2)
        
    def __startThreadPoolOnly(self):
        for i in range(self.numthreads):
            t = Thread(target=doTask, args=(self.q, self.myMethod))
            t.setDaemon(True)
            t.start()
    
    #These are the 2 ways to start the thread pool:
    #1: provide a list of lists
        #argsToMethod has format: [ [1,2], [3,4], [5,6], [7,8] ]
        #Threadpool will launch these in seperate threads: theMethod(1,2), theMethod(3,4)... etc.
    def startThreadPoolWithArgs(self, argsToMethod = []):
        self.__startThreadPoolOnly()        
        for i in argsToMethod:
            self.q.put(i)
        self.q.join()	
    
    #2: provide a method that takes in a queue and puts the arguments in it
    #addTasksTo will add tasks to the queue (tasks are added as lists with length == #args for self.myMethod)
    def startThreadPoolWithDynamicTask(self, addTasksTo):
        self.__startThreadPoolOnly()        
        addTasksTo(self.q)
        self.q.join()	#wait for all threads to finish

