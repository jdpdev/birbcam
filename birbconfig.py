import configparser

class BirbConfig:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    @property
    def saveTo(self):
        return self.config["SaveDirectory"]