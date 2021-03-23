from .exposurestate import ExposureState
from time import time
import logging

class Sleep(ExposureState):
    def __init__(self, waitTime):
        super().__init__()
        self._releaseTime = time() + waitTime

    def setup(self):
        logging.info(f"[Sleep] take_over")

    def update(self, camera, image):
        if time() < self._releaseTime:
            return

        self._changeState(None)
