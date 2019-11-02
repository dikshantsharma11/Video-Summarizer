import cv2
import os
import pandas as pd
import numpy as np
import imutils


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
      imp_frams = []
      fgbg = cv2.createBackgroundSubtractorKNN()
      kernel = np.ones((25, 25), np.uint8)
      for i in range(len(frame)):
        frameDelta = fgbg.apply(frame[i])
        thresh = cv2.threshold(frameDelta, 200, 255, cv2.THRESH_BINARY)[1]

        thresh = cv2.dilate(thresh, None, iterations=4)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        maxi = 0
        for c in cnts:
            if cv2.contourArea(c) > maxi:
                maxi = cv2.contourArea(c)
                cnt = c
            
            if maxi > 500:
                text = str(i/fps) 
                (x, y, w, h) = cv2.boundingRect(cnt)
                cv2.rectangle(frame[i], (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame[i], text, (x, h), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), lineType=cv2.LINE_AA) 

        if maxi > 500:
            frame_nos.append(i)
            imp_frams.append(frame[i])
      return frame_nos,imp_frams



def genImpVid(video_name, images, height, width, color, fps):
    writer = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(
        *'MP4V'), fps, (width, height), color)
    for i in images:
        writer.write(i)


def main(vid_file):
    global og_frames, g_frames, fps, height, width, hist_arr, impFrams

    g_frames,fps,height,width = FrameExtract(vid_file,500)
    frame_nos,impFrams = impPt(g_frames,fps)

    return genImpVid("static/video/output/og.mp4",impFrams,height,width,True,fps)
