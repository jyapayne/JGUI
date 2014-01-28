
class Event(object):
    def __init__(self, name='event', data=None):
        self.name = name
        self.data = data

class EventSource(object):
    types = [] # list of event names

    def __init__(self):
        super(EventSource, self).__init__()
        self.events = {}
        for type in self.types:
            self.events[type] = []

    def accept(self, event, callback):
        if event in self.events:
            if callback not in self.events[event]:
                self.events[event].append(callback)

    def dispatch(self, event, *args, **kwargs):
        for callback in self.events[event]:
            callback(*args, **kwargs)

    def reject(self, event, callback):
        if event in self.events:
            if callback in self.events[event]:
                self.events[event].remove(callback)

class WindowEventSource(EventSource):
    types = ['mouse-enter', 'mouse-leave',
             'resize', 'move',
             'key-repeat', 'key-down', 'key-up',
             'mouse-right-down', 'mouse-right-up',
             'mouse-left-down', 'mouse-left-up',
             'mouse-middle-down', 'mouse-middle-up',
             'scroll-up', 'scroll-down', 'drag']
