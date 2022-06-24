#!/usr/bin/env python

from multiprocessing import Process
import multiprocessing , ctypes
import time

import signal  


count = multiprocessing.Value(ctypes.c_int, 0)  # (type, init value)
rev_count = multiprocessing.Value(ctypes.c_int, 0)  # (type, init value)
poison = multiprocessing.Value(ctypes.c_bool,False)

def manage_ctrlC(*args):

    poison.value = True
    time.sleep(0.1)
    # To let them finish one itter of while loop
    if f1.is_alive() or f2.is_alive(): time.sleep(1)
    print("Processes f1 running ",f1.is_alive())
    print("Processes f2 running ",f2.is_alive())

    f1.terminate()
    f2.terminate()
    # Joining each process so they end at the same time
    f1.join()
    f2.join()


def infiniteloop1(count,poison):
    while not poison.value:
        count.value +=1
        print('From Loop 1:',count.value)
        #print(multiprocessing.current_process().pid)
        time.sleep(0.1)
        if count.value >99:
            count.value = 0
            rev_count.value += 1

def infiniteloop2(count,poison):
    while not poison.value:
        print('----------------From Loop 2:',count.value)
        #print(multiprocessing.current_process().pid)
        time.sleep(1)


if __name__ == "__main__":

    f1 = Process(target = infiniteloop1,args=(count,poison))
    f2 = Process(target = infiniteloop2,args=(count,poison))

    # Starting each process
    f1.start()
    f2.start()

    # Recieve the Ctrl + C interupt and send the response to manage_ctrlC function    
    signal.signal(signal.SIGINT, manage_ctrlC)

        


