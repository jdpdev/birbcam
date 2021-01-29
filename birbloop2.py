from picamera.array import PiRGBArray
from picamera import PiCamera
#from common import draw_mask
from time import time, sleep
import common
import cv2
import numpy as np
import imutils
import argparse
import sys
import logging
import sched
from datetime import datetime
from setproctitle import setproctitle

LIVE_CAMERA_STEP = 10
FULL_PICTURE_STEP = 10

previewResolution = (640, 480)
#FULL_RES = (3280, 2464)
FULL_RES = (4056, 3040)
mask = (0.5, 0.5)
windowName = 'birbcam'
debugMode = False
noCaptureMode = False
average = None
scheduler = sched.scheduler(time, sleep)
takeFullPicture = False
takeLivePicture = False
nextLivePictureTime = 0
nextFullPictureTime = 0

setproctitle("birbcam -- birbloop2")

def setup_logging():
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", default=None, help="path to the log file")
    ap.add_argument("-d", "--debug", help="debug mode", action='store_true')
    ap.add_argument("-n", "--no-capture", help="do not capture photos", action='store_true')
    #parsed = ap.parse_args()
    args = vars(ap.parse_args())

    if not args.get('file') is None:
        logging.basicConfig(level=logging.INFO, filename=args.get('file'), format='%(levelname)s: %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    global debugMode
    global noCaptureMode
    debugMode = args.get('debug')
    noCaptureMode = args.get('no_capture')

    if noCaptureMode:
        logging.info("Using No Capture Mode")
    
    if debugMode:
        logging.info("Using Debug Mode")

def process_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    return gray

def current_filestamp():
    date = datetime.now()
    return date.strftime("%Y-%m-%d-%H:%M:%S")

def save_location():
    return "/home/pi/Public/birbs/"

def toggle_full_picture(sc):
    logging.info('Ready for full picture')
    global takeFullPicture
    global fullPictureScheduler
    takeFullPicture = True
    fullPictureScheduler = sc

def schedule_full_picture():
    global nextFullPictureTime
    nextFullPictureTime = time() + FULL_PICTURE_STEP

def is_full_picture_time():
    global nextFullPictureTime
    return time() >= nextFullPictureTime

def take_full_picture(camera):
    global noCaptureMode
    if noCaptureMode:
        return False

    date = datetime.now()
    filename = current_filestamp() + ".jpg"
    path = save_location() + filename

    global takeFullPicture
    takeFullPicture = False
    
    camera.resolution = FULL_RES
    camera.capture(path)
    camera.resolution = previewResolution
    rawCapture.truncate(0)

    schedule_full_picture()

    global debugMode
    if not debugMode:
        return True

    logging.info("Capturing Image...")
    logging.info("  save to: " + path)
    logging.info("  shutter: %d", camera.shutter_speed)
    logging.info("  shutter (auto): %d", camera.exposure_speed)
    logging.info("  iso: %d", camera.iso)

    return True

def schedule_live_picture():
    global nextLivePictureTime
    nextLivePictureTime = time() + LIVE_CAMERA_STEP

def is_live_picture_time():
    global nextLivePictureTime
    return time() >= nextLivePictureTime

def take_live_picture(camera):
    global noCaptureMode
    if noCaptureMode:
        return

    global takeLivePicture
    takeLivePicture = False

    camera.resolution = (800,600)
    camera.capture(save_location() + "live.jpg")
    camera.resolution = previewResolution
    rawCapture.truncate(0)

    schedule_live_picture()

def draw_histogram(key, now, resolution):
    halfHeight = int(resolution[1] / 2)
    blank = np.zeros((resolution[1],resolution[0],3), np.uint8)

    key_hist = cv2.calcHist([key], [0], None, [256], [0,256])
    #cv2.normalize(key_hist, key_hist, 0, halfHeight, cv2.NORM_MINMAX)
    #key_data = np.int32(np.around(key_hist))

    #for x, y in enumerate(key_data):
    #    cv2.line(blank, (x * 2,halfHeight),(x * 2,halfHeight-y),(255,255,255))

    now_hist = cv2.calcHist([now], [0], None, [256], [0,256])
    #cv2.normalize(now_hist, now_hist, 0, halfHeight, cv2.NORM_MINMAX)
    #now_data = np.int32(np.around(now_hist))

    #for x, y in enumerate(now_data):
    #    cv2.line(blank, (x * 2,resolution[1]),(x * 2,resolution[1]-y),(255,255,255))

    compare = cv2.compareHist(key_hist, now_hist, cv2.HISTCMP_CHISQR)
    cv2.putText(blank,"%d" % compare,(30, 30),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 255, 255),2)

    return blank

def debug_frame(frame, key):
    (ahist, adata) = common.build_histogram(frame)
    (bhist, bdata) = common.build_histogram(key)
    compare = common.compare_histograms(ahist, bhist)

    logging.info("Histogram comparison: %d" % compare)

setup_logging()

camera = PiCamera()
camera.resolution = previewResolution
camera.framerate = 30;
camera.iso = 200
rawCapture = PiRGBArray(camera, size=previewResolution)

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
focusWindowName = "Focus Assist"
focusWindowResolution = (1024, 768)
focusStart = (0, 0)
focusEnd = focusWindowResolution
isDragging = False

def focus_click_event(event, x, y, camera, resolution):
    global focusStart
    global focusEnd
    global isDragging
    
    if event == cv2.EVENT_LBUTTONDOWN:
        focusStart = (x, y)
        focusEnd = (x, y)
        isDragging = True
        return

    if event == cv2.EVENT_LBUTTONUP:
        isDragging = False
        set_zoom_rect(camera, focusStart, focusEnd, focusWindowResolution)
        return

    if event == cv2.EVENT_MOUSEMOVE:
        if isDragging:
            focusEnd = (x, y)
        return

def set_zoom_rect(camera, tl, br, resolution):
    x = tl[0] / focusWindowResolution[0]
    y = tl[1] / focusWindowResolution[1]
    w = (br[0] - tl[0]) / focusWindowResolution[0]
    h = (br[1] - tl[1]) / focusWindowResolution[1]
    camera.zoom = (x, y, w, h)


cv2.namedWindow(focusWindowName)
cv2.setMouseCallback(focusWindowName, lambda event, x, y, flags, param: focus_click_event(event, x, y, camera, focusWindowResolution))

camera.resolution = focusWindowResolution
rawCapture = PiRGBArray(camera, size=focusWindowResolution)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    image = frame.array
    rawCapture.truncate(0)

    laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()

    # drag rect
    if isDragging:
        cv2.rectangle(image, focusStart, focusEnd, (255, 0, 255), 2)

    # focus amount
    cv2.rectangle(image, (0,0), (120, 40), (255, 0, 255), -1)
    cv2.putText(image, str(int(laplacian_var)), (5,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    # crosshair
    common.draw_aim_grid(image, focusWindowResolution)
    
    cv2.imshow(focusWindowName, image)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("r"):
        set_zoom_rect(camera, (0,0), focusWindowResolution, focusWindowResolution)

    if key == ord("q"):
        break

    if key == ord("x"):
        sys.exit()

cv2.destroyAllWindows()

# **************************************
#   Set mask
# **************************************
maskWindowName = "Set Detection Mask"
maskWindowResolution = (800, 600)
mask = (0.5, 0.5)
camera.zoom = (0, 0, 1, 1)

def mask_click_event(event, x, y, flags, param):
    if event != cv2.EVENT_LBUTTONDOWN:
        return

    global mask
    global maskWindowResolution
    mask = common.change_mask_size(x, y, maskWindowResolution)

cv2.namedWindow(maskWindowName)
cv2.setMouseCallback(maskWindowName, mask_click_event)

camera.resolution = maskWindowResolution
rawCapture = PiRGBArray(camera, size=maskWindowResolution)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    
    image = frame.array
    common.draw_mask(image, mask, maskWindowResolution)
    common.draw_aim_grid(image, maskWindowResolution)
    rawCapture.truncate(0)

    cv2.imshow(maskWindowName, image)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    if key == ord("x"):
        sys.exit()

cv2.destroyAllWindows()

# **************************************
#   Capture loop
# **************************************
currentShutterSpeed = 0
shutterSpeeds = [333333, 16666, 11111, 8333, 5555, 4166, 3076, 2000, 1333, 1000]
shutterSpeedNames = ["30", "60", "90", "120", "180", "240", "325", "500", "750", "1000"]

isoSpeeds = [100, 200, 400, 600, 800]
exposureComps = [-12, -6, 0, 6, 12]

def next_shutter_speed(camera, delta):
    global currentShutterSpeed
    global shutterSpeeds

    currentShutterSpeed += delta

    if currentShutterSpeed >= len(shutterSpeeds):
        currentShutterSpeed = 0

    if currentShutterSpeed < 0:
        currentShutterSpeed = len(shutterSpeeds) - 1

    camera.shutter_speed = shutterSpeeds[currentShutterSpeed]

def next_iso(camera, delta):
    global isoSpeeds
    i = isoSpeeds.index(camera.iso)
    i += delta

    if i >= len(isoSpeeds):
        i = 0

    if i < 0:
        i = len(isoSpeeds) - 1

    camera.iso = isoSpeeds[i]

def next_exposure_comp(camera, delta):
    global exposureComps
    i = exposureComps.index(camera.exposure_compensation)
    i += delta

    if i >= len(exposureComps):
        i = 0

    if i < 0:
        i = len(exposureComps) - 1

    camera.exposure_compensation = exposureComps[i]

camera.resolution = previewResolution
rawCapture = PiRGBArray(camera, size=previewResolution)
mask_resolution = common.get_mask_real_size(mask, previewResolution)
mask_bounds = common.get_mask_coords(mask, previewResolution)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    now = rawCapture.array
    gray = process_image(now)
    now = imutils.resize(now, 640, 480)
    rawCapture.truncate(0)

    now = common.extract_image_region(now, mask_bounds)
    gray = common.extract_image_region(gray, mask_bounds)

    # initialize average
    if (average is None):
        average = gray.copy().astype('float')
        continue
    
    # calculate delta
    cv2.accumulateWeighted(gray, average, 0.05)
    convertAvg = cv2.convertScaleAbs(average)
    frameDelta = cv2.absdiff(gray, convertAvg)
    thresh = cv2.threshold(frameDelta, 90, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    # detect
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    shouldTrigger = False
    for c in cnts:
        if cv2.contourArea(c) < 600:
            continue
        
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(now, (x, y), (x + w, y + h), (0, 255, 0), 2)
        shouldTrigger = True

    # capture full
    didTakeFullPicture = False
    if shouldTrigger and is_full_picture_time():
        didTakeFullPicture = take_full_picture(camera)

        if didTakeFullPicture and debugMode:
            debug_frame(gray, convertAvg)

    if is_live_picture_time():
        take_live_picture(camera)

    # visualize
    if debugMode:
        convertAvg = cv2.cvtColor(convertAvg, cv2.COLOR_GRAY2BGR)
        frameDelta = cv2.cvtColor(frameDelta, cv2.COLOR_GRAY2BGR)
        thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

        histogram = draw_histogram(gray, convertAvg, mask_resolution)

        cv2.putText(histogram, "(S)hutter (A): " + str(shutterSpeedNames[currentShutterSpeed]), (10, 120), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv2.putText(histogram, "(E)xposure (W): " + str(camera.exposure_compensation), (10, 150), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv2.putText(histogram, "(I)SO (U): " + str(camera.iso), (10, 180), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

        rtop = cv2.hconcat([now, histogram])
        rbottom = cv2.hconcat([frameDelta, thresh])
        quad = cv2.vconcat([rtop, rbottom])
        #quad = cv2.resize(quad, (800, 600))
        cv2.imshow('processors', quad)

        if didTakeFullPicture:
            stamp = current_filestamp()
            cv2.imwrite(save_location() + "/debug/" + stamp + ".jpg", quad)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        next_shutter_speed(camera, 1)

    if key == ord("a"):
        next_shutter_speed(camera, -1)

    if key == ord("i"):
        next_iso(camera, 1)

    if key == ord("u"):
        next_iso(camera, -1)

    if key == ord("e"):
        next_exposure_comp(camera, 1)

    if key == ord("w"):
        next_exposure_comp(camera, -1)

    if key == ord("q"):
        break

    