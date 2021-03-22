from .adjust import Adjust
import numpy as np

class AdjustDown(Adjust):
    def do_adjust(self, camera):
        if self._shutterFlipper.is_at_end:
            self.finish()
            return

        self._shutterFlipper.next()
    
    def check_exposure(self, exposure):
        delta = exposure - self._targetLevel
        lastDelta = self._lastExposure - self._targetLevel

        # stop if crossed line
        if np.sign(delta) != np.sign(lastDelta):
            return True

        # stop if close enough
        if abs(delta) < self._levelMargin:
            return True

        return False
