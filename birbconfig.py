import configparser

class BirbConfig:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')