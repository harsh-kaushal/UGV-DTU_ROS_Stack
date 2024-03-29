#!/usr/bin/env python

from __future__ import print_function

import sys

import cv2
import numpy as np

from ugv_scripts.srv import SendImage, SendImageResponse, SendImageRequest
import rospy

def image_client():
    rospy.wait_for_service('get_camera_image_service')
    try:
        print("Input was :",a)
        srv_obj = rospy.ServiceProxy('get_camera_image_service', SendImage,persistent=True)
        responce = srv_obj(a)
        return responce
        
    except rospy.ServiceException as e:
        print("Service call failed: %s"%e)


if __name__ == "__main__":
    
    VERBOSE = False

    a = input("Enter Bool :")

    if a==True:
        if VERBOSE:
            print("Entered Bool : ",a)
            print("---------------------------")
            print("Recieved Something ",image_client())

        ros_data = image_client()

        np_arr = np.fromstring(ros_data.depth_data, np.uint8)
        depth_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) # OpenCV >= 3.0:

        np_arr = np.fromstring(ros_data.thresh_data, np.uint8)
        thresh_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) # OpenCV >= 3.0:

        cv2.imshow('Image',depth_np)
        cv2.waitKey()
        cv2.destroyAllWindows()

    else:
        print("Shit Happened in client")
        sys.exit(1)