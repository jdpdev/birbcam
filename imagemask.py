from picamerax.array import PiRGBArray
from picamerax import PiCamera
import common
import cv2

class ImageMask:
    maskWindowName = "Set Detection Region"
    maskWindowResolution = (800, 600)

    def __init__(self):
        self._mask = (0.5, 0.5)

    @property
    def mask(self):
        """The region to mask"""
        return self._mask

    def run(self, camera):
        camera.zoom = (0, 0, 1, 1)
        camera.resolution = self.maskWindowResolution
        rawCapture = PiRGBArray(camera, size=self.maskWindowResolution)

        cv2.namedWindow(self.maskWindowName)
        cv2.setMouseCallback(self.maskWindowName, self.__mask_click_event)

        keepGoing = self.__loop(camera, rawCapture)
        cv2.destroyAllWindows()

        return keepGoing

    def __loop(self, camera, rawCapture):
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    
            image = frame.array
            common.draw_mask(image, self._mask, self.maskWindowResolution)
            common.draw_aim_grid(image, self.maskWindowResolution)
            rawCapture.truncate(0)

            cv2.imshow(self.maskWindowName, image)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                return True

            if key == ord("x"):
                return False

    def __mask_click_event(self, event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN:
            return

        self._mask = common.change_mask_size(x, y, self.maskWindowResolution)