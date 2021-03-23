from .exposurestate import ExposureState
from .adjustup import AdjustUp
from .adjustdown import AdjustDown
from .utils import calculate_exposure
from time import time
import logging

class Watch(ExposureState):
    def __init__(self, interval):
        super().__init__()
        self._interval = interval
        self.__increment_time()

    def setup(self):
        logging.info(f"[Watch] every {self._interval}")

    def update(self, camera, image):
        if time() < self._nextCheckTime:
            return

        level = calculate_exposure(image)
        delta = level - self._targetLevel
        logging.info(f"[Watch] level {level}, delta {delta}")

        if abs(delta) > self._levelMargin:
            if delta > 0:
                self._changeState(AdjustUp())
            else:
                self._changeState(AdjustDown())
        else:
            self.__increment_time()


    def __increment_time(self):
        self._nextCheckTime = time() + self._interval
