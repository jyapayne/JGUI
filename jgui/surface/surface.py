import cairo
import math
from .structures import Size, Position, Rectangle
from ..events.events import WindowEventSource

class Surface(object):
    def __init__(self, size=None, context=None):
        self.size = Size.from_value(size)
        if context is None:
            self.csurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.size.width, self.size.height)
            self.context = cairo.Context(self.csurface)
        else:
            self.context = context
        self.root_window = Window('root', Position(0,0), self.size, self.context)
        self.root_window.add_child(Window('child', Position(0,0), [500,200], self.context))
        self.windows = [self.root_window]

    def setTopZero(self, context):
        context.identity_matrix()
        matrix = cairo.Matrix(1, 0, 0,
                              1, 0, 0)
        context.transform(matrix)

    def draw(self):
        #self.setTopZero(ctx)
        self.context.identity_matrix()
        self.context.set_operator(cairo.OPERATOR_CLEAR)
        self.context.rectangle(0.0, 0.0, self.size.width, self.size.height)
        self.context.fill()
        self.context.set_operator(cairo.OPERATOR_OVER)
        for window in self.windows:
            window.draw()

class WindowSurface(object):
    def __init__(self):
        super(WindowSurface, self).__init__()
        #self.mouse_pos


    def draw_circle(self, position, size, color=(1,1,1), outline_width=1.0, outline_color=(0,0,0), start_angle=0.0, end_angle=360.0):
        context = self.context
        position = Position.from_value(position)
        size = Size.from_value(size)
        width = size.width
        height = size.height

        x,y = (self.position.x+position.x+width/2,
               self.position.y+position.y+height/2)

        context.set_line_width(outline_width)

        context.save()
        context.translate(x, y)
        context.scale(width/2.0-outline_width/2.0, height/2.0-outline_width/2.0)
        context.arc(0, 0, 1, start_angle, end_angle * math.pi/180.0)
        context.restore()

        context.set_source_rgba(*color)
        context.fill_preserve()
        context.set_source_rgba(*outline_color)
        context.stroke()

    def draw_rounded_rect(self, position, size, color=(1,1,1), outline_width=1, outline_color=(0,0,0), corner_radius=10):
        position = Position.from_value(position)
        size = Size.from_value(size)

        context = self.context
        radius = corner_radius
        degrees = math.pi / 180.0
        x = position.x + self.position.x
        y = position.y + self.position.y
        width = size.width
        height = size.height

        context.new_sub_path()
        context.arc(x + width - radius - outline_width/2.0, y + radius + outline_width/2.0, radius, -90 * degrees, 0 * degrees)
        context.arc(x + width - radius - outline_width/2.0, y + height - radius - outline_width/2.0, radius, 0 * degrees, 90 * degrees)
        context.arc(x + radius + outline_width/2.0, y + height - radius - outline_width/2.0, radius, 90 * degrees, 180 * degrees)
        context.arc(x + radius + outline_width/2.0, y + radius + outline_width/2.0, radius, 180 * degrees, 270 * degrees)
        context.close_path()

        context.set_source_rgb(*color)
        context.fill_preserve()
        context.set_source_rgba(*outline_color)
        context.set_line_width(outline_width)
        context.stroke()

    def render(self):
        self.draw_rounded_rect([0,0], [self.size.width, self.size.height], outline_width=self.size.width/50)

    def draw(self):
        self.context.save()
        self.process_inputs()
        self.render()
        for child in self.children:
            child.draw()
        self.context.restore()


class Window(WindowEventSource, WindowSurface):
    def __init__(self, name, position=None, size=None, context=None):
        super(Window, self).__init__()
        self.context = context
        self.name = name
        self.rectangle = Rectangle(position, size)
        self.children = []
        self.parent = None
        self.mouse_pos = Position(-1, -1)
        self.mouse_in = False
        self.mouse_hover = False
        self.mouse_down = False
        self.old_mouse_down = False

    def injectMouseDown(self, button):
        self.mouse_down = True

    def injectMouseUp(self, button):
        self.mouse_down = False

    def injectMousePosition(self, pos):
        self.mouse_pos = Position.from_value(pos)
        for child in self.children:
            child.injectMousePosition(pos)

    def has_mouse_focus(self):
        res = self.rectangle.intersects_with(self.mouse_pos)
        for child in self.children:
            res &= not child.has_mouse_focus()
        return res

    def process_inputs(self):
        mouse_focus = self.has_mouse_focus()
        if mouse_focus:
            if not self.mouse_in:
                print 'mouse-enter'
                self.dispatch('mouse-enter', self)
            self.mouse_in = True
        else:
            if self.mouse_in:
                print 'mouse-leave'
                self.dispatch('mouse-leave', self)
            self.mouse_in = False

        if self.mouse_in and self.mouse_down and not self.old_mouse_down:
            print 'mousedown'
            self.dispatch('mouse-left', self, self.mouse_pos)
            self.old_mouse_down = True
        elif self.mouse_in and not self.mouse_down and self.old_mouse_down:
            print 'mouseup'
            self.dispatch('mouse-left-up', self, self.mouse_pos)
            self.old_mouse_down = False


    def add_child(self, child_window):
        if child_window not in self.children:
            child_window.parent = self
            child_window.position = child_window.position + self.position
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
        self.rectangle.position = position

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

