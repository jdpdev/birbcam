from time import time, sleep
from picamera.array import PiRGBArray
from picamera import PiCamera
#from cv2 import imwrite, imshow, waitKey
import cv2
import sched
import imutils
from datetime import datetime

WATCHER_STEP = 5

class BirbWatcher:
    camera = None
    rawCapture = None
    keyframe = None

    def __init__(self):
        print("chirp chirp")

        self.camera = PiCamera()
        self.camera.resolution = (2592, 1944)

        self.rawCapture = PiRGBArray(self.camera)

    def startup(self):
        sleep(1)
        return self.capture_photo("startup")

    def run(self):
        print("Using camera settings...")
        print("  Resolution: ", self.camera.resolution.width,  self.camera.resolution.height)
        print("  ISO: ", self.camera.iso)
        print("  Metering: " + self.camera.meter_mode)
        print("  Exposure Mode: " + self.camera.exposure_mode)

        self.keyframe = self.simplify_image(self.startup())

        s = sched.scheduler(time, sleep)
        s.enter(WATCHER_STEP, 1, self.watch_loop, (s,))
        s.run()

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
        cv2.imwrite("debug/delta.jpg", delta)
        thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]

        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 500:
                continue
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            #(x, y, w, h) = cv2.boundingRect(c)
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #text = "Occupied"
            return True

        return False

    def watch_loop(self, sc):
        print("looking for birbs")

        image = self.capture_photo()
        simple = self.simplify_image(image)

        if self.compare_with_keyframe(simple):
            print("found one!")
            self.save_bird_pic(image)

        sc.enter(WATCHER_STEP, 1, self.watch_loop, (sc,))

    def save_bird_pic(self, image):
        date = datetime.now()
        filename = date.strftime("%Y-%m-%d-%H:%M:%S") + ".jpg"
        path = "/home/pi/Public/birbs/" + filename
        #cv2.imwrite(path, image)
        
        print("Capturing Image...")
        print("  save to: " + path)
        print("  shutter: ", self.camera.shutter_speed)
        print("  shutter (auto): ", self.camera.exposure_speed)
        print("  iso: ", self.camera.iso)
        
        self.camera.capture(path)
        
        

watcher = BirbWatcher()
watcher.run()