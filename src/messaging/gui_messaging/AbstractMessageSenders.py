import constants as c


class MessageDown(object):
    def __init__(self):
        pass

    def sendEventToChildren(self, function):
        raise NotImplementedError("sendEventToChildren not implemented!")


class Leaf(MessageDown):
    def __init__(self):
        MessageDown.__init__(self)

    def sendEventToChildren(self, function):
        function(self)


class NonLeaf(MessageDown):
    def __init__(self, widgets_list):
        MessageDown.__init__(self)
        self.widgets_list = widgets_list

    def sendEventToChildren(self, function):
        message = function(self)
        if not message == c.STOP_EVENT_SENDING:
            for widget in self.widgets_list:
                widget.sendEventToChildren(function)


class MessageUp(object):
    def __init__(self):
        pass

    def sendEventToRoot(self, function, needs_stopped_state=False):
        raise NotImplementedError("sendEventToRoot not implemented!")


class NonRoot(MessageUp):
    def __init__(self, parent):
        MessageUp.__init__(self)
        self.parent = parent

    def sendEventToRoot(self, function, needs_stopped_state=False):
        self.parent.sendEventToRoot(function, needs_stopped_state)

    def sendEventToAll(self, function, needs_stopped_state=False):
        self.parent.sendEventToAll(function, needs_stopped_state)


class Root(MessageUp, NonLeaf):
    def __init__(self, widgets_list, post_office_message_handler):
        MessageUp.__init__(self)
        NonLeaf.__init__(self, widgets_list)
        self.post_office_message_handler = post_office_message_handler

    def bciIsStopped(self):
        return self.post_office_message_handler.isStopped()

    def checkIfStopped(self, function, needs_stopped_state):
        if needs_stopped_state and self.bciIsStopped() or not needs_stopped_state:
            function()
        else:
            print "BCI has to be stopped to use this functionality!"

    def sendEventToRoot(self, function, needs_stopped_state=False):
        self.checkIfStopped(lambda: function(self), needs_stopped_state)

    def sendEventToAll(self, function, needs_stopped_state=False):
        self.checkIfStopped(lambda: self.sendEventToChildren(function), needs_stopped_state)


class Widget(NonRoot, Leaf):
    def __init__(self, parent):
        NonRoot.__init__(self, parent)
        Leaf.__init__(self)


class Frame(NonRoot, NonLeaf):
    def __init__(self, parent, widgets_list):
        NonRoot.__init__(self, parent)
        NonLeaf.__init__(self, widgets_list)
