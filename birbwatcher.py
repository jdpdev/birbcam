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
from optionflipper import OptionFlipper

FULL_RES = (4056, 3040)
LIVE_RES = (800, 600)
PREVIEW_RES = (800, 600)

LIVE_CAMERA_STEP = 10
FULL_PICTURE_STEP = 10

shutterSpeeds = [333333, 25000, 16666, 11111, 8000, 5555, 4166, 4000, 2857, 1333, 1000]
shutterSpeedNames = ["30", "45", "60", "90", "125", "180", "250", "350", "500", "750", "1000"]
isoSpeeds = [100, 200, 400, 600, 800]
exposureComps = [-12, -6, 0, 6, 12]
whiteBalanceModes = ["auto", "sunlight", "cloudy", "shade"]

class BirbWatcher:
    def __init__(self, config):
        self.config = config

        self.fullPictureTaker = picturetaker.PictureTaker(
            FULL_RES, 
            FULL_PICTURE_STEP, 
            f"{config.saveTo}/full", 
            picturetaker.filename_filestamp
        )
        self.livePictureTaker = picturetaker.PictureTaker(
            LIVE_RES,
            LIVE_CAMERA_STEP,
            config.saveTo,
            picturetaker.filename_live_picture
        )

        self.shutterFlipper = OptionFlipper(shutterSpeeds, 2, shutterSpeedNames)
        self.isoFlipper = OptionFlipper(isoSpeeds, 1)
        self.exposureFlipper = OptionFlipper(exposureComps, 2)
        self.wbFlipper = OptionFlipper(whiteBalanceModes)

        self.pauseRecording = True

    def run(self, camera, mask):
        camera.shutter_speed = self.shutterFlipper.value
        camera.iso = self.isoFlipper.value
        camera.awb_mode = self.wbFlipper.value
        camera.exposure_compensation = self.exposureFlipper.value
        camera.resolution = PREVIEW_RES
        rawCapture = PiRGBArray(camera, size=PREVIEW_RES)

        return self.__loop(camera, rawCapture, mask)

    def __loop(self, camera, rawCapture, mask):
        average = None
        mask_resolution = common.get_mask_real_size(mask, PREVIEW_RES)
        mask_bounds = common.get_mask_coords(mask, PREVIEW_RES)

        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            (now, masked, gray) = self.__take_preview(rawCapture, mask_bounds)

            if average is None:
                average = self.__initialize_average(gray)
                continue

            (newAverage, frameDelta, thresh, convertAvg) = self.__process_average(average, gray)
            average = newAverage

            # detect contours and determine if any are big enough to trigger a picture
            contours = self.__find_contours(thresh)
            shouldTrigger = self.__should_trigger(contours)
            
            # take our pictures if it's time
            didTakeFullPicture = False
            self.livePictureTaker.take_picture(camera, rawCapture)
            
            if not self.pauseRecording and shouldTrigger: 
                didTakeFullPicture = self.fullPictureTaker.take_picture(camera, rawCapture)

                if didTakeFullPicture:
                    filename = picturetaker.filename_filestamp()
                    cv2.imwrite(f"{self.config.saveTo}/thumb/{filename}", now)

            # visualize
            if self.config.debugMode:
                self.__show_debug(contours, masked, now, thresh, convertAvg, mask_resolution, frameDelta, didTakeFullPicture)

            if not self.__key_listener(camera):
                return False

    def __take_preview(self, rawCapture, mask_bounds):
        now = rawCapture.array
        gray = self.__blur_and_grayscale(now)
        #now = imutils.resize(now, 640, 480)
        rawCapture.truncate(0)

        masked = common.extract_image_region(now, mask_bounds)
        gray = common.extract_image_region(gray, mask_bounds)

        return (now, masked, gray)


    def __blur_and_grayscale(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        return gray

    def __initialize_average(self, gray):
        return gray.copy().astype('float')

    def __process_average(self, average, gray):
        # calculate delta
        cv2.accumulateWeighted(gray, average, 0.1)
        convertAvg = cv2.convertScaleAbs(average)
        frameDelta = cv2.absdiff(gray, convertAvg)
        thresh = cv2.threshold(frameDelta, 90, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        return (average, frameDelta, thresh, convertAvg)

    def __find_contours(self, thresh):
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        return cnts

    def __should_trigger(self, contours):
        for c in contours:
            if cv2.contourArea(c) < 600:
                continue
            
            return True
        
        return False

    def __compare_histograms(self, frame, key):
        (ahist, adata) = common.build_histogram(frame)
        (bhist, bdata) = common.build_histogram(key)
        compare = common.compare_histograms(ahist, bhist)

        return compare

    def __key_listener(self, camera):
        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            camera.shutter_speed = self.shutterFlipper.next()
            
        if key == ord("a"):
            camera.shutter_speed = self.shutterFlipper.previous()

        if key == ord("i"):
            camera.iso = self.isoFlipper.next()

        if key == ord("u"):
            camera.iso = self.isoFlipper.previous()

        if key == ord("e"):
            camera.exposure_compensation = self.exposureFlipper.next()

        if key == ord("w"):
            camera.exposure_compensation = self.exposureFlipper.previous()

        if key == ord("b"):
            camera.awb_mode = self.wbFlipper.next()

        if key == ord("v"):
            camera.awb_mode = self.wbFlipper.previous()

        if key == ord("p"):
           self.pauseRecording = not self.pauseRecording

        if key == ord("q"):
            return False

        return True

    def __show_debug(self, contours, masked, now, thresh, convertAvg, mask_resolution, frameDelta, didTakeFullPicture):
        for c in contours:
            if cv2.contourArea(c) < 600:
                continue
            
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(masked, (x, y), (x + w, y + h), (0, 255, 0), 2)

        convertAvg = cv2.cvtColor(convertAvg, cv2.COLOR_GRAY2BGR)
        frameDelta = cv2.cvtColor(frameDelta, cv2.COLOR_GRAY2BGR)
        thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

        histogram = self.__draw_exposure_histogram(cv2.cvtColor(now, cv2.COLOR_BGR2GRAY), mask_resolution)

        cv2.putText(histogram, f"(S)hutter (A): {self.shutterFlipper.label}", (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv2.putText(histogram, f"(E)xposure (W): {self.exposureFlipper.label}", (10, 50), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv2.putText(histogram, f"(I)SO (U): {self.isoFlipper.label}", (10, 80), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv2.putText(histogram, f"W(B) (V): {self.wbFlipper.label}", (10, 110), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        
        if self.pauseRecording:
            cv2.putText(histogram, "PAUSED", (90, 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        rtop = cv2.hconcat([masked, histogram])
        rbottom = cv2.hconcat([frameDelta, thresh])
        quad = cv2.vconcat([rtop, rbottom])
        cv2.imshow('processors', quad)

        if didTakeFullPicture:
            stamp = picturetaker.filename_filestamp()
            cv2.imwrite(f"{self.config.saveTo}/debug/{stamp}", quad)

    def __draw_exposure_histogram(self, now, resolution):
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