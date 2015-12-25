

class Standby(object):
    def __init__(self):
        self.enabled = False
        self.in_standby_state = False
        self.standby_freq = None

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def setup(self, standby_freq):
        self.in_standby_state = False
        if self.enabled:
            self.standby_freq = standby_freq

    def notInStandby(self):
        return not self.in_standby_state or not self.enabled
