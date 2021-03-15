import configparser
from argparse import ArgumentParser

class BirbConfig:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        self.ap = ArgumentParser()
        self.ap.add_argument("-f", "--file", default=None, help="path to the log file")
        self.ap.add_argument("-d", "--debug", help="debug mode", default=None)
        self.ap.add_argument("-n", "--no-capture", help="do not capture photos", default=None)
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
        return self.__clean_string(self.config["Saving"]["Directory"].strip("'"))

    # ********************
    #  [Debug] Debug details
    # ********************
    @property
    def debugMode(self):
        return self.config["Debug"].getboolean("Enable", False)

    @property
    def logFile(self):
        return self.__clean_string(self.config["Debug"].get("LogFile", None))

    @property
    def noCaptureMode(self):
        return self.config["Debug"].getboolean("NoCapture", False)