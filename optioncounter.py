class OptionCounter:
    def __init__(self, min, max, increment, start = None):
        self.min = min
        self.max = max
        self.increment = increment
        
        if start == None:
            self.current = min
        else:
            self.current = start

    @property
    def value(self):
        return self.current

    @property
    def label(self):
        return f"{self.current}"

    def next(self):
        i = self.current + self.increment

        if i > self.max:
            i = self.max

        self.current = i
        return i

    def previous(self):
        i = self.current - self.increment

        if i < self.min:
            i = self.min

        self.current = i
        return i