#
# Copyright https://github.com/norm42/summerize_video/blob/master/LICENSE.md
# (Mit license)
#
import sys
import numpy as np
import cv2
import create_collage as ccoll

threshold = 20

# Open video file for processing
camera = cv2.VideoCapture('Front.20200506_154854.mp4')

fps = camera.get(cv2.CAP_PROP_FPS)  # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
frame_count = int(camera.get(cv2.CAP_PROP_FRAME_COUNT))
duration = frame_count / fps

num_frames = 10
if((duration > 20) and (duration <=40)):
    num_frames = 15
elif ( duration > 40):
    num_frames = 20
#nsamples = int(duration - 2)  # each second
#second_sample = int(duration/num_frames)  # number of seconds to sample, only num_frames
#frame_sample = fps * second_sample
iframs_per_sample = int(frame_count/num_frames)  # Only process num_frames in any video


nframes_to_proc = frame_count - iframs_per_sample  # do not run off end of video (error)

# Get initial reference frame.  Generate a grayscale and filtered version
_, backgroundFrame = camera.read()
backgroundFrame = cv2.cvtColor(backgroundFrame, cv2.COLOR_BGR2GRAY)
refdenoise = cv2.fastNlMeansDenoising(backgroundFrame, None, 10.0, 7, 21)
refimage = backgroundFrame

for j in range(1, nframes_to_proc):
    _, currentFrame = camera.read()
    if (j % iframs_per_sample) == 0:
        collage_list = []
        # Note if you use this program, the directory structures need to be made shown here
        # so intermediate files can be saved.  Also purge the directories between runs.
        ifname = "img/foregnd/foregnd" + str(j) +".png"
        filter_fname = "img/filter/filter_foregnd" + str(j) +".png"
        raw_fname = "img/raw/raw_foregnd" + str(j) + ".png"
        cur_fname = "img/current/cur_frame" + str(j) + ".png"
        ref_fname = "img/refimage/refimage" + str(j) + ".png"
        coll_fname = "img/collage/coll" + str(j) + ".png"
        #
        # convert color image to grayscale
        srcimage = cv2.cvtColor(currentFrame, cv2.COLOR_BGR2GRAY)
        # Filter out some of the camera noise.  Not sure how much this helps
        srcdenoise = cv2.fastNlMeansDenoising(srcimage, 10.0, 10.0, 7, 21)
        # Write the noise image for analysis
        cv2.imwrite(cur_fname, srcdenoise)
        collage_list.append(srcdenoise)  # filtered new frame
        # Difference the reference image with the new frame
        rawimage = cv2.absdiff(refdenoise, srcdenoise)
        # write for analysis
        cv2.imwrite(raw_fname, rawimage)
        # Filter out some of the noise in the differenced image
        fordenoise = cv2.fastNlMeansDenoising(rawimage, 10.0, 10.0, 7, 21)
        # Write out filtered difference for analysis
        cv2.imwrite(filter_fname, fordenoise)
        collage_list.append(fordenoise)
        # Start to build the mask images.  These will be binary images that control
        # What parts from the build up reference image are punched out and replaced
        # with the complement area in the new frame
        th1 = cv2.threshold(fordenoise, threshold, 255, cv2.THRESH_BINARY)[1]
        th1_inv = cv2.bitwise_not(th1)
        # Write out mask image
        cv2.imwrite(ifname, th1)
        collage_list.append(th1)
        collage_list.append(th1_inv)
        # Punch out of the current reference image the motion portion of the new frame
        backgnd = cv2.bitwise_and(src1=refimage, src2=refimage, mask=th1_inv)
        # Punch out the reference image - background from the new frame
        fgnd = cv2.bitwise_and(src1=srcdenoise, src2=srcdenoise, mask=th1)
        collage_list.append(backgnd)
        # Add the two together to merge in the past reference image with the new frame
        # A new reference frame is generated
        refimage = cv2.add(backgnd, fgnd)
        collage_list.append(refimage)
        coll_img = ccoll.create_colg(collage_list, 0.25)
        cv2.imwrite(coll_fname, coll_img)
        # Write for analysis
        cv2.imwrite(ref_fname, refimage)
# Write out the final image
cv2.imwrite("img/final_image.png", refimage)
cv2.imwrite("img/back_img.png", backgroundFrame)
