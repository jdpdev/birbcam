from .exposurestate import ExposureState
from .sleep import Sleep
from .watch import Watch
from .utils import calculate_exposure
import time

class Adjust(ExposureState):
    def __init__(self):
        self._nextLookTime = 0
        self._lastExposure = None

    def update(self, camera, image):
        if time() < self._nextLookTime:
            return

        exposure = calculate_exposure(image)

        if self.check_exposure(exposure):
            self.finish()

        self._lastExposure = exposure

        self.do_adjust(camera)
        self._nextLookTime = time() + 1

    def check_exposure(self, exposure):
        return True

    def do_adjust(self, camera):
        return

    def finish(self):
        self._changeState(Sleep(300), Watch(10))