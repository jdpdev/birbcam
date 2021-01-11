from time import time, sleep
from picamera.array import PiRGBArray
from picamera import PiCamera
from cv2 import imwrite, imshow, waitKey
import sched

WATCHER_STEP = 5

def run():
    camera = PiCamera()
    rawCapture = PiRGBArray(camera)
    keyframe = startup(camera, rawCapture)

    s = sched.scheduler(time, sleep)
    s.enter(WATCHER_STEP, 1, bird_watcher, (s,))
    s.run()

    #imshow("Image", image)
    #waitKey(0)

def startup(camera, rawCapture):
    sleep(1)
    return capture_photo(camera, rawCapture, "startup")

def bird_watcher(sc):
    print("looking for birbs")
    sc.enter(WATCHER_STEP, 1, bird_watcher, (sc,))

def capture_photo(camera, rawCapture, save_to=None):
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array

    # for debug
    if not save_to is None:
        imwrite(save_to + "-cv.jpg", image)
        camera.capture(save_to + "-picamera.jpg")

    return image

run()