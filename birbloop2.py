from picamerax.array import PiRGBArray
from picamerax import PiCamera
from time import time, sleep
import common
import lensshading
import cv2
import numpy as np
import imutils
import argparse
import sys
import logging
import sched
from datetime import datetime
from setproctitle import setproctitle

from birbconfig import BirbConfig
from focusassist import FocusAssist
from imagemask import ImageMask
from birbwatcher import BirbWatcher

LIVE_CAMERA_STEP = 10
FULL_PICTURE_STEP = 10

previewResolution = (640, 480)
#FULL_RES = (3280, 2464)
FULL_RES = (4056, 3040)
windowName = 'birbcam'
saveLocation = '/home/pi/Public/birbs/'
debugMode = False
noCaptureMode = False
average = None
scheduler = sched.scheduler(time, sleep)
takeFullPicture = False
takeLivePicture = False
nextLivePictureTime = 0
nextFullPictureTime = 0

setproctitle("birbcam")
config = BirbConfig()

if not config.logFile is None:
    logging.basicConfig(level=logging.INFO, filename=config.logFile, format='%(levelname)s: %(message)s')
else:
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

logging.info(f"Saving output to: {config.saveTo}")
if config.noCaptureMode: logging.info("Using No Capture Mode")
if config.debugMode: logging.info("Using Debug Mode")

camera = PiCamera()
camera.resolution = previewResolution
camera.framerate = 30;
camera.iso = 200
rawCapture = PiRGBArray(camera, size=previewResolution) 

"""
shading = lensshading.get_lens_shading(args.get("lensshading"))
if shading != None:
    shading = shading.astype("uint8")
    print(np.shape(shading))
    camera.lens_shading_table = shading
"""

camera.exposure_mode = 'auto'
camera.awb_mode = 'auto'
camera.meter_mode = 'spot'

sleep(2)

camera.shutter_speed = camera.exposure_speed
#camera.exposure_mode = 'off'
#g = camera.awb_gains
#camera.awb_mode = 'auto'
#camera.awb_gains = g

if debugMode:
    logging.info("Using camera settings...")
    logging.info("  ISO: %d", camera.iso)
    logging.info("  Metering: " + camera.meter_mode)
    logging.info("  Exposure Mode: " + camera.exposure_mode)
    logging.info("  White Balance: " + camera.awb_mode)
    logging.info("  Shutter: %d", camera.shutter_speed)

# **************************************
#   Focus assist
# **************************************
focusAssist = FocusAssist()
if focusAssist.run(camera) == False: sys.exit()

# **************************************
#   Set mask
# **************************************
imageMask = ImageMask()
if imageMask.run(camera) == False: sys.exit()
mask = imageMask.mask

# **************************************
#   Capture loop
# **************************************
watcher = BirbWatcher(config)
watcher.run(camera, mask)