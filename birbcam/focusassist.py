from picamerax.array import PiRGBArray
from picamerax import PiCamera
from birbcam.common import draw_aim_grid
import cv2

from .rectanglegrabber import RectangleGrabber

class FocusAssist:
    focusWindowName = "Focus Assist"
    focusWindowResolution = (800, 600)
    captureResolution = (3200, 2400)

    def __init__(self):
        self.focusStart = (0, 0)
        self.focusEnd = self.focusWindowResolution
        self.isDragging = False

        cv2.namedWindow(self.focusWindowName)

    def run(self, camera):
        self.zoomRect = RectangleGrabber(
            self.focusWindowName,
            self.focusWindowResolution,
            onEnd=lambda bounds: self.__set_zoom_rect(camera, bounds),
            preserveAspectRatio=True
        )

        camera.resolution = self.focusWindowResolution
        rawCapture = PiRGBArray(camera, size=self.focusWindowResolution)

        keepGoing = self.__camera_loop(camera, rawCapture)
        
        cv2.destroyAllWindows()
        camera.zoom = (0, 0, 1, 1)

        return keepGoing

    def __camera_loop(self, camera, rawCapture):
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

            image = frame.array
            rawCapture.truncate(0)

            laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()

            # drag rect
            if self.zoomRect.isDragging:
                (tl, br) = self.zoomRect.bounds
                cv2.rectangle(image, tl, br, (255, 0, 255), 2)

            # focus amount
            cv2.rectangle(image, (0,0), (120, 40), (255, 0, 255), -1)
            cv2.putText(image, str(int(laplacian_var)), (5,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

            # crosshair
            draw_aim_grid(image, self.focusWindowResolution)
            
            cv2.imshow(self.focusWindowName, image)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("r"):
                self.zoomRect.reset()

            if key == ord("q"):
                cv2.destroyWindow(self.focusWindowName)
                return True

            if key == ord("x"):
                cv2.destroyWindow(self.focusWindowName)
                return False

    def __set_zoom_rect(self, camera, bounds):
        (tl, br) = bounds
        rx = self.focusWindowResolution[0]
        ry = self.focusWindowResolution[1]

        x = tl[0] / rx
        y = tl[1] / ry
        w = (br[0] - tl[0]) / rx
        h = (br[1] - tl[1]) / ry
        camera.zoom = (x, y, w, h)