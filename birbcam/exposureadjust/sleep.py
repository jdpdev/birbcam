from .exposurestate import ExposureState
import time

class Sleep(ExposureState):
    def __init__(self, waitTime, next):
        super().__init__()
        self._releaseTime = time() + waitTime
        self._nextState = next

    def update(self, camera, image):
        if time() < self._releaseTime:
            return

        self._changeState(self._nextState)
