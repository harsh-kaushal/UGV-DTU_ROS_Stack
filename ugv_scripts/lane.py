#!/usr/bin/env python

# Python libs

# numpy and scipy
import numpy as np
import math

import matplotlib.pyplot as plt

# OpenCV
import cv2

# Ros libraries
import rospy

# Ros Messages
from sensor_msgs.msg import CompressedImage
from sensor_msgs.msg import LaserScan

# Ros Service
from ugv_scripts.srv import SendImage, SendImageResponse, SendImageRequest


'''TO understand
Minimize all the function except the main,
then start reading from there 
then start opening function as you encounter one.

imagesShow() is complimentary if you want to see all the images'''
#=========================================================================================
#=========================================================================================
# Calculates Polar Cordinates for 3 given cartesian coordinates
def calculatePolarCord(x3, y3): 
  '''
  the x coordinates increases from left to right
  while the y coordinates increses from top to bottom which 
  leaves us with no standard coordinate system so 
  to do polar angle and radius calculation we make the image appear
  in 4th quadrant where x increase left to right and y increase top to bottom but in the negative range
  so the index of y coordinate is negated everywhere   
  '''
  #   C(i , -j) 0   0 B (IMAGE_W/2 , 0)---BOT's HEADING
  #              \  |
  #               \ |
  #                \|
  #                 0 A (IMAGE_W/2 , -IMAGE_H)---BOT's POSITION

  #bot position in image (IMAGE_W/2 , IMAGE_H)
  x1 ,y1 = IMAGE_W/2 , -IMAGE_H
  #Reference Point for angle
  x2 ,y2 = IMAGE_W/2 , 0
  # White lanes cordinate in image
  x3 ,y3 = x3 , -y3

  # Find direction ratio of line AB 
  ABx = x2 - x1 
  ABy = y2 - y1 

  # Find direction ratio of line AC 
  ACx = x3 - x1 
  ACy = y3 - y1 

  # Find the dotProduct of lines AB & AC 
  dotProduct = (ABx * ACx + ABy * ACy)

  # square of magnitude of line AB and AC 
  magABsq = (ABx * ABx + ABy * ABy )        
  magACsq = (ACx * ACx + ACy * ACy )

  # cosine of the angle formed by line AB and AC 
  angle = dotProduct
  angle /= math.sqrt(magABsq * magACsq)

  angle = math.acos(angle)

  if x3 < IMAGE_W/2:
    angle = angle 
  if x3 >= IMAGE_W/2:
    angle = -1*angle

  return [math.sqrt(magACsq), angle]

#Searches white pixels in an input image
def whitePixelSearch(img):
  #global IMAGE_H
  #global IMAGE_W
  
  # print(img.shape[0])
  # print(img.shape[1])
  # print(img.shape[2])

  # plt.imshow(img, interpolation='nearest')
  # plt.show()
 
  indices=[]
  for i in range(0,IMAGE_H):
    j = 0
    while j < IMAGE_W:

      if np.sum(img[i,j]) >= 1.5*255.0:         # If the edge of lane is hit.
        
        index = calculatePolarCord(j,i)
        index[0] = np.sum(depth_img[i,j])/3 # actual polar distance
        index[1] = (index[1]*fov_d)/(2*90.0) # actual theta
        indices.append(index)

        #j += 50                  # To skip useless search in blank space between lanes  

        #print("#################")
      j+= 1
  #print(type(indices))
  #print(len(indices))        

  return indices

#Creates and publishes Final Image message to rviz
def Img_msg_Publisher():

  global count      #just fancy stuff (for loop counter)
  count += 1

  #------------------Publish Final Image to rviz-----------------------

  pub1 = rospy.Publisher("/ugvbot/Threshold_image/compressed",CompressedImage, queue_size = 1)

  msg1 = CompressedImage()
  msg1.header.stamp = rospy.Time.now()
  msg1.format = "jpeg"
  msg1.data = np.array(cv2.imencode('.jpg', thresh_img)[1]).tostring()

  pub2 = rospy.Publisher("/ugvbot/Depth_image/compressed",CompressedImage, queue_size = 1)

  msg2 = CompressedImage()
  msg2.header.stamp = rospy.Time.now()
  msg2.format = "jpeg"
  msg2.data = np.array(cv2.imencode('.jpg', depth_img)[1]).tostring()
  # Publish Final Images
  pub1.publish(msg1)
  pub2.publish(msg2)

  print("#######################-"+ str(count) +"-############################")
  if VERBOSE :
    rospy.loginfo("From Image Msg Publisher")
    print("Msg Format = ",msg1.format)
    print("Shape of Image = ",thresh_img.shape)
    print("-------------------------------------------------")
  else :
    print("Publishing Final Image.....Bitches!")

#Processes Image and Calls Img_msg_Publisher at end.
def Img_Processor(ros_data):

  global thresh_img
  global depth_img
  
  global IMAGE_H
  global IMAGE_W


  if VERBOSE :
    print("-------------------------------------------------")
    rospy.loginfo("From Image Processor")
    print("Type of Received Image = "+ str(ros_data.format))
    print("length of Recieved Image = ",len(ros_data.depth_data))
  

  #### direct conversion to CV2 ####
  np_arr = np.fromstring(ros_data.depth_data, np.uint8)
  depth_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) # OpenCV >= 3.0:

  np_arr = np.fromstring(ros_data.thresh_data, np.uint8)
  thresh_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) # OpenCV >= 3.0:

  #Image Dimensions
  IMAGE_H = thresh_img.shape[0]  # assuming 256
  IMAGE_W = thresh_img.shape[1]  # assuming 512 

  Img_msg_Publisher()

  laser_processor()

#Creates and publishes Laser message for lanes to rviz 
def laser_msg_publisher(ranges_list):
  
  #------------------Publish Fake Laser to rviz-----------------------
  laser_pub = rospy.Publisher('ugvbot/fake_scan', LaserScan, queue_size=1)

  angle_min = -(fov_d*math.pi/180.0)/2
  angle_max = (fov_d*math.pi/180.0)/2
  intensities=[]

  start_time = rospy.Time.now()
  angle_increment = np.pi/(180*scan_res_inv)
  time_increment= 1/100

  msg=LaserScan()
  msg.header.stamp = start_time
  msg.header.frame_id = "laser"
  msg.angle_min=angle_min
  msg.angle_max=angle_max
  msg.angle_increment = angle_increment   # Angle Increment
  msg.time_increment = time_increment     # Time Increment
  msg.range_min=0                       # If range < MinRange range = 0 
  msg.range_max=100                     # If range > MaxRange range = inf 
  msg.ranges=ranges_list                # Range of Lanes pixel
  msg.intensities=intensities           # Intensities empty

  # Publish fake LaserScan 
  laser_pub.publish(msg)

  if VERBOSE :
    rospy.loginfo("From Laser message Publisher")
    print("Angle Increment", msg.angle_increment)
    print("length of Range list = ",len(msg.ranges))
  else :
    print("           Fake Laser......Bitches!")

#Processes Final Image and finds polar cordinates wrt to bot
#Also calls laser_msg_publisher at end
def laser_processor():

  if type(thresh_img) is np.ndarray:

    # Indices of white pixels from image
    polar = whitePixelSearch(thresh_img)
    print(len(polar))


    # radius = np.array(polar)[:,0]
    # theta = np.array(polar)[:,1]
    # plt.polar(theta,radius,'g.')         # Syntax plt.polar(theta,r)
    # plt.show()
    
    ranges=[1000.0]*int(fov_d*scan_res_inv)       # Cross Verify length from laser msg Defination in laser_msg_publisher
    print(len(ranges))
    for i in range(len(polar)):
      degree = polar[i][1]*180/np.pi
      index = (degree+fov_d/2)*scan_res_inv
      ranges[int(index)] = polar[i][0]

    laser_msg_publisher(ranges)



  else :
    print("##################################")
    print("Shit Happened in laser_processor!!")
    print("Type of final Image = ",type(thresh_img))
    exit(1)

#Custom Service client
def image_client():
  rospy.wait_for_service('get_camera_image_service')
  try:
    srv_obj = rospy.ServiceProxy('get_camera_image_service', SendImage, persistent=True)
    responce = srv_obj(1)
    return responce
      
  except rospy.ServiceException as e:
    print("Service call failed: %s"%e)
    print(" ")
    print("Ohh My GOD !!!!!!!!!!!!!!")

if __name__ == '__main__':
  #-----------------Global Variables Used-------------------
  #For Image processing
        # masked_img     Masked with ROI
        # warped_img     prespective transformed 
        # thresh         thresholded to 0.0 or 255.0
        # reconst_img    Reconstructed From Inverse Prespective
        # final_img      Image with Hough lines on thresh 
        # IMAGE_H        Image Height 720
        # IMAGE_W        Image Width 1280

  count = 0
  scan_res_inv = 100
  fov_d = 118

  VERBOSE = False

  rospy.init_node('Lanes_Processing_N_Publishing_service', anonymous=False)

  while True:
    try:
      responce_data = image_client()
      Img_Processor(responce_data)

    except KeyboardInterrupt:
      plt.close('all')
      print("Shutting down ROS Lanes_Processor_N_Publisher module")
      break

  print("Fat boi .... You made a intrrupt")