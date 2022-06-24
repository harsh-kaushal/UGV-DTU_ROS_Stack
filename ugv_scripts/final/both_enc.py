#!/usr/bin/env python
import threading
import math
import time

import rospy  
from sensor_msgs.msg import JointState
from diffbot_msgs.msg import EncodersStamped

import RPi.GPIO as GPIO

#Defining Pins for Reading left encoder

#Left
lsine = 37 # Brown
lcosine = 35 # Orange
lrevPin = 33 # Yellow

# Right
rsine = 36 # Brown
rcosine = 38 # Orange
rrevpin = 40 # Yellow

ldir = 0
lcount = 0
lrev_count = 0
lcurrent_rev_ind = 0
lprevious_rev_ind = 0
lcurrent_sine = 0
lprevious_sine = 0
lcurrent_cosine = 0

rdir = 0
rcount = 0
rrev_count = 0
rcurrent_rev_ind = 0
rprevious_rev_ind = 0
rcurrent_sine = 0
rprevious_sine = 0
rcurrent_cosine = 0

# For Deriving angular velocities

def init():
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(lsine,GPIO.IN)
	GPIO.setup(lcosine,GPIO.IN)	
	GPIO.setup(lrevPin,GPIO.IN)

	GPIO.setup(rsine,GPIO.IN)
	GPIO.setup(rcosine,GPIO.IN)	
	GPIO.setup(rrevpin,GPIO.IN)

def stop():
	GPIO.cleanup((lsine,lcosine,lrevPin,rsine,rcosine,rrevpin))

def read_Left_Enc():
	global lcount
	global lrev_count
	global lcurrent_sine
	global lprevious_sine
	global lcurrent_cosine
	global lcurrent_rev_ind
	global lprevious_rev_ind
	global ldir
	
	while not rospy.is_shutdown():

		lcurrent_sine = GPIO.input(lsine)
		lcurrent_cosine = GPIO.input(lcosine)
		lcurrent_rev_ind = GPIO.input(lrevPin)
		
		#--------------------Rev Counter------------------
		if lcurrent_rev_ind!=lprevious_rev_ind and lcurrent_rev_ind > lprevious_rev_ind:
			lrev_count -= ldir
			lcount = 0
			print("Left RevCount = ",lrev_count)
		lprevious_rev_ind = lcurrent_rev_ind

		#-------------------Pulse Counter-----------------
		if(lcurrent_sine > lcurrent_cosine):	ldir = 1
		if(lcurrent_sine < lcurrent_cosine):	ldir = -1
		
		if(lcurrent_sine!= lprevious_sine and lcurrent_sine > lprevious_sine):
			lcount += ldir
			print("Left count = ",lcount)
			print("=====================")
		lprevious_sine = lcurrent_sine

def read_Right_Enc():
	global rcount
	global rrev_count
	global rcurrent_sine
	global rprevious_sine
	global rcurrent_cosine
	global rcurrent_rev_ind
	global rprevious_rev_ind
	global rdir
	while not rospy.is_shutdown():

		rcurrent_sine = GPIO.input(rsine)
		rcurrent_cosine = GPIO.input(rcosine)
		rcurrent_rev_ind = GPIO.input(rrevpin)
		
		#--------------------Rev Counter------------------
		if rcurrent_rev_ind!=rprevious_rev_ind and rcurrent_rev_ind > rprevious_rev_ind:
			rrev_count -= rdir
			rcount = 0
			print("Right RevCount = ",rrev_count)
		rprevious_rev_ind = rcurrent_rev_ind

		#-------------------Pulse Counter-----------------
		if(rcurrent_sine > rcurrent_cosine):	rdir = 1
		if(rcurrent_sine < rcurrent_cosine):	rdir = -1
		
		if(rcurrent_sine!= rprevious_sine and rcurrent_sine > rprevious_sine):
			rcount += rdir
			print("Right count = ",rcount)
			print("=====================")
		rprevious_sine = rcurrent_sine


def pubToROS():
	global lcount
	global rcount

	prev_ang_pos = [0.0,0.0]

	ft = 0.0
	st = 0.0

	r = 10
	rate = rospy.Rate(r)
	while not rospy.is_shutdown():
		
		ft = time.time()
		
		n_lcount = lcount%1000
		n_rcount = rcount%1000

		#print("in pubToROS:",count)
		ang_pos = [(lrev_count + n_lcount/1000.0)*2*math.pi,(rrev_count + n_rcount/1000.0)*2*math.pi] # converted to radians
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


if __name__ == '__main__':
	
	try:
		init()
		
		rospy.init_node('js_n_ticks_writer', anonymous=False)
		#for constantly reading Left encoder GPIO 
		thread1 = threading.Thread(target=read_Left_Enc)
		thread1.start()
		thread2 = threading.Thread(target=read_Right_Enc)
		thread2.start()		
		#for publishing ticks at ros Rate
		thread3 = threading.Thread(target=pubToROS)
		thread3.start()

	except rospy.ROSInterruptException:
		print('stopped')			