#!/usr/bin/env python
import threading
import time
import signal

count = 0
def infiniteloop1():
    global count
    count +=1
    print('From Loop 1:',count)

    time.sleep(0.1)
    if count >999:
        count = 0

def infiniteloop2():
    global count
    print('----------------From Loop 2:',count)
    time.sleep(1)

class MyThread(threading.Thread):
    die = False
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run (self):
        global count
        if self.name == "1":
            while not self.die:
                infiniteloop1()
        
        if self.name == "2":
            while not self.die:
                infiniteloop2()
    
    def join(self):
        self.die = True
        super(MyThread, self).join()

if __name__ == '__main__':

    t1 = MyThread('1')
    t1.start()
    t2 = MyThread('2')
    t2.start()
    try:
        signal.pause()
    except KeyboardInterrupt:
        t1.join()
        t2.join()