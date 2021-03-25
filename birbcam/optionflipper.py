class OptionFlipper:
    def __init__(self, options, start = 0, labels = None):
        self.options = options
        self.index = start
        self.labels = labels

    @property
    def value(self):
        return self.options[self.index]

    @property
    def label(self):
        if self.labels == None:
            return f"{self.value}"
        else:
            return self.labels[self.index]

    @property 
    def is_at_start(self):
        return self.index == 0

    @property 
    def is_at_end(self):
        return self.index == len(self.options) - 1

    def next(self):
        return self.__flip(1)

    def previous(self):
        return self.__flip(-1)

    def __flip(self, delta):
        try:
            self.index += delta

            if self.index >= len(self.options):
                self.index = 0

            if self.index < 0:
                self.index = len(self.options) - 1
        except ValueError:
            self.index = 0

        return self.options[self.index]