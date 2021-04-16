import logging
from time import time

class PictureLogger:
    def __init__(self, file_source):
        self._loggedPictures = []
        #self.__read_picture_history(file_source)

        self._log_file = open(file_source, mode="a", encoding="utf-8")

    def __del__(self):
        self._log_file.close()

    def log_picture(self, fullPath, thumbPath, classification, shutter, iso):
        entry = {
            "full": fullPath,
            "thumb": thumbPath,
            "evaluation": [dictify_classification(c) for c in classification],
            "time": time(),
            "shutter": shutter,
            "iso": iso
        }

        self.__append_to_file(entry)

    def __read_picture_history(self, file_source):
        f = open(file_source, mode="r", encoding="utf-8")
        for line in f:
            self._loggedPictures.append(self.__deserialize_entry(line))

    def __append_to_file(self, entry):
        self._loggedPictures.append(entry)
        self._log_file.write(self.__serialize_entry(entry))
        self._log_file.write("\n")
        self._log_file.flush()

    def __serialize_entry(self, entry):
        c = self.__serialize_classification(entry["evaluation"])
        return f"{entry['time']}|{entry['full']}|{entry['thumb']}|{c}|{entry['shutter']}|{entry['iso']}"

    def __deserialize_entry(self, string):
        split = string.split("|")
        return {
            "time": split[0],
            "full": split[1],
            "thumb": split[2],
            "evaluation": self.__deserialize_classification(split[3]),
            "shutter": split[4],
            "iso": split[5]
        }

    def __serialize_classification(self, results):
        strings = [stringify_result(r) for r in results]
        return "@".join(strings)

    def __deserialize_classification(self, string):
        split = string.split("@")
        return [destringify_result(s) for s in split]

def dictify_classification(classification):
    return {
        "label": classification.label,
        "confidence": classification.confidence
    }

def stringify_result(result):
    return f"{result['label']}~{result['confidence']}"

def destringify_result(result):
    split = result.split("~")
    return {
        "label": split[0],
        "confidence": split[1]
    }