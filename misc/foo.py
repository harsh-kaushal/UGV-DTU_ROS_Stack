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
rrevPin = 40 # Yellow

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
	GPIO.setup(rrevPin,GPIO.IN)

def stop():
	GPIO.cleanup((lsine,lcosine,lrevPin,rsine,rcosine,rrevPin))

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
		rcurrent_rev_ind = GPIO.input(rrevPin)
		
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

if __name__ == '__main__':
    try:
        GPIO.cleanup()
        init()
        thread1 = threading.Thread(target=read_Left_Enc)
        thread1.start()
        thread2 = threading.Thread(target=read_Right_Enc)
        thread2.start()	

    except KeyboardInterrupt:
        stop()
        print('stopped')