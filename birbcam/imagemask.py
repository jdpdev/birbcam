from picamerax.array import PiRGBArray
from picamerax import PiCamera
from birbcam.common import draw_aim_grid, draw_mask
import cv2

from .rectanglegrabber import RectangleGrabber

class ImageMask:
    maskWindowName = "Set Detection Region"
    maskWindowResolution = (800, 600)

    def __init__(self):
        self._mask = (0.25, 0.25, 0.5, 0.5)

    @property
    def mask(self):
        """The region to mask"""
        return self._mask

    def run(self, camera):
        cv2.namedWindow(self.maskWindowName)
        self.maskRect = RectangleGrabber(
            self.maskWindowName, 
            self.maskWindowResolution,
            onDrag = lambda bounds: self.__set_mask_rect(bounds),
            onEnd = lambda bounds: self.__set_mask_rect(bounds) 
        )

        camera.resolution = self.maskWindowResolution
        rawCapture = PiRGBArray(camera, size=self.maskWindowResolution)

        keepGoing = self.__loop(camera, rawCapture)
        cv2.destroyAllWindows()

        return keepGoing

    def __loop(self, camera, rawCapture):
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    
            image = frame.array
            draw_mask(image, self._mask, self.maskWindowResolution)
            draw_aim_grid(image, self.maskWindowResolution)
            rawCapture.truncate(0)

            cv2.imshow(self.maskWindowName, image)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                return True

            if key == ord("x"):
                return False

    def __set_mask_rect(self, bounds):
        (tl, br) = bounds
        rx = self.maskWindowResolution[0]
        ry = self.maskWindowResolution[1]

        x = tl[0] / rx
        y = tl[1] / ry
        w = (br[0] - tl[0]) / rx
        h = (br[1] - tl[1]) / ry

        self._mask = (x, y, w, h)