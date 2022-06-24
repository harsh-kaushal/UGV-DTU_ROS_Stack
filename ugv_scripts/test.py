#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

thresh_img = plt.imread('/home/jacksparrow/ugv2_ws/src/ugv_II/thresh_final.jpg')
depth_img = plt.imread('/home/jacksparrow/ugv2_ws/src/ugv_II/depth_final.jpg')

thresh_img = np.uint8(thresh_img)

a2 = Image.fromarray(thresh_img)
print(thresh_img.shape)
arr = thresh_img.tostring()
print(len(arr))
print(np.fromstring(arr,dtype=np.uint8).reshape(256, 512).shape)