from ..optionflipper import OptionFlipper
from .exposurestate import ExposureState
from .watch import Watch
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
        self._currentState = None
        self.change_state(Watch(10))

    @property
    def isAdjustingExposure(self):
        return self._currentState.isAdjustingExposure if self._currentState != None else False

    @property
    def targetExposure(self):
        return self.targetLevel

    def change_state(self, nextState: ExposureState):
        if self._currentState != None:
            self._currentState.release()

        self._currentState = nextState

        if self._currentState == None:
            self._currentState = Watch(10)

        if self._currentState != None:
            self._currentState.take_over(self.shutterFlipper, self.change_state, self.targetExposure, self.desiredMargin)

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
        self._currentState.update(camera, image)
        return self._currentState.isAdjustingExposure