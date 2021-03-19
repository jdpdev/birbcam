import configparser
import os
from argparse import ArgumentParser

class BirbConfig:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(f"{os.path.dirname(os.path.realpath(__file__))}/config.ini")

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
    def saveTo(self):
        arg = self.args.get("save")
        if arg != None: return arg

        return self.config["Saving"]["Directory"]

    # ********************
    #  [Detection] Detection parameters
    # ********************
    @property
    def threshold(self):
        return int(self.config["Detection"]["Threshold"])
    
    @property
    def contourArea(self):
        return int(self.config["Detection"]["ContourArea"])

    # ********************
    #  [Debug] Debug details
    # ********************
    @property
    def debugMode(self):
        #arg = self.args.get("debug")
        #if arg != None: return arg

        return self.config["Debug"].getboolean("Enable", False)

    @property
    def logFile(self):
        loc = self.config["Debug"].get("LogFile", None)
        if loc is None: return None

        return f"{os.path.dirname(os.path.realpath(__file__))}/{loc}"

    @property
    def noCaptureMode(self):
        arg = self.args.get("no-capture")
        if arg != None: return arg

        return self.config["Debug"].getboolean("NoCapture", False)