#!/usr/bin/env python
# this bitch is working without joint state pubisher in hw.launch
import rospy  
from sensor_msgs.msg import JointState
from std_msgs.msg import Float32

def loop():

    global lw_ang
    global rw_ang
    
    pub = rospy.Publisher('/diffbot/measured_joint_states', JointState, queue_size=1)
   
    joint_state = JointState()
    data = [0.0,0.0]
    joint_state.name = ["left_wheel_joint","right_wheel_joint"]
    joint_state.header.stamp = rospy.Time.now()
    joint_state.position = data #msg.data
    joint_state.velocity = []
    joint_state.effort = []
    pub.publish(joint_state)

if __name__ == '__main__':
    try:
        rospy.init_node('js_redirector', anonymous=False)
        rate = rospy.Rate(10) # 10hz
        while not rospy.is_shutdown():
            loop()
            rate.sleep()
    except rospy.ROSInterruptException:
        pass