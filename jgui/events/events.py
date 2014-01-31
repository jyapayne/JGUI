
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
    mouse_events = ['mouse-enter', 'mouse-leave', 'drag', 'mouse-move', 'hover']
    mouse_wheel_events = ['scroll-up', 'scroll-down']
    mouse_button_down_events = ['mouse-right', 'mouse-left', 'mouse-middle']
    mouse_button_drag_events = ['mouse-right-drag', 'mouse-left-drag', 'mouse-middle-drag']
    mouse_button_up_events = ['mouse-right-up', 'mouse-left-up',
                              'mouse-middle-up']
    mouse_button_events = mouse_button_down_events + mouse_button_up_events + mouse_button_drag_events
    window_events = ['resize', 'move', 'focus', 'focus-lost']
    key_events = ['key-down', 'key-up', 'key-repeat']
    types = mouse_events + mouse_wheel_events + mouse_button_events +\
            window_events + key_events
