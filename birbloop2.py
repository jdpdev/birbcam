from picamera.array import PiRGBArray
from picamera import PiCamera
from common import draw_mask
import time
import cv2
import numpy as np
import imutils
import argparse
import sys
import logging
from datetime import datetime

previewResolution = (640, 480)
FULL_RES = (2592, 1952)
mask = (0.5, 0.5)
windowName = 'birbcam'
debugMode = False
average = None
lastCaptureTicks = 0

def setup_logging():
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", default=None, help="path to the log file")
    ap.add_argument("-d", "--debug", help="debug mode", action='store_true')
    args = vars(ap.parse_args())

    if not args.get('file') is None:
        logging.basicConfig(level=logging.INFO, filename=args.get('file'), format='%(levelname)s: %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    global debugMode
    debugMode = args.get('debug')
    
    if debugMode:
        logging.info("Using Debug Mode")

def process_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    return gray

def take_full_picture(camera):
    date = datetime.now()
    filename = date.strftime("%Y-%m-%d-%H:%M:%S") + ".jpg"
    path = "/home/pi/Public/birbs/" + filename
    
    camera.resolution = FULL_RES
    camera.capture(path)
    camera.resolution = previewResolution

    global debugMode
    if not debugMode:
        return

    logging.info("Capturing Image...")
    logging.info("  save to: " + path)
    logging.info("  shutter: %d", camera.shutter_speed)
    logging.info("  shutter (auto): %d", camera.exposure_speed)
    logging.info("  iso: %d", camera.iso)

setup_logging()

camera = PiCamera()
camera.resolution = previewResolution
camera.framerate = 30;
camera.iso = 200
rawCapture = PiRGBArray(camera, size=previewResolution)

camera.exposure_mode = 'auto'
camera.awb_mode = 'auto'
camera.meter_mode = 'spot'

time.sleep(2)

camera.shutter_speed = camera.exposure_speed
camera.exposure_mode = 'off'
g = camera.awb_gains
camera.awb_mode = 'off'
camera.awb_gains = g

if debugMode:
    logging.info("Using camera settings...")
    logging.info("  ISO: %d", camera.iso)
    logging.info("  Metering: " + camera.meter_mode)
    logging.info("  Exposure Mode: " + camera.exposure_mode)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    now = rawCapture.array
    gray = process_image(now)
    now = imutils.resize(now, 640, 480)
    rawCapture.truncate(0)

    # initialize average
    if (average is None):
        average = gray.copy().astype('float')
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

    shouldTrigger = False
    for c in cnts:
        if cv2.contourArea(c) < 300:
            continue
        
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(now, (x, y), (x + w, y + h), (0, 255, 0), 2)
        shouldTrigger = True

    # capture full
    if shouldTrigger and lastCaptureTicks > 60:
        take_full_picture(camera)
        lastCaptureTicks = 0
    else:
        lastCaptureTicks += 1

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

    