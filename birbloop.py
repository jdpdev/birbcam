from time import time, sleep
from picamera.array import PiRGBArray
from picamera import PiCamera
#from cv2 import imwrite, imshow, waitKey
import cv2
import sched
import imutils
import argparse
import sys
import logging
from datetime import datetime

WATCHER_STEP = 5

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", default=None, help="path to the log file")
args = vars(ap.parse_args())

if not args.get('file') is None:
    logging.basicConfig(level=logging.INFO, filename=args.get('file'), format='%(levelname)s: %(message)s')
else:
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class BirbWatcher:
    camera = None
    rawCapture = None
    keyframe = None
    loopsSinceBirb = 0

    def __init__(self):
        logging.info("chirp chirp")

        self.camera = PiCamera()
        self.camera.resolution = (2592, 1944)

        self.rawCapture = PiRGBArray(self.camera)

    def startup(self):
        return self.capture_photo("startup")

    def run(self):
        self.take_keyframe()

        s = sched.scheduler(time, sleep)
        s.enter(WATCHER_STEP, 1, self.watch_loop, (s,))
        s.run()

    def take_keyframe(self):
        self.camera.iso = 200
        self.camera.exposure_mode = 'auto'
        self.camera.awb_mode = 'auto'

        sleep(2)

        self.camera.shutter_speed = self.camera.exposure_speed
        self.camera.exposure_mode = 'off'
        g = self.camera.awb_gains
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = g

        logging.info("Using camera settings...")
        logging.info("  Resolution: %d,%d", self.camera.resolution.width,  self.camera.resolution.height)
        logging.info("  ISO: %d", self.camera.iso)
        logging.info("  Metering: " + self.camera.meter_mode)
        logging.info("  Exposure Mode: " + self.camera.exposure_mode)

        self.keyframe = self.simplify_image(self.startup())
        cv2.imwrite("debug/keyframe.jpg", self.keyframe)

    def capture_photo(self, save_to=None):
        self.rawCapture = PiRGBArray(self.camera)
        self.camera.capture(self.rawCapture, format="bgr")
        image = self.rawCapture.array

        # for debug
        if not save_to is None:
            cv2.imwrite("debug/" + save_to + "-cv.jpg", image)
            self.camera.capture("debug/" + save_to + "-picamera.jpg")

        return image

    def simplify_image(self, image):
        resize = imutils.resize(image, width=500)
        gray = cv2.cvtColor(resize, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        return gray

    def compare_with_keyframe(self, image):
        delta = cv2.absdiff(self.keyframe, image)
        cv2.imwrite("debug/comparer.jpg", image)
        cv2.imwrite("debug/delta.jpg", delta)
        thresh = cv2.threshold(delta, 90, 255, cv2.THRESH_BINARY)[1]
        cv2.imwrite("debug/thresh.jpg", thresh)

        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 600:
                continue
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            #(x, y, w, h) = cv2.boundingRect(c)
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #text = "Occupied"
            self.save_bird_pic_debug(delta, "delta")
            self.save_bird_pic_debug(thresh, "thresh")
            return True

        return False

    def watch_loop(self, sc):
        logging.info("looking for birbs")

        image = self.capture_photo()
        simple = self.simplify_image(image)

        self.save_rolling_image()

        if self.compare_with_keyframe(simple):
            logging.info("found one!")
            self.save_bird_pic()
            self.loopsSinceBirb = 0
        else:
            self.loopsSinceBirb += 1

        if self.loopsSinceBirb > 6:
            logging.info("updating keyframe")
            self.take_keyframe()
            self.loopsSinceBirb = 0

        sc.enter(WATCHER_STEP, 1, self.watch_loop, (sc,))

    def save_bird_pic_debug(self, image, name):
        date = datetime.now()
        filename = date.strftime("%Y-%m-%d-%H:%M:%S") + ".jpg"
        path = "/home/pi/Public/birbs/" + name + "/" + filename
        cv2.imwrite(path, image)

    def save_rolling_image(self):
        path = "/home/pi/Public/birbs/live.jpg"
        self.camera.capture(path)

    def save_bird_pic(self):
        date = datetime.now()
        filename = date.strftime("%Y-%m-%d-%H:%M:%S") + ".jpg"
        path = "/home/pi/Public/birbs/" + filename
        
        logging.info("Capturing Image...")
        logging.info("  save to: " + path)
        logging.info("  shutter: %d", self.camera.shutter_speed)
        logging.info("  shutter (auto): %d", self.camera.exposure_speed)
        logging.info("  iso: %d", self.camera.iso)
        
        self.camera.capture(path)
        
        

watcher = BirbWatcher()
watcher.run()