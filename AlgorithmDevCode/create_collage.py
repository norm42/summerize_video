#
# Copyright https://github.com/norm42/summerize_video/blob/master/LICENSE.md
# (Mit license)
#
import cv2
import numpy as np

# image collage as a debug tool.
# Input is four images and a scale factor
def create_colg(image_list, scale_factor ):
    height, width = image_list[0].shape
    img1 = cv2.resize(image_list[0], (0, 0), None, scale_factor, scale_factor)
    img2 = cv2.resize(image_list[1], (0, 0), None, scale_factor, scale_factor)
    # mask images
    gray_image = np.ones((height,width,1),np.uint8)*128
    tmp_img = cv2.bitwise_and(src1=gray_image, src2=gray_image, mask=image_list[2])
    img3 = cv2.resize(tmp_img, (0, 0), None, scale_factor, scale_factor)

    tmp_img = cv2.bitwise_and(src1=gray_image, src2=gray_image, mask=image_list[3])
    img4 = cv2.resize(tmp_img, (0, 0), None, scale_factor, scale_factor)

    img5 = cv2.resize(image_list[4], (0, 0), None, scale_factor, scale_factor)
    img6 = cv2.resize(image_list[5], (0, 0), None, scale_factor, scale_factor)

    numpy_horz1 = np.hstack((img1, img2))
    numpy_horz2 = np.hstack((img3, img4))
    numpy_horz3 = np.hstack((img5, img6))
    numpy_final = np.vstack((numpy_horz1, numpy_horz2, numpy_horz3))
    return(numpy_final)
