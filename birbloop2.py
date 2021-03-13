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

LIVE_CAMERA_STEP = 10
FULL_PICTURE_STEP = 10

previewResolution = (640, 480)
#FULL_RES = (3280, 2464)
FULL_RES = (4056, 3040)
mask = (0.5, 0.5)
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

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", default=None, help="path to the log file")
ap.add_argument("-d", "--debug", help="debug mode", action='store_true')
ap.add_argument("-n", "--no-capture", help="do not capture photos", action='store_true')
ap.add_argument("-s", "--save", help="picture save location", default='/home/pi/Public/birbs/')
ap.add_argument("-ls", "--lensshading", help="which lens shading compensation to use", nargs="?", const=None, default=None)
args = vars(ap.parse_args())

def setup_logging(args):
    if not args.get('file') is None:
        logging.basicConfig(level=logging.INFO, filename=args.get('file'), format='%(levelname)s: %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    global saveLocation
    saveLocation = args.get('save')
    logging.info("Saving to: " + saveLocation)

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
    return date.strftime("%Y-%m-%d-%H-%M-%S")

def save_location():
    global saveLocation
    return saveLocation

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

def take_full_picture(camera, thumbnail):
    global noCaptureMode
    if noCaptureMode:
        return False

    date = datetime.now()
    filestamp = current_filestamp()
    filename = filestamp + ".jpg"
    path = save_location() + "full/" + filename
    cv2.imwrite(save_location() + "thumb/" + filename, thumbnail)

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

def draw_histogram(now, key, resolution):
    halfHeight = int(resolution[1] / 2)
    blank = np.zeros((resolution[1],resolution[0],3), np.uint8)

    now_hist = cv2.calcHist([now], [0], None, [256], [0,255])
    cv2.normalize(now_hist, now_hist, 0, halfHeight, cv2.NORM_MINMAX)
    now_data = np.int32(np.around(now_hist))
    
    max = now_data.max()
    average = 0
    total = 0

    for x, y in enumerate(now_data):
        average += y * x
        total += y

    average = int(average / total)

    for x, y in enumerate(now_data):
        color = (0, 255, 0) if x == average else (255, 255, 255)
        height = resolution[1] - 255 if x == average else resolution[1] - y;
        cv2.line(blank, (x, resolution[1]),(x, height), color)

    #compare = cv2.compareHist(key_hist, now_hist, cv2.HISTCMP_CHISQR)
    cv2.putText(blank,"%d" % average,(average + 5, resolution[1] - 128),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 255, 0))

    return blank

def debug_frame(frame, key):
    (ahist, adata) = common.build_histogram(frame)
    (bhist, bdata) = common.build_histogram(key)
    compare = common.compare_histograms(ahist, bhist)

    logging.info("Histogram comparison: %d" % compare)

setup_logging(args)

camera = PiCamera()
camera.resolution = previewResolution
camera.framerate = 30;
camera.iso = 200
rawCapture = PiRGBArray(camera, size=previewResolution) 

shading = lensshading.get_lens_shading(args.get("lensshading"))
if shading != None:
    shading = shading.astype("uint8")
    print(np.shape(shading))
    camera.lens_shading_table = shading

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

# **************************************
#   Capture loop
# **************************************
shutterSpeeds = [333333, 25000, 16666, 11111, 8000, 5555, 4166, 4000, 2857, 1333, 1000]
shutterSpeedNames = ["30", "45", "60", "90", "125", "180", "250", "350", "500", "750", "1000"]
isoSpeeds = [100, 200, 400, 600, 800]
exposureComps = [-12, -6, 0, 6, 12]
whiteBalanceModes = ["auto", "sunlight", "cloudy", "shade"]
pauseRecording = True

currentShutterSpeed = 2
camera.shutter_speed = shutterSpeeds[currentShutterSpeed]
camera.iso = isoSpeeds[1]
camera.awb_mode = whiteBalanceModes[0]

def flip_through_array(values, current, delta):
    try:
        i = values.index(current)
        i += delta

        if i >= len(values):
            i = 0

        if i < 0:
            i = len(values) - 1
    except ValueError:
        i = 0

    return values[i]

def next_shutter_speed(camera, delta):
    global shutterSpeeds
    global currentShutterSpeed
    
    shutter = flip_through_array(shutterSpeeds, shutterSpeeds[currentShutterSpeed], delta)
    camera.shutter_speed = shutter

    currentShutterSpeed = shutterSpeeds.index(shutter)

def next_iso(camera, delta):
    global isoSpeeds
    camera.iso = flip_through_array(isoSpeeds, camera.iso, delta)

def next_exposure_comp(camera, delta):
    global exposureComps
    camera.exposure_compensation = flip_through_array(exposureComps, camera.exposure_compensation, delta)

def next_white_balance(camera, delta):
    global whiteBalanceModes
    camera.awb_mode = flip_through_array(whiteBalanceModes, camera.awb_mode, delta)

camera.resolution = previewResolution
rawCapture = PiRGBArray(camera, size=previewResolution)
camera.lens_shading_table = shading
mask_resolution = common.get_mask_real_size(mask, previewResolution)
mask_bounds = common.get_mask_coords(mask, previewResolution)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    now = rawCapture.array
    gray = process_image(now)
    now = imutils.resize(now, 640, 480)
    rawCapture.truncate(0)

    masked = common.extract_image_region(now, mask_bounds)
    gray = common.extract_image_region(gray, mask_bounds)

    # initialize average
    if (average is None):
        average = gray.copy().astype('float')
        continue
    
    # calculate delta
    cv2.accumulateWeighted(gray, average, 0.1)
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
        
        shouldTrigger = True

    # capture full
    didTakeFullPicture = False
    if shouldTrigger and is_full_picture_time() and not pauseRecording:
        didTakeFullPicture = take_full_picture(camera, masked)

        if didTakeFullPicture and debugMode:
            debug_frame(gray, convertAvg)

    if is_live_picture_time():
        take_live_picture(camera)

    # visualize
    if debugMode:
        for c in cnts:
            if cv2.contourArea(c) < 600:
                continue
            
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(masked, (x, y), (x + w, y + h), (0, 255, 0), 2)

        convertAvg = cv2.cvtColor(convertAvg, cv2.COLOR_GRAY2BGR)
        frameDelta = cv2.cvtColor(frameDelta, cv2.COLOR_GRAY2BGR)
        thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

        histogram = draw_histogram(cv2.cvtColor(now, cv2.COLOR_BGR2GRAY), convertAvg, mask_resolution)

        cv2.putText(histogram, "(S)hutter (A): " + str(shutterSpeedNames[currentShutterSpeed]), (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv2.putText(histogram, "(E)xposure (W): " + str(camera.exposure_compensation), (10, 50), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv2.putText(histogram, "(I)SO (U): " + str(camera.iso), (10, 80), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv2.putText(histogram, "W(B) (V): " + str(camera.awb_mode), (10, 110), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        
        if pauseRecording:
            cv2.putText(histogram, "PAUSED", (90, 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        rtop = cv2.hconcat([masked, histogram])
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

    if key == ord("b"):
        next_white_balance(camera, 1)

    if key == ord("v"):
        next_white_balance(camera, -1)

    if key == ord("p"):
        pauseRecording = not pauseRecording

    if key == ord("q"):
        break

    