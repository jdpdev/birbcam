from ..optionflipper import OptionFlipper

class ExposureState:
    def __init__(self):
        self._shutterFlipper = None
        self._changeState = None
        self._targetLevel = None
        self._levelMargin = None
        self._isAdjusting = False

    def setup(self):
        return

    def take_over(self, shutterFlipper: OptionFlipper, changeState, targetLevel: int, levelMargin: int):
        self._shutterFlipper = shutterFlipper
        self._changeState = changeState
        self._targetLevel = targetLevel
        self._levelMargin = levelMargin
        self.setup()

    def update(self, camera, image):
        return

    def release(self):
        return

    @property
    def isAdjustingExposure(self):
        return self._isAdjusting