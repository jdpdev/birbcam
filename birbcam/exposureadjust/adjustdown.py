from .adjust import Adjust
import numpy as np
import logging

class AdjustDown(Adjust):
    def setup(self):
        logging.info(f"[AdjustDown] take_over")

    def do_adjust(self, camera):
        if self._shutterFlipper.is_at_start:
            self.finish()
            return

        camera.shutter_speed = self._shutterFlipper.previous()
    
    def check_exposure(self, exposure):
        delta = exposure - self._targetLevel
        logging.info(f"[AdjustDown] {exposure}, {delta} < {self._levelMargin}, {self._lastExposure}")
        
        if self._lastExposure != None:
            lastDelta = self._lastExposure - self._targetLevel

            # stop if crossed line
            if np.sign(delta) != np.sign(lastDelta):
                return True

        # stop if close enough
        if abs(delta) < self._levelMargin:
            return True

        return False
