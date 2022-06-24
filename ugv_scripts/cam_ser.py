#!/usr/bin/env python
from __future__ import print_function

import os
import matplotlib.pyplot as plt
import cv2
import numpy as np

from sensor_msgs.msg import CompressedImage

import rospy
from ugv_scripts.srv import SendImage, SendImageResponse

def handle_image(request):

    global thresh_img
    global depth_img
    global count

    if request:
        count +=1
        print("#######################-"+ str(count) +"-############################")
#        vid = cv2.VideoCapture(0)
#        ret, thresh_img = vid.read()
        thresh_img = plt.imread('/home/jacksparrow/ugv2_ws/src/ugv_II/THRESH_IMG.jpg')
        depth_img = plt.imread('/home/jacksparrow/ugv2_ws/src/ugv_II/DEPTH_IMG.jpg')
        
        if VERBOSE:
            print("Request Variable",request)
            print("Request Variable type",type(request))
            print("-----------------------------------------")

        srv_msg = SendImageResponse()
        srv_msg.header.stamp = rospy.Time.now()
        srv_msg.format = "jpeg"
        srv_msg.thresh_data = np.array(cv2.imencode('.jpg',thresh_img)[1]).tostring()
        srv_msg.depth_data = np.array(cv2.imencode('.jpg',depth_img)[1]).tostring()

        print("Hey Homie........")
        print("Done Sending !!!!")

        return srv_msg

if __name__ == "__main__":

    VERBOSE = False
    
    rospy.init_node('camera_image_server')
    
    s = rospy.Service('get_camera_image_service', SendImage, handle_image)
    print("Ready to send Image.")
    count = 0
    rospy.spin()