from picamerax.array import PiRGBArray
from picamerax import PiCamera
from time import time, sleep
from birbcam.common import get_mask_real_size, get_mask_coords, extract_image_region, build_histogram, compare_histograms
import cv2
import numpy as np
import imutils
import sched
import logging
from datetime import datetime
from setproctitle import setproctitle
from birbvision import ClassifyBird
from .picturelogger import PictureLogger

from birbcam.picturetaker import PictureTaker, filename_filestamp, filename_live_picture
from .birbconfig import BirbConfig
from .optionflipper import OptionFlipper
from .optioncounter import OptionCounter
from .exposureadjust import ExposureAdjust
from .exposureadjust.utils import build_image_histogram, calculate_exposure_from_histogram

PREVIEW_RES = (800, 600)

shutterSpeeds =     [40000, 33333, 25000, 20000, 16667, 12500, 10000, 8000,  5556,  5000,  4000,  3125,  2500,  2000,  1563,  1250,  1000,   800]
shutterSpeedNames = ["25",  "30",  "40",  "50",  "60",  "80",  "100", "125", "180", "200", "250", "320", "400", "500", "640", "800", "1000", "1250"]
isoSpeeds = [100, 200, 400, 600, 800]
exposureComps = [-12, -6, 0, 6, 12]
whiteBalanceModes = ["auto", "sunlight", "cloudy", "shade"]

class BirbWatcher:
    def __init__(self, config: BirbConfig):
        self.config = config
        
        self.fullPictureTaker = PictureTaker(
            config.fullPictureResolution, 
            config.fullPictureInterval, 
            f"{config.saveTo}/full", 
            filename_filestamp
        )
        self.livePictureTaker = PictureTaker(
            config.livePictureResolution,
            config.livePictureInterval,
            config.saveTo,
            filename_live_picture
        )

        self.shutterFlipper = OptionFlipper(shutterSpeeds, 6, shutterSpeedNames)
        self.isoFlipper = OptionFlipper(isoSpeeds, 1)
        self.exposureFlipper = OptionFlipper(exposureComps, 2)
        self.wbFlipper = OptionFlipper(whiteBalanceModes)
        self.thresholdCounter = OptionCounter(0, 255, 5, self.config.threshold)
        self.contourCounter = OptionCounter(0, 1500, 50, self.config.contourArea)

        self.exposureAdjust = ExposureAdjust(
            self.shutterFlipper, 
            self.isoFlipper, 
            interval=config.exposureInterval,
            targetLevel=config.exposureLevel,
            margin=config.exposureError
        )
        self.pauseRecording = True

        self.classifier = ClassifyBird()
        self.pictureLogger = PictureLogger(f"{config.saveTo}/pictures.txt")
        
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
        mask_resolution = get_mask_real_size(mask, PREVIEW_RES)
        mask_bounds = get_mask_coords(mask, PREVIEW_RES)

        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            (now, masked, gray) = self.__take_preview(rawCapture, mask_bounds)

            if average is None:
                average = self.__initialize_average(gray)
                continue

            isCheckingExposure = self.exposureAdjust.check_exposure(camera, gray)

            (newAverage, frameDelta, thresh, convertAvg) = self.__process_average(average, gray)
            average = newAverage

            # detect contours and determine if any are big enough to trigger a picture
            contours = self.__find_contours(thresh)
            shouldTrigger = self.__should_trigger(contours)
            
            # take our pictures if it's time
            didTakeFullPicture = (False, None)
            classifyResults = []
            self.livePictureTaker.take_picture(camera)
            
            if not self.pauseRecording and not isCheckingExposure and shouldTrigger and self.fullPictureTaker.readyForPicture: 
                classify = self.__classify_image(now)
                classifyResults = classify[1]

                if classify[0]:
                    #logging.info(f"[birbvision] shoot: {classifyResults[0].label} @ {classifyResults[0].confidence:.2f}")
                    didTakeFullPicture = self.fullPictureTaker.take_picture(camera)
                    if didTakeFullPicture[0]:
                        thumbfile = f"{self.config.saveTo}/thumb/{didTakeFullPicture[1]}"
                        cv2.imwrite(thumbfile, now)
                        self.pictureLogger.log_picture(didTakeFullPicture[2], thumbfile, classifyResults, self.shutterFlipper.label, self.isoFlipper.label)
                else:
                #    logging.info(f"[birbvision] ignore: {classifyResults[0].label} @ {classifyResults[0].confidence:.2f}")
                    self.fullPictureTaker.reset_time()

            # visualize
            window = (None, None)
            if self.config.debugMode:
                window = self.__show_debug(contours, masked, now, gray, thresh, convertAvg, mask_resolution, frameDelta, didTakeFullPicture, isCheckingExposure, classifyResults)
            else:
                window = self.__show_control_console(gray, (600,400))

            if window[0] != None:
                cv2.imshow("console", window[1])

            if not self.__key_listener(camera):
                return False

    def __classify_image(self, image):
        classify = self.classifier.classify_image(image)
        results = classify.get_top_results(5)
        return (results[0].label != "None" and results[0].confidence > 0.30, results)

    def __take_preview(self, rawCapture, mask_bounds):
        now = rawCapture.array
        gray = self.__blur_and_grayscale(now)
        #now = imutils.resize(now, 640, 480)
        rawCapture.truncate(0)

        masked = extract_image_region(now, mask_bounds)
        gray = extract_image_region(gray, mask_bounds)

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
        thresh = cv2.threshold(frameDelta, self.thresholdCounter.value, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        return (average, frameDelta, thresh, convertAvg)

    def __find_contours(self, thresh):
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        return cnts

    def __should_trigger(self, contours):
        for c in contours:
            if cv2.contourArea(c) < self.contourCounter.value:
                continue
            
            return True
        
        return False

    def __compare_histograms(self, frame, key):
        (ahist, adata) = build_histogram(frame)
        (bhist, bdata) = build_histogram(key)
        compare = compare_histograms(ahist, bhist)

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

        if key == ord("t"):
            self.thresholdCounter.next()

        if key == ord("r"):
            self.thresholdCounter.previous()

        if key == ord("c"):
            self.contourCounter.next()

        if key == ord("x"):
            self.contourCounter.previous()

        if key == ord("="):
            self.config.exposureLevel += 2
            self.exposureAdjust.targetExposure = self.config.exposureLevel

        if key == ord("-"):
            self.config.exposureLevel -= 2
            self.exposureAdjust.targetExposure = self.config.exposureLevel

        if key == ord("p"):
           self.pauseRecording = not self.pauseRecording

        if key == ord("d"):
            self.config.debugMode = not self.config.debugMode

        if key == ord("q"):
            return False

        return True

    def __show_control_console(self, exposure, resolution):
        canvas = self.__draw_control_panel(exposure, resolution)
        return ('control console', canvas)

    def __show_debug(self, contours, masked, now, exposure, thresh, convertAvg, mask_resolution, frameDelta, didTakeFullPicture, isCheckingExposure, classifyResults):
        for c in contours:
            if cv2.contourArea(c) < self.contourCounter.value:
                continue
            
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(masked, (x, y), (x + w, y + h), (0, 255, 0), 2)

        convertAvg = cv2.cvtColor(convertAvg, cv2.COLOR_GRAY2BGR)
        frameDelta = cv2.cvtColor(frameDelta, cv2.COLOR_GRAY2BGR)
        thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

        histogram = self.__draw_control_panel(exposure, mask_resolution)

        rtop = cv2.hconcat([masked, histogram])
        rbottom = cv2.hconcat([frameDelta, thresh])
        quad = cv2.vconcat([rtop, rbottom])
        
        if didTakeFullPicture[0] == True:
            bvdebug = np.zeros((mask_resolution[1],mask_resolution[0],3), np.uint8)

            y = 20
            yStep = 20
            for r in classifyResults:
                cv2.putText(bvdebug, f"{r.confidence:.2f}: {r.label}", (10, y), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
                y += yStep

            dtop = cv2.hconcat([masked, bvdebug])
            dbottom = cv2.hconcat([frameDelta, thresh])
            dquad = cv2.vconcat([dtop, dbottom])

            cv2.imwrite(f"{self.config.saveTo}/debug/{didTakeFullPicture[1]}", dquad)

        return ('debug console', quad)

    def __draw_control_panel(self, exposure, mask_resolution):
        histogram = self.__draw_exposure_histogram(exposure, mask_resolution)

        cv2.putText(histogram, f"(S)hutter (A): {self.shutterFlipper.label}", (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv2.putText(histogram, f"(E)xposure (W): {self.exposureFlipper.label}", (10, 40), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv2.putText(histogram, f"(I)SO (U): {self.isoFlipper.label}", (10, 60), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv2.putText(histogram, f"W(B) (V): {self.wbFlipper.label}", (10, 80), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv2.putText(histogram, f"(T)hreshold (R): {self.thresholdCounter.label}", (10, 100), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        cv2.putText(histogram, f"(C)ontour (X): {self.contourCounter.label}", (10, 120), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)

        if self.config.debugMode:
            cv2.putText(histogram, f"(D) Console", (10, 140), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        else:
            cv2.putText(histogram, f"(D) Debug", (10, 140), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
        
        if self.pauseRecording:
            cv2.putText(histogram, "PAUSED", (180, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
        
        if self.exposureAdjust.isAdjustingExposure:
            cv2.putText(histogram, "EXPOSURE", (180, 60), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        return histogram

    def __draw_exposure_histogram(self, now, resolution):
        halfHeight = int(resolution[1] / 2)
        blank = np.zeros((resolution[1],resolution[0],3), np.uint8)

        histogram = build_image_histogram(now)
        average = calculate_exposure_from_histogram(histogram)
        normalized = np.interp(histogram, (histogram.min(), histogram.max()), (0, halfHeight))

        for x, y in enumerate(normalized):
            color = (255, 255, 255)
            height = resolution[1] - y

            if x == self.exposureAdjust.targetExposure:
                color = (0, 255, 0)
                height = resolution[1] - 255
            elif x == average:
                color = (255, 255, 0)
                height = resolution[1] - 255

            cv2.line(blank, (x, resolution[1]),(x, height), color)

        #compare = cv2.compareHist(key_hist, now_hist, cv2.HISTCMP_CHISQR)
        cv2.putText(blank,"%d" % average,(average + 5, resolution[1] - 100),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255, 255, 0))
        cv2.putText(blank,"+",(self.exposureAdjust.targetExposure + 5, resolution[1] - 80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0))
        cv2.putText(blank,"-",(self.exposureAdjust.targetExposure - 15, resolution[1] - 80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 255, 0))

        return blank
