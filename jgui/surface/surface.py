import cairo
import math
from .structures import Size, Position, Rectangle
from ..events.events import WindowEventSource

class Surface(object):
    def __init__(self, size=None):
        self.size = Size.from_value(size)
        self.csurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.size.width, self.size.height)
        self.root_window = Window('root', Position(0,0), self.size)
        self.windows = [self.root_window]

    def draw(self):
        for window in self.windows:
            window.draw(self.csurface)

surface = None
def init(size):
    surface = Surface(size)

class WindowSurface(object):
    def __init__(self):
        super(WindowSurface, self).__init__()
        #self.mouse_pos

    def draw(self, surface):
        Width = self.size.width
        Height = self.size.height
        x,y, radius = (Width/2,Height/2, Width/2-Width/10)
        ctx = cairo.Context(surface)
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.rectangle(0.0, 0.0, Width, Height)
        ctx.fill()

        ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.set_line_width(Width/10)
        ctx.arc(x, y, radius, 0, 2.0 * math.pi)
        ctx.set_source_rgba(0.8, 0.8, 0.8)
        ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1)
        ctx.stroke()


class Window(WindowEventSource, WindowSurface):
    def __init__(self, name, position=None, size=None):
        super(Window, self).__init__()
        self.name = name
        self.rectangle = Rectangle(position, size)
        self.children = []
        self.parent = None
        self.mouse_pos = Position()


    def add_child(self, child_window):
        if child_window not in self.children:
            child_window.parent = self
            self.children.append(child_window)

    def remove_child(self, child_window):
        try:
            self.children.remove(child_window)
            child_window.parent = None
        except ValueError:
            pass

    @property
    def position(self):
        return self.rectangle.position

    @position.setter
    def position(self, position):
        diff = position - self.rectangle.position
        if diff.x != 0 or diff.y != 0:
            self.dispatch('move', self, position)
            for child in self.children:
                child.position = child.position + diff
        self.recangle.position = position

    @property
    def size(self):
        return self.rectangle.size

    @size.setter
    def size(self, size):
        diff = size - self.rectangle.size
        if diff.height != 0 or diff.width != 0:
            self.dispatch('resize', self, size)
            for child in self.children:
                child.size = child.size + diff
        self.rectangle.size = size

