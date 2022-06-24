#!/usr/bin/env python

import sys
import threading
import math
import time

import rospy  
from sensor_msgs.msg import JointState
#from std_msgs.msg import Int32
from diffbot_msgs.msg import EncodersStamped

count = 0
prev_ang_pos = [0.0,0.0]
def readGPIO():
    global count
    while not rospy.is_shutdown():
        count +=1
        #print('From Loop 1:',count)

        time.sleep(0.01)
        # if count >999:
        #     count = 0

def pubToROS():
	global count
	global prev_ang_pos

	r = 100
	rate = rospy.Rate(r)
	while not rospy.is_shutdown():
		
		print("in pubToROS")
		ang_pos = [count*(2*math.pi/1000.0),count*(2*math.pi/1000.0)] # converted to radians

        #----------------------------------------------
		pubjs = rospy.Publisher('/diffbot/measured_joint_states', JointState, queue_size=1)
		joint_state = JointState()
		
		joint_state.name = ["left_wheel_joint","right_wheel_joint"]
		joint_state.header.stamp = rospy.Time.now()
		joint_state.position = ang_pos #msg.data
		joint_state.velocity = [(ang_pos[0]-prev_ang_pos[0])*r,(ang_pos[1]-prev_ang_pos[1])*r]
		joint_state.effort = []
		pubjs.publish(joint_state)

		#----------------------------------------------
		pubticks = rospy.Publisher('/diffbot/encoder_tick', EncodersStamped, queue_size=1)
		enc_stamped = EncodersStamped()
		
		enc_stamped.header.stamp = rospy.Time.now()
		enc_stamped.encoders.ticks = [count,count]
		pubticks.publish(enc_stamped) # this is questionable check without publishing this

		prev_ang_pos = ang_pos 
		rate.sleep()


if __name__ == '__main__':
	
	try:
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