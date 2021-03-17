from time import time
from datetime import datetime
import cv2

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

    def take_picture(self, camera, rawCapture, thumbnail = None):
        if not self.readyForPicture: 
            return False

        filename = self.__get_file_name()

        restoreResolution = camera.resolution
        camera.resolution = self.resolution
        camera.capture(self.__save_path(filename))
        camera.resolution = restoreResolution

        if thumbnail != None:
            cv2.imwrite(f"{thumbnail[0]}{filename}", thumbnail[1])

        self.__schedule_next_picture()
        return True

    def __get_file_name(self):
        return self.fileNamer()

    def __save_path(self, file):
        return f"{self.saveTo}/{file}"

    def __schedule_next_picture(self):
        self.nextPictureTime = time() + self.cooldown

def filename_live_picture():
    return "live.jpg"

def filename_filestamp():
    date = datetime.now()
    return date.strftime("%Y-%m-%d-%H-%M-%S") + ".jpg"