#!/usr/bin/env python
# license removed for brevity

import rospy

from my_mouse.msg import basic_message as basic_msg_type

def talker():
    pub = rospy.Publisher('testing_temp', basic_msg_type, queue_size=10)
    rospy.init_node('test_publisher', anonymous=False)
    rate = rospy.Rate(10) # 10hz

    msg_info = basic_msg_type()
    #HEADER INFORMATION
    msg_info.header.stamp = rospy.Time.now()
    msg_info.header.frame_id = 'some_frame_id'

    #DATA INFROMATION
    # temp_info.xypose ={x : 0.35,y : 0.34, z : 0.00} 
    # temp_info.yaw = 0.0
    # temp_info.covariance = [[1,0,0],[0,1,0],[0,0,1]]

    msg_info.marker_name = "successful"
 

    while not rospy.is_shutdown():
        pub.publish(msg_info)
        rate.sleep()
        print("Publishing !!!!")


if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass