from picamera.array import PiRGBArray
from picamera import PiCamera
from common import draw_mask
import time
import cv2
import numpy as np
import imutils

previewResolution = (640, 480)
mask = (0.5, 0.5)
windowName = 'birbcam'

def process_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    return gray

#cv2.namedWindow(windowName)

camera = PiCamera()
camera.resolution = previewResolution
camera.framerate = 32;
rawCapture = PiRGBArray(camera, size=previewResolution)

time.sleep(0.1)

average = None

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    now = rawCapture.array
    gray = process_image(now)
    now = imutils.resize(now, 640, 480)

    # initialize average
    if (average is None):
        average = gray.copy().astype('float')
        rawCapture.truncate(0)
        continue
    
    # calculate delta
    cv2.accumulateWeighted(gray, average, 0.05)
    convertAvg = cv2.convertScaleAbs(average)
    frameDelta = cv2.absdiff(gray, convertAvg)
    thresh = cv2.threshold(frameDelta, 70, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    # detect
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    for c in cnts:
        if cv2.contourArea(c) < 300:
            continue
        
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(now, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #text = "Occupied"

    # visualize
    convertAvg = cv2.cvtColor(convertAvg, cv2.COLOR_GRAY2BGR)
    frameDelta = cv2.cvtColor(frameDelta, cv2.COLOR_GRAY2BGR)
    thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    rtop = cv2.hconcat([now, convertAvg])
    rbottom = cv2.hconcat([frameDelta, thresh])
    quad = cv2.vconcat([rtop, rbottom])
    quad = cv2.resize(quad, (800, 600))
    cv2.imshow('processors', quad)
    #cv2.imshow('stream', now)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    rawCapture.truncate(0)