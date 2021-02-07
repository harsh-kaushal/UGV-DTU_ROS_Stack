# Image Lanes to Laser Scan !!

>Uses a simple approach to extact lanes distance data,
>from image and convert it to a laser scan
>which will be published to rviz and can also be used for 
>mapping and localization packages such as costmap_2d or gmapping


## Running the scripts

Start by running the camera image subscriber service by command
```sh
rosrun ugv_bot camera_img_service
``` 

next open a new terminal tab by pressing ctrl+shift+tab

now run the image to laser scan script by command
```sh
rosrun ugv_bot lanes_pub_using_srv
```

# Explanation
script starts from main

initiates a node named "Lanes_Processing_N_Publishing_service"

gets into image_client function the latest image from "get_camera_image_service" server and returns the responce_data.

Now this responce data is of standard compressedImage message type

the responce_data is passed to Image_Processor function

## Image_Processor

this function seperates the image data form message and does the following tasks.

1. Defines a mask and get the Region of interest using bitwise_and Operation.
<img src="Images/maskedImage.png" width="640" height="360" align="left"/>
  \ 
2. Next transforms(warp) the image such that the straight lanes becomes straight lines as you can see below.
<img src="Images/wrapedImage.png" width="640" height="360" align="left"/>
\
3. Now this image undergoes a binary thresholding for seperating the white pixels
<img src="Images/thresholdedImage.png" width="640" height="360" align="left"/>
\
4. To finally get only lanes in the image the hough transform is used.
<img src="Images/HoughLinesImage.png" width="640" height="360"/>


