import Switchable


class Standby(Switchable.Switchable):
    def __init__(self):
        Switchable.Switchable.__init__(self)
        self.in_standby_state = False
        self.standby_freq = None

    def setup(self, standby_freq):
        self.in_standby_state = False
        if self.enabled:
            self.standby_freq = standby_freq

    def notInStandby(self):
        return not self.in_standby_state or not self.enabled

    def choseStandbyFreq(self, chosen_freq):
        return chosen_freq == self.standby_freq

    def switchStandby(self):
        self.in_standby_state = not self.in_standby_state
