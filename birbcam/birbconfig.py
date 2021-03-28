import configparser
import os
from argparse import ArgumentParser

class BirbConfig:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(f"{os.path.dirname(os.path.realpath(__file__))}/../config.ini")

        self.ap = ArgumentParser()
        self.ap.add_argument("-f", "--file", default=None, help="path to the log file")
        self.ap.add_argument("-n", "--no-capture", help="do not capture photos", action='store_true')
        self.ap.add_argument("-s", "--save", help="picture save location", default=None)
        self.ap.add_argument("-ls", "--lensshading", help="which lens shading compensation to use", default=None)

        self.args = vars(self.ap.parse_args())

    def __has_argument(self, key):
        return self.args.get(key)

    def __clean_string(self, string):
        if string == None: return None
        return string.strip("'")

    # ********************
    #  [Saving] Save location details
    # ********************
    @property
    def saveTo(self) -> str:
        """
        Root save location for images

        :return: Root save path
        :rtype: str
        """
        arg = self.args.get("save")
        if arg != None: return arg

        return self.config["Saving"]["Directory"]

    @property
    def livePictureInterval(self) -> float:
        """ Number of seconds between each live picture.

        :returns: Number of seconds between each live picture, or 0 to disable
        :rtype: float
        """
        return float(self.config["Saving"]["LivePictureInterval"])

    @property
    def fullPictureInterval(self) -> float:
        """ 
        Minimum number of seconds between each full picture. The actual elapsed time between full pictures can be longer than this if there is no picture event after the interval.

        :returns: Number of seconds between each full picture
        :rtype: float
        """
        return float(self.config["Saving"]["LivePictureInterval"])

    @property
    def fullPictureResolution(self) -> str:
        """
        Resolution is a string as dimensions: <width>x<height>
        Note that the camera modules only natively supports certain resolutions, and the supported resolutions depend on the camera module version. Any other resolution will be scaled by the GPU.
        A list of native resolutions can be found on the camera module documentation under the '--mode' flag: https://www.raspberrypi.org/documentation/raspbian/applications/camera.md

        :returns: The resolution to use for full pictures
        :rtype: str
        """
        return self.config["Saving"]["FullPictureResolution"]

    @property
    def livePictureResolution(self) -> str:
        """
        Resolution is a string as dimensions: <width>x<height>
        Note that the camera modules only natively supports certain resolutions, and the supported resolutions depend on the camera module version. Any other resolution will be scaled by the GPU.
        A list of native resolutions can be found on the camera module documentation under the '--mode' flag: https://www.raspberrypi.org/documentation/raspbian/applications/camera.md

        :returns: The resolution to use for full pictures
        :rtype: str
        """
        return self.config["Saving"]["LivePictureResolution"]

    # ********************
    #  [Detection] Detection parameters
    # ********************
    @property
    def threshold(self) -> int:
        return int(self.config["Detection"]["Threshold"])
    
    @property
    def contourArea(self) -> int:
        return int(self.config["Detection"]["ContourArea"])

    @property 
    def exposureInterval(self) -> int:
        return int(self.config["Detection"]["ExposureInterval"])

    @property 
    def exposureLevel(self) -> int:
        return int(self.config["Detection"]["ExposureLevel"])

    @exposureLevel.setter
    def exposureLevel(self, value: int):
        if value < 0:
            value = 0
        elif value > 200:
            value = 200

        self.config["Detection"]["ExposureLevel"] = str(value)

    @property 
    def exposureError(self) -> int:
        return int(self.config["Detection"]["ExposureError"])
        

    # ********************
    #  [Debug] Debug details
    # ********************
    @property
    def debugMode(self) -> bool:
        #arg = self.args.get("debug")
        #if arg != None: return arg

        return self.config["Debug"].getboolean("Enable", False)

    @debugMode.setter
    def debugMode(self, value: bool):
        self.config["Debug"]["Enable"] = str(value)

    @property
    def logFile(self) -> str:
        loc = self.config["Debug"].get("LogFile", None)
        if loc is None: return None

        return f"{os.path.dirname(os.path.realpath(__file__))}/{loc}"

    @property
    def noCaptureMode(self) -> bool:
        arg = self.args.get("no-capture")
        if arg != None: return arg

        return self.config["Debug"].getboolean("NoCapture", False)