from ..optionflipper import OptionFlipper
from .exposurestate import ExposureState
from .watch import Watch
from cv2 import normalize, calcHist, cvtColor, COLOR_BGR2GRAY
from time import time
import numpy as np
import logging

class ExposureAdjust:
    def __init__(self, shutterFlipper: OptionFlipper, isoFlipper: OptionFlipper, interval: int = 300, targetLevel: int = 110, margin: int = 10):
        """
        Parameters
        ----------
        shutterFlipper : OptionFlipper
        isoFlipper : OptionFlipper
        """
        self.shutterFlipper = shutterFlipper
        self.isoFlipper = isoFlipper
        self.targetLevel = targetLevel

        self._interval = interval
        self._actualMargin = margin

        self._currentState = None
        self.change_state(Watch(self._interval))

    @property
    def isAdjustingExposure(self):
        return self._currentState.isAdjustingExposure if self._currentState != None else False

    @property
    def targetExposure(self):
        return self.targetLevel

    @targetExposure.setter
    def targetExposure(self, value):
        self.targetLevel = value

    @property
    def sleepInterval(self):
        return self._interval

    @property
    def levelError(self):
        return self._actualMargin

    def change_state(self, nextState: ExposureState):
        if self._currentState != None:
            self._currentState.release()

        self._currentState = nextState

        if self._currentState == None:
            self._currentState = Watch(self._interval)

        if self._currentState != None:
            self._currentState.take_over(self, 
                self.shutterFlipper, 
                self.isoFlipper, 
                self.change_state, 
                self.targetExposure, 
                self._actualMargin
            )
        
    def check_exposure(self, camera, image):
        self._currentState.update(camera, image)
        return self._currentState.isAdjustingExposure