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
        self.root_window.add_child(Window('child', Position(0,0), [500,200], self.context, draggable=True))
        self.windows = [self.root_window]

    def setTopZero(self, context):
        context.identity_matrix()
        matrix = cairo.Matrix(1, 0, 0,
                              1, 0, 0)
        context.transform(matrix)

    def inject_mouse_position(self, pos):
        self.root_window.inject_mouse_position(pos)

    def inject_mouse_down(self, button):
        self.root_window.inject_mouse_down(button)

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
        self.draw_rounded_rect([0,0], [self.size.width, self.size.height], outline_width=self.size.width/70)

    def draw(self):
        if self.visible:
            self.context.save()
            self.process_inputs()
            self.render()
            for child in self.children:
                child.draw()
            self.context.restore()


class Window(WindowEventSource, WindowSurface):
    def __init__(self, name, position=None, size=None, context=None, draggable=False):
        super(Window, self).__init__()
        self.context = context
        self.name = name
        self.rectangle = Rectangle(position, size)
        self.children = []
        self.parent = None
        self.mouse_pos = Position(-1, -1)
        self.mouse_diff = Position(0, 0)
        self.mouse_in = False
        self.mouse_hover = False
        self.mouse_down = False
        self.old_mouse_down = False
        self.mouse_inputs = dict.fromkeys(self.mouse_button_down_events, False)
        self.focused = False
        self.visible = True
        self.draggable = draggable

        if self.draggable:
            self.accept('mouse-left-drag', self.drag)
            self.accept('mouse-left', self.click)
            self.accept('mouse-left-up', self.click_up)

    def drag(self, obj, mouse_pos):
        obj.position = mouse_pos - self.mouse_diff

    def click(self, obj, mouse_pos):
        self.mouse_diff = mouse_pos - self.position

    def click_up(self, obj, mouse_pos):
        self.mouse_diff = Position(0, 0)

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def inject_mouse_down(self, button):
        if self.mouse_inside():
            print button, self.name
            self.mouse_inputs[button] = True
            self.mouse_down = True
            self.grab_focus()
            self.dispatch(button, self, self.mouse_pos)
        else:
            self.release_focus()
        for child in self.children:
            child.inject_mouse_down(button)

    def inject_mouse_up(self, button):
        if self.mouse_inside() and self.mouse_inputs[button]:
            print button+'-up', self.name
            self.mouse_down = False
            self.mouse_inputs[button] = False
            self.dispatch('{}-up'.format(button), self, self.mouse_pos)
        for child in self.children:
            child.inject_mouse_up(button)

    def inject_mouse_position(self, pos):
        mouse_pos = Position.from_value(pos)
        diff = mouse_pos - self.mouse_pos
        if diff != Position(0,0):
            self.dispatch('mouse-move', self, self.mouse_pos, mouse_pos)
            if self.focused and self.mouse_down:
                for button, down in self.mouse_inputs.items():
                    if down:
                        self.dispatch('{}-drag'.format(button), self, self.mouse_pos)
        self.mouse_pos = mouse_pos
        for child in self.children:
            child.inject_mouse_position(pos)

    def grab_focus(self):
        self.focused = True

    def release_focus(self):
        if self.focused:
            print 'released', self.name
            self.focused = False
            self.mouse_down = False
            #clear events that may have been triggered
            #eg. User clicks on one window, holds, and
            #then releases on another
            for key in self.mouse_inputs:
                self.mouse_inputs[key] = False


    def mouse_inside(self):
        res = self.rectangle.intersects_with(self.mouse_pos)
        for child in self.children:
            res &= not child.mouse_inside()
        return res

    def mouse_held(self):
        res = self.mouse_down
        for child in self.children:
            res |= child.mouse_down
        return res

    def process_inputs(self):
        mouse_focus = self.mouse_inside()
        if not self.mouse_held():
            if mouse_focus:
                if not self.mouse_in:
                    print 'mouse-enter', self.name
                    self.dispatch('mouse-enter', self)
                self.mouse_in = True
            else:
                if self.mouse_in:
                    print 'mouse-leave', self.name
                    self.dispatch('mouse-leave', self)
                self.mouse_in = False

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

