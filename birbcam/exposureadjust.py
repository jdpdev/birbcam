from .optionflipper import OptionFlipper
from cv2 import normalize, calcHist, cvtColor, COLOR_BGR2GRAY
from time import time
import numpy as np
import logging

class ExposureAdjust:
    def __init__(self, shutterFlipper: OptionFlipper, isoFlipper: OptionFlipper, targetLevel: int = 120, margin: int = 10):
        """
        Parameters
        ----------
        shutterFlipper : OptionFlipper
        isoFlipper : OptionFlipper
        """
        self.shutterFlipper = shutterFlipper
        self.isoFlipper = isoFlipper
        self.targetLevel = targetLevel
        self._isAdjusting = False
        self.lastAdjustTime = time()
        self.checkExposureTime = 0
        self.lastAdjustLevel = None

        self.desiredMargin = margin
        self._actualMargin = margin

        self._undoLastStop = None

    @property
    def isAdjustingExposure(self):
        return self._isAdjusting

    @property
    def targetExposure(self):
        return self.targetLevel

    def increase_exposure(self, amount):
        level = self.targetExposure + amount
        self.set_target_exposure(level)

    def decrease_exposure(self, amount):
        level = self.targetExposure - amount
        self.set_target_exposure(level)

    def set_target_exposure(self, level):
        if level > 255:
            level = 255
        elif level < 0:
            level = 0
        
        self.targetLevel = level
        
    def check_exposure(self, camera, image):
        #logging.info(f"[check_exposure] {time() - self.lastAdjustTime}")

        if time() - self.lastAdjustTime < 10:
            return False

        if self._isAdjusting and time() < self.checkExposureTime:
            return True

        imageLevel = self.__calculate_exposure(image)
        #logging.info(f"[check_exposure] target: {self.targetLevel}, image: {imageLevel}")

        if abs(imageLevel - self.targetLevel) < self.desiredMargin:
            if not self._isAdjusting:
                return False
            else:
                return self.__finish_adjust()

        isAdjusting = False
        if self._isAdjusting:
            isAdjusting = self.__start_adjusting(camera, imageLevel)
        else:
            isAdjusting = self.__check_adjustment(camera, imageLevel)
        
        return isAdjusting

    def __start_adjusting(self, camera, imageLevel):
        logging.info(f"[__start_adjusting]")
        self._isAdjusting = True
        return self.__adjust(camera, imageLevel)

    def __check_adjustment(self, camera, imageLevel):
        now = time()

        if now < self.checkExposureTime:
            return True

        logging.info(f"[__check_adjustment]")
        return self.__adjust(camera, imageLevel)

    def __adjust(self, camera, imageLevel):
        self.checkExposureTime = time() + 1

        if self.lastAdjustLevel != None:
            lastDelta = self.lastAdjustLevel - self.targetLevel
            nowDelta = imageLevel - self.targetLevel

            # if sign switches, pick the closest
            if np.sign(nowDelta) != np.sign(lastDelta):
                if abs(lastDelta) > abs(nowDelta):
                    self._undoLastStop()

                return self.__finish_adjust()
        
        # stop up
        if self.targetLevel < imageLevel:
            logging.info(f"[__adjust] stop up")
            if self.shutterFlipper.is_at_end: return self.__finish_adjust()
            camera.shutter_speed = self.shutterFlipper.next()
            self._undoLastStop = self.shutterFlipper.previous

        # stop down
        else:
            logging.info(f"[__adjust] stop down")
            if self.shutterFlipper.is_at_start: return self.__finish_adjust()
            camera.shutter_speed = self.shutterFlipper.previous()
            self._undoLastStop = self.shutterFlipper.next

        self.lastAdjustLevel = imageLevel

        return True

    def __finish_adjust(self):
        logging.info(f"[__finish_adjust]")
        self._isAdjusting = False
        self.lastAdjustTime += 10
        return False


    def __calculate_exposure(self, image):
        luminance = cvtColor(image, COLOR_BGR2GRAY)
        histogram = calcHist([luminance], [0], None, [256], [0,255])
        data = np.int32(np.around(histogram))

        max = data.max()
        average = 0
        total = 0

        for x, y in enumerate(data):
            average += y * x
            total += y

        return int(average / total)