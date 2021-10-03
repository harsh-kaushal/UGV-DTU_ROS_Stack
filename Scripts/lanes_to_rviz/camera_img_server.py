#!/usr/bin/env python
from __future__ import print_function

import os

import cv2
import numpy as np

from sensor_msgs.msg import CompressedImage

import ugv_bot.srv
from ugv_bot.srv import SendImage, SendImageResponse
import rospy

def handle_image(request):

    global img
    global count

    if request:
        count +=1
        print("#######################-"+ str(count) +"-############################")

        if VERBOSE:
            print("Request Variable",request)
            print("Request Variable type",type(request))
            print("-----------------------------------------")

        srv_msg = SendImageResponse()
        srv_msg.header.stamp = rospy.Time.now()
        srv_msg.format = "jpeg"
        srv_msg.data = np.array(cv2.imencode('.jpg',img)[1]).tostring()

        print("Hey Homie........")
        print("Done Sending !!!!")

        return srv_msg

def Img_redirector(ros_data):

    global img

    np_arr = np.fromstring(ros_data.data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) # OpenCV >= 3.0:

if __name__ == "__main__":
    VERBOSE = False

    img = None

    count = 0

    rospy.init_node('camera_image_server')
    rospy.Subscriber("/ugvbot/image_raw/compressed",CompressedImage, Img_redirector,  queue_size = 1)
    s = rospy.Service('get_camera_image_service', SendImage, handle_image)

    print("Ready to send Image.")
    
    rospy.spin()