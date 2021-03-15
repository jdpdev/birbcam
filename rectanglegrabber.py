import cv2

class RectangleGrabber:
    def __init__(self, windowName, resolution, onEnd, preserveAspectRatio = False):
        self.start = (0,0)
        self._isDragging = False
        self.onEnd = onEnd
        self.preserveAspectRatio = preserveAspectRatio

        if preserveAspectRatio:
            self.aspectRatio = resolution[1] / resolution[0]

        cv2.setMouseCallback(windowName, self.__click_handler)

    @property
    def isDragging(self): return self._isDragging

    @property
    def bounds(self): return (self.start, self.end)

    def reset(self):
        self.start = (0,0)
        self.end = resolution
        self._isDragging = False
        self.__report_end()

    def __click_handler(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start = (x, y)
            self.end = self.end = self.__calculate_br(x, y)
            self._isDragging = True
            return

        if event == cv2.EVENT_LBUTTONUP:
            self._isDragging = False
            self.__report_end()
            return

        if event == cv2.EVENT_MOUSEMOVE:
            if self.isDragging:
                self.end = self.__calculate_br(x, y)
            return

    def __calculate_br(self, brx, bry):
        if not self.preserveAspectRatio:
            return (brx, bry)

        h = round((brx - self.start[0]) * self.aspectRatio)
        return (brx, self.start[1] + h)

    def __report_end(self):
        self.onEnd(self.start, self.end)

    