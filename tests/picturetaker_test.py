from birbcam.picturetaker import PictureTaker, filename_filestamp, filename_live_picture
from time import time
from datetime import datetime
from collections import deque

class MockCamera:
    def __init__(self, startResolution, expectResolution, expectSaveTo):
        self.startResolution = startResolution
        self.expectResolution = deque(expectResolution)
        self.expectSaveTo = expectSaveTo
        self._resolution = startResolution

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self, r):
        expect = self.expectResolution.popleft()
        assert expect == r

    def capture(self, path):
        assert path == self.expectSaveTo

def test_filename_live_picture():
    assert filename_live_picture() == "live.jpg"

def test_filename_filestamp():
    date = datetime.now()
    expect = date.strftime("%Y-%m-%d-%H-%M-%S") + ".jpg"
    assert expect == filename_filestamp()

def test_should_immediately_be_ready_to_take_picture():
    taker = PictureTaker("800x600", 5, ".", filename_live_picture)
    assert taker.readyForPicture == True

def test_should_take_picture():
    taker = PictureTaker("1600x1200", 5, ".", filename_live_picture)
    mockCamera = MockCamera("800x600", ["1600x1200", "800x600"], "./" + filename_live_picture())

    assert taker.take_picture(mockCamera)
