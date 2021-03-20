import cv2

class RectangleGrabber:
    def __init__(self, windowName, resolution, onDrag = None, onEnd = None, preserveAspectRatio = False):
        self.resolution = resolution
        self.start = (0,0)
        self.end = resolution
        self._isDragging = False
        self.onDrag = onDrag
        self.onEnd = onEnd
        self.preserveAspectRatio = preserveAspectRatio

        if preserveAspectRatio:
            self.aspectRatio = resolution[1] / resolution[0]

        cv2.setMouseCallback(windowName, self.__click_handler)

    @property
    def isDragging(self): return self._isDragging

    @property
    def bounds(self): 
        if self.start[0] <= self.end[0] and self.start[1] <= self.end[1]:
            return (self.start, self.end)
        elif self.start[0] > self.end[0] and self.start[1] > self.end[1]:
            return (self.end, self.start)
        elif self.start[0] > self.end[0]:
            return ((self.end[0], self.start[1]), (self.start[0], self.end[1]))
        else:
            return ((self.start[0], self.end[1]), (self.end[0], self.start[1]))

    def reset(self):
        self.start = (0,0)
        self.end = self.resolution
        self._isDragging = False
        self.__report_end()

    def __click_handler(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start = (x, y)
            self.end = (x, y)
            self._isDragging = True
            return

        if event == cv2.EVENT_LBUTTONUP:
            self._isDragging = False
            self.__report_end()
            return

        if event == cv2.EVENT_MOUSEMOVE:
            if self.isDragging:
                self.end = self.__calculate_br(x, y)

                if self.onDrag != None:
                    self.onDrag(self.bounds)
            return

    def __calculate_br(self, brx, bry):
        if not self.preserveAspectRatio:
            return (brx, bry)

        dx = brx - self.start[0]
        dy = bry - self.start[1]
        h = round(dx * self.aspectRatio)

        if dx > 0 and dy < 0 or dx < 0 and dy > 0:
            h *= -1

        return (brx, self.start[1] + h)

    def __report_end(self):
        if self.onEnd != None:
            self.onEnd(self.bounds)

    