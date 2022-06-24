#!/usr/bin/env python

from multiprocessing import Process
import multiprocessing , ctypes
import time
import signal  

import math
import rospy
from sensor_msgs.msg import JointState
from diffbot_msgs.msg import EncodersStamped

count = multiprocessing.Value(ctypes.c_int, 0)  # (type, init value)
rev_count = multiprocessing.Value(ctypes.c_int, 0)  # (type, init value)
poison = multiprocessing.Value(ctypes.c_bool,False) # To kill the processes while loops

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

def pubToROS(lcount,lrev_count,poison):

    ft = 0.0
    st = 0.0
    prev_ang_pos = [0.0,0.0]

    r = 10
    rate = rospy.Rate(r)
    while not poison:

        ft = time.time()

        n_lcount = lcount.value%1000
        n_rcount = lcount.value%1000
        rev_count = lrev_count.value
        
		#print("in pubToROS:",count)
        ang_pos = [(lrev_count + n_lcount/1000.0)*2*math.pi,(rev_count + n_rcount/1000.0)*2*math.pi] # converted to radians
        vel = [(ang_pos[0]-prev_ang_pos[0])/(ft-st),(ang_pos[1]-prev_ang_pos[1])/(ft-st)]

        #----------------------------------------------
        pubjs = rospy.Publisher('/diffbot/measured_joint_states', JointState, queue_size=1)
        joint_state = JointState()

        joint_state.name = ["left_wheel_joint","right_wheel_joint"]
        joint_state.header.stamp = rospy.Time.now()
        joint_state.position = ang_pos #msg.data
        joint_state.velocity = vel
        joint_state.effort = []
        pubjs.publish(joint_state)

        #----------------------------------------------
        pubticks = rospy.Publisher('/diffbot/encoder_ticks', EncodersStamped, queue_size=1)
        enc_stamped = EncodersStamped()

        enc_stamped.header.stamp = rospy.Time.now()
        enc_stamped.encoders.ticks = [n_lcount,n_rcount]
        pubticks.publish(enc_stamped) # this is questionable check without publishing this

        prev_ang_pos = ang_pos 
        st = time.time()

        rate.sleep()


if __name__ == "__main__":

    f1 = Process(target = infiniteloop1,args=(count,poison))
    f2 = Process(target = infiniteloop2,args=(count,poison))

    # Starting each process
    f1.start()
    f2.start()

    # Recieve the Ctrl + C interupt and send the response to manage_ctrlC function    
    signal.signal(signal.SIGINT, manage_ctrlC)

        


