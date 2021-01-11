from time import time, sleep
from picamera.array import PiRGBArray
from picamera import PiCamera
#from cv2 import imwrite, imshow, waitKey
import cv2
import sched
import imutils

WATCHER_STEP = 5

class BirbWatcher:
    camera = None
    rawCapture = None
    keyframe = None

    def __init__(self):
        print("chirp chirp")

        self.camera = PiCamera()
        self.rawCapture = PiRGBArray(self.camera)

    def startup(self):
        sleep(1)
        return self.capture_photo("startup")

    def run(self):
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
            cv2.imwrite(save_to + "-cv.jpg", image)
            self.camera.capture(save_to + "-picamera.jpg")

        return image

    def simplify_image(self, image):
        resize = imutils.resize(image, width=500)
        gray = cv2.cvtColor(resize, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        return gray

    def compare_with_keyframe(self, image):
        delta = cv2.absdiff(self.keyframe, image)
        cv2.imwrite("delta.jpg", delta)
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
            cv2.imwrite("bird-match-cv.jpg", image)

        sc.enter(WATCHER_STEP, 1, self.watch_loop, (sc,))

watcher = BirbWatcher()
watcher.run()