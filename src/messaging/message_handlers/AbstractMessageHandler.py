

class MessageHandler(object):
    def __init__(self, possible_messages):
        self.possible_messages = possible_messages

    def canHandle(self, message):
        return message in self.possible_messages

    def handle(self, message):
        raise NotImplementedError("handle not implemented!")