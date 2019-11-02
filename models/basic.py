import cv2
import os
import pandas as pd
import numpy as np
import imutils
import ffmpy

def ImpTimestamp(timestamps,fps):
    
    impTime = []
    for i in range(len(timestamps)-1):
      if (timestamps[i+1]-timestamps[i]- float(1/fps)) > 0.0001:
        impTime.append(timestamps[i])
        impTime.append(timestamps[i+1])

    return impTime

def FrameExtract(path,reso): 
      
    vidObj = cv2.VideoCapture(path) 
    fps = vidObj.get(cv2.CAP_PROP_FPS)
    g_frame=[]
    og_frame=[]
    wi = reso
    hi = int(vidObj.get(cv2.CAP_PROP_FRAME_HEIGHT)/vidObj.get(cv2.CAP_PROP_FRAME_WIDTH)*reso)
    success = True
  
    while success: 
  
        success, image = vidObj.read()
        if (success == True):
          gray_img = cv2.resize(image, (wi,hi), interpolation = cv2.INTER_AREA)
          # Saves the frames with frame-count 
          g_frame.append(gray_img)

    return g_frame,fps,hi,wi

def impPt(frame,fps):
    frame_nos = []
    timestamps = []
    imp_frams = []
    fgbg = cv2.createBackgroundSubtractorKNN()
    kernel = np.ones((2, 2), np.uint8)
    kernel2 = np.ones((25, 25), np.uint8)
    for i in range(len(frame)):
        frameDelta = fgbg.apply(frame[i])
        thresh = cv2.threshold(frameDelta, 200, 255, cv2.THRESH_BINARY)[1]

        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        thresh = cv2.dilate(opening, None, iterations=4)
        closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        
        maxi = 0
        for c in cnts:
            if cv2.contourArea(c) > maxi:
                maxi = cv2.contourArea(c)
                cnt = c
            
            if maxi > 1000:
                text = float(i/fps) 
                (x, y, w, h) = cv2.boundingRect(cnt)

        if maxi > 1000:
            (x, y, w, h) = cv2.boundingRect(cnt)
            cv2.putText(frame[i], '%.2f' % text, (x, h), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), lineType=cv2.LINE_AA) 
            frame_nos.append(i)
            imp_frams.append(frame[i])
            timestamps.append(float(text))
            
    return frame_nos,imp_frams,timestamps

def sizeDiff(inf, outf):
    infs = os.path.getsize(inf)
    outfs = os.path.getsize(outf)
    return (infs >> 20), (outfs >> 20)

def genImpVid(video_name, images, height, width, color, fps):
    writer = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height), color)
    for i in images:
        writer.write(i)
        

def main(vid_file):
    global og_frames, g_frames, fps, height, width, hist_arr, impFrams

    g_frames,fps,height,width = FrameExtract(vid_file,1280)
    frame_nos,impFrams,timestamps = impPt(g_frames,fps)

    genImpVid("static/video/output/og.mp4",impFrams,height,width,True,fps)
    
    impTS = ImpTimestamp(timestamps,fps)
    
    os.system(
        "yes | ffmpeg -i static/video/output/og.mp4 -vcodec libx264 static/video/output/output.mp4")
    os.remove("static/video/output/og.mp4")
    
    infilesize, outfilesize = sizeDiff("static/video/output/output.mp4",vid_file)
