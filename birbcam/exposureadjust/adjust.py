from .exposurestate import ExposureState
from .sleep import Sleep
from .utils import calculate_exposure
import time
import logging

class Adjust(ExposureState):
    def __init__(self):
        super().__init__()
        self._nextLookTime = 0
        self._lastExposure = None

    def reset_last_exposure(self):
        self._lastExposure = None

    def update(self, camera, image):
        if time.time() < self._nextLookTime:
            return

        exposure = calculate_exposure(image)

        if self.check_exposure(exposure):
            logging.info(f" >> Stop adjust")
            self.finish()
        else:
            self._isAdjusting = True
            self._lastExposure = exposure

            self.do_adjust(camera)
            self._nextLookTime = time.time() + 2

    def check_exposure(self, exposure):
        return True

    def do_adjust(self, camera):
        return

    def finish(self):
        self._isAdjusting = False
        self._changeState(Sleep(self._exposurer.sleepInterval))