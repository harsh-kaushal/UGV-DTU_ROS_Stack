#!/usr/bin/env python
import Queue as queue
import sys
import threading
import math
import time

import rospy  
from sensor_msgs.msg import JointState
#from std_msgs.msg import Int32
from diffbot_msgs.msg import EncodersStamped

import RPi.GPIO as GPIO

#Defining Pins for Reading
sine = 38 # White
cosine = 36 # Green
revPin = 40 # Yellow

dir = 0

count = 0
rev_count = 0

current_rev_ind = 0
previous_rev_ind = 0

current_sine = 0
previous_sine = 0
current_cosine = 0
previous_cosine = 0

prev_ang_pos = [0.0,0.0]

def init():

	GPIO.setmode(GPIO.BOARD)

	GPIO.setup(sine,GPIO.IN)
	GPIO.setup(cosine,GPIO.IN)	
	GPIO.setup(revPin,GPIO.IN)

def stop():
	GPIO.cleanup((sine,cosine,revPin))

def readGPIO():
	global count
	global rev_count
	global current_sine
	global previous_sine
	global current_cosine
	global previous_cosine
	global current_rev_ind
	global previous_rev_ind
	global dir
	while not rospy.is_shutdown():

		current_sine = GPIO.input(sine)
		current_cosine = GPIO.input(cosine)
		current_rev_ind = GPIO.input(revPin)
		#--------------------Rev Counter------------------
		if current_rev_ind!=previous_rev_ind and current_rev_ind > previous_rev_ind:
			rev_count -= dir
			count = 0

			print("RevCount = ",rev_count)

		previous_rev_ind = current_rev_ind
		#-------------------Pulse Counter-----------------
		if(current_sine > current_cosine):	dir = 1
		if(current_sine < current_cosine):  dir = -1
		
		if(current_sine!= previous_sine and current_sine > previous_sine):
			
			count += dir

			print("count = ",count)
			print("=====================")
		
		previous_sine = current_sine

right_q = queue.Queue()
left_q = queue.Queue()
right_sum = 0
left_sum = 0

def func(left_vel, right_vel, kernel=3):
    
    global right_sum, left_sum
    right_q.put(right_vel)
    left_q.put(left_vel)
    
    right_sum += right_vel
    left_sum += left_vel
    
    print(right_sum, left_sum)
    
    if(right_q.qsize() > kernel):
        num = right_q.get()
        right_sum -= num
        
        num = left_q.get()
        left_sum -= num
    
    
    return [left_sum/left_q.qsize(), right_sum/right_q.qsize()]

def pubToROS():
	global count
	global prev_ang_pos

	ft = 0.0
	st = 0.0

	r = 10
	rate = rospy.Rate(r)
	while not rospy.is_shutdown():
		
		ft = time.time()
		ncount = count%1000

		#print("in pubToROS:",count)
		ang_pos = [(rev_count + (ncount)/1000.0)*2*math.pi,(rev_count + (ncount)/1000.0)*2*math.pi] # converted to radians
		vel = [(ang_pos[0]-prev_ang_pos[0])/(ft-st),(ang_pos[1]-prev_ang_pos[1])/(ft-st)]
		#vel = func(vel[0],vel[1])
		#print(vel)

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
		enc_stamped.encoders.ticks = [(ncount),(ncount)]
		pubticks.publish(enc_stamped) # this is questionable check without publishing this

		prev_ang_pos = ang_pos 
		st = time.time()

		rate.sleep()


if __name__ == '__main__':
	
	try:
		init()
		
		rospy.init_node('js_n_ticks_writer', anonymous=False)
		#for constantly reading GPIO 
		thread1 = threading.Thread(target=readGPIO)
		thread1.start()
		#for publishing ticks at ros Rate
		thread2 = threading.Thread(target=pubToROS)
		thread2.start()

	except rospy.ROSInterruptException:
		print('stopped')
		sys.exit(1)				