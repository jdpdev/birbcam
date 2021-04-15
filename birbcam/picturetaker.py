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
            return (False, None)

        filename = self.fileNamer()
        filepath = self.__save_path(filename)

        restoreResolution = camera.resolution
        camera.resolution = self.resolution
        camera.capture(filepath)
        camera.resolution = restoreResolution

        self.__schedule_next_picture()
        return (True, filename, filepath)

    def __save_path(self, name = None):
        if name == None:
            name = self.fileNamer()
            
        return f"{self.saveTo}/{name}"

    def reset_time(self):
        self.__schedule_next_picture()

    def __schedule_next_picture(self):
        self.nextPictureTime = time() + self.cooldown

def filename_live_picture():
    return "live.jpg"

def filename_filestamp():
    date = datetime.now()
    return date.strftime("%Y-%m-%d-%H-%M-%S") + ".jpg"