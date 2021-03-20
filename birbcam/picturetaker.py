from time import time
from datetime import datetime

class PictureTaker:
    def __init__(self, resolution, cooldown, saveTo, fileNamer):
        self.nextPictureTime = 0
        self.resolution = resolution
        self.cooldown = cooldown
        self.saveTo = saveTo
        self.fileNamer = fileNamer

    @property
    def readyForPicture(self):
        return time() >= self.nextPictureTime

    def take_picture(self, camera):
        if not self.readyForPicture: 
            return False

        restoreResolution = camera.resolution
        camera.resolution = self.resolution
        camera.capture(self.__save_path())
        camera.resolution = restoreResolution

        self.__schedule_next_picture()
        return True

    def __save_path(self):
        return f"{self.saveTo}/{self.fileNamer()}"

    def __schedule_next_picture(self):
        self.nextPictureTime = time() + self.cooldown

def filename_live_picture():
    return "live.jpg"

def filename_filestamp():
    date = datetime.now()
    return date.strftime("%Y-%m-%d-%H-%M-%S") + ".jpg"