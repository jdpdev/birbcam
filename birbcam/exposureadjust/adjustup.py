from .adjust import Adjust
import numpy as np
import logging

class AdjustUp(Adjust):
    def setup(self):
        logging.info(f"[AdjustUp] take_over")

    def do_adjust(self, camera):
        if self._shutterFlipper.is_at_end:
            self.finish()
            return

        camera.shutter_speed = self._shutterFlipper.next()
    
    def check_exposure(self, exposure):
        delta = exposure - self._targetLevel
        logging.info(f"[AdjustUp] {exposure}, {delta} < {self._levelMargin}, {self._lastExposure}")
        
        if self._lastExposure != None:
            lastDelta = self._lastExposure - self._targetLevel

            # stop if crossed line
            if np.sign(delta) != np.sign(lastDelta):
                return True

        # stop if close enough
        if abs(delta) < self._levelMargin:
            return True

        return False
