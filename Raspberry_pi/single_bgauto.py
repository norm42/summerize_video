#
# Copyright https://github.com/norm42/summerize_video/blob/master/LICENSE.md
# (Mit license)
#
import os
import sys
import cv2
import dbxlib
import time
from stat import *
from datetime import datetime

def measure_temp():
    # function to return the cpu temp
    temp = os.popen("vcgencmd measure_temp").readline()
    temp = temp.replace("temp=","")
    temp = temp.replace("'C", "")
    return(float(temp))
        
def got_file(file_name):
    # check to see if a file exists
    try:
        mode = os.stat(file_name).st_mode
        if S_ISREG(mode):   # regular file?
            return(True)
        else:
            return(False)
    except FileNotFoundError:
        #print("Oops ", file_name)
        return(False)

def proc_video(vfile_name, outname):
    # Create a summarization file from the video file name, store jpg summarization on outname
    min_frame = 45      # have to have at least this frames to process (3 seconds at 15 fps)
    threshold = 20		# level to create mask file
    
    # Open video file, get camera object.  Get frame/sec and total frames
    camera = cv2.VideoCapture(vfile_name)
    fps = camera.get(cv2.CAP_PROP_FPS)  # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
    frame_count = int(camera.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Some error checking for minimum file and get video length in seconds
    # Should typically get at least 3 to 5 seconds of video
    if (fps > 0) and (frame_count > min_frame):
        duration = frame_count / fps
    else:
        print("Bad video file: ", vfile_name)
        return(False)
    
    #For most files, 20ish seconds, we will process 10 frames. Longer files,
    #we will process fewer frames to a max of 20.  This limits the processing
    #time for long videos    
    num_frames = 10
    if((duration > 20) and (duration <=40)):
        num_frames = 15
    elif ( duration > 40):
        num_frames = 20

    frams_per_sample = int(frame_count/num_frames)  # Only process num_frames in any video
    # do not run off end of video (rounding, video ending truncation).  Reduce by one sample
    nframes_to_proc = frame_count - frams_per_sample

    # Get initial reference frame.  Generate a grayscale and filtered version
    _, reference_frame = camera.read()
    reference_frame = cv2.cvtColor(reference_frame, cv2.COLOR_BGR2GRAY)  #reference/background frame,first sample frame in image
    sumarized_image = reference_frame  #initalize the summation image
    
    # loop for number of frames in video - one sample
    # every iframs_per_sample, process a frame and build summarized image
    for j in range(1, nframes_to_proc):
        _, currentFrame = camera.read()
        if (j % frams_per_sample) == 0:  # Sample this frame
            # Get initial reference frame.  Generate a grayscale and filtered version
            srcimage = cv2.cvtColor(currentFrame, cv2.COLOR_BGR2GRAY)
            # Difference the reference image with the new frame
            rawimage = cv2.absdiff(reference_frame, srcimage)
            # Filter out some of the camera noise.  Not sure how much this helps
            gimage = cv2.fastNlMeansDenoising(rawimage, None, 10.0, 7, 21)
            # Start to build the mask images.  These will be binary images that control
            # What parts from the build up reference image are punched out and replaced
            # with the complement area in the new frame
            ret, th1 = cv2.threshold(gimage, threshold, 255, cv2.THRESH_BINARY)  #mask

            th1_inv = cv2.bitwise_not(th1)  # complement mask
            # Punch out of the current in progress summarized image, 
            # the motion portion of the new frame (srcimage)
            backgnd = cv2.bitwise_and(src1=sumarized_image, src2=sumarized_image, mask=th1_inv)
            # Punch out the content area in the in progress summarized image in  the new frame
            fgnd = cv2.bitwise_and(src1=srcimage, src2=srcimage, mask=th1)
            # Add the two together to merge in the past summarized image with the new frame
            # A new partial summarized frame is generated
            sumarized_image = cv2.add(backgnd, fgnd)

    quality = 50
    # We now have the final summarized image, write out jpg file
    cv2.imwrite(outname, sumarized_image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    camera.release()  # close the video file
    return(True)

# this is so we can use this file as an import or a main process

if __name__ == '__main__':
    safe_temp = 50.0  # Temp to get down to (or lower) to process a video.  A eyeball estimate.
    # This program is "noisy" printing info on the process.
    # I usually pipe this to a log file
    print("Creating a Dropbox object...")
    dbx = dbxlib.dbx_open('variam')
    if dbx == None:
        sys.exit("Can not open dbx app variam")

    vid_dict = dbxlib.dbx_getdirlist(dbx, "/vid")  #get list of video files 
    # for all the new video files in the directory, make summarization file
    for entry in vid_dict:
        #print(vid_dict[entry]["name"], " ", vid_dict[entry]["server_mod"])  #debug
        #Generate dropbox file names
        vfile_name = vid_dict[entry]["name"]
        if(vfile_name.find("mp4") > 0):         # only process mp4 files
            dbx_srcname = "/vid/" + vfile_name  # dropbox name
            dstname = "vid/" + vfile_name		# name on pi file system
            # Generate the output file name, split off the extension to get the 
            # jpeg file name with the same root name as the video
            name_no_mp4 = vfile_name.replace(".mp4", "")
            name_no_mp4 = name_no_mp4.replace(".", "_")
            filename_noext = name_no_mp4
            img_outname = "img/" + filename_noext + ".jpg"
            #
            #download the video file if the outfile does not exist
            if got_file(img_outname) == False:
                dbxlib.dbx_download(dbx, dbx_srcname, dstname, True)  #download file from DBX
                while measure_temp() > safe_temp:  # make sure the pi is not too hot to start with
                    time.sleep(10)
                # process a video file and compute processing time
                print("Processing ...", dstname, " ", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                start_time = time.time()
                if proc_video(dstname, img_outname):        #Summarize video file
                    proc_time = time.time() - start_time       #how long?
                    print("Processing time: %5.1f" %(proc_time), " seconds")
                    dbx_dstname = "/img/" + filename_noext + ".jpg"     #Dropbox file name
                    dbxlib.dbx_upload(dbx, img_outname, dbx_dstname, True)  #upload image summary to DBX
                    dbxlib.dbx_deletefile(dbx, dbx_srcname)  # delete video file on dropbox
        
    print("Done!")  # Yup

