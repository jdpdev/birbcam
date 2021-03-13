from picamerax.array import PiRGBArray
from picamerax import PiCamera
import common
import cv2

class FocusAssist:
    focusWindowName = "Focus Assist"
    focusWindowResolution = (800, 600)

    def __init__(self):
        self.focusStart = (0, 0)
        self.focusEnd = self.focusWindowResolution
        self.isDragging = False

    def run(self, camera):
        camera.resolution = self.focusWindowResolution
        rawCapture = PiRGBArray(camera, size=self.focusWindowResolution)

        cv2.namedWindow(self.focusWindowName)
        cv2.setMouseCallback(self.focusWindowName, 
            lambda event, x, y, flags, param: self.__focus_click_event(event, x, y, camera, self.focusWindowResolution))

        keepGoing = self.__camera_loop(camera, rawCapture)
        cv2.destroyAllWindows()

        return keepGoing

    def __camera_loop(self, camera, rawCapture):
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

            image = frame.array
            rawCapture.truncate(0)

            laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()

            # drag rect
            if self.isDragging:
                cv2.rectangle(image, self.focusStart, self.focusEnd, (255, 0, 255), 2)

            # focus amount
            cv2.rectangle(image, (0,0), (120, 40), (255, 0, 255), -1)
            cv2.putText(image, str(int(laplacian_var)), (5,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

            # crosshair
            common.draw_aim_grid(image, self.focusWindowResolution)
            
            cv2.imshow(self.focusWindowName, image)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("r"):
                self.__set_zoom_rect(camera, (0,0), self.focusWindowResolution, self.focusWindowResolution)

            if key == ord("q"):
                return True

            if key == ord("x"):
                return False

    def __focus_click_event(self, event, x, y, camera, resolution):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.focusStart = (x, y)
            self.focusEnd = (x, y)
            self.isDragging = True
            return

        if event == cv2.EVENT_LBUTTONUP:
            self.isDragging = False
            self.__set_zoom_rect(camera, self.focusStart, self.focusEnd, self.focusWindowResolution)
            return

        if event == cv2.EVENT_MOUSEMOVE:
            if self.isDragging:
                self.focusEnd = (x, y)
            return

    def __set_zoom_rect(self, camera, tl, br, resolution):
        rx = resolution[0]
        ry = resolution[1]

        x = tl[0] / rx
        y = tl[1] / ry
        w = (br[0] - tl[0]) / rx
        h = (br[1] - tl[1]) / ry
        camera.zoom = (x, y, w, h)