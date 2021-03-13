from picamerax.array import PiRGBArray
from picamerax import PiCamera
from time import time, sleep
import common
import cv2
import numpy as np
import imutils
import sched
from datetime import datetime
from setproctitle import setproctitle

import picturetaker

FULL_RES = (4056, 3040)
LIVE_RES = (800, 600)

LIVE_CAMERA_STEP = 10
FULL_PICTURE_STEP = 10

class BirbWatcher:
    def __init__(self, config):
        fullPictureTaker = picturetaker.PictureTaker(
            FULL_RES, 
            FULL_PICTURE_STEP, 
            config.saveTo, 
            picturetaker.filename_filestamp
        )
        livePictureTaker = picturetaker.PictureTaker(
            LIVE_RES,
            LIVE_CAMERA_STEP,
            config.saveTo,
            picturetaker.filename_live_picture
        )

    def run(self, camera, rawCapture):
        return True


    def process_image(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        return gray