import cairo
import math
from .structures import Size, Position, Rectangle, Color
from ..events.events import WindowEventSource

debug = True

class Surface(object):
    def __init__(self, size=None, context=None, render_mouse=True):
        self.size = Size.from_value(size)
        if context is None:
            self.csurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.size.width, self.size.height)
            self.context = cairo.Context(self.csurface)
        else:
            self.context = context
        self.root_window = Window('root', Position(0,0), self.size, self.context)
        self.render_mouse = render_mouse
        if self.render_mouse:
            self.mouse_icon = Mouse('mouse', Position(0, 0), Size(12,20), self.context)
        self.windows = [self.root_window, self.mouse_icon]

    def setTopZero(self, context):
        context.identity_matrix()
        matrix = cairo.Matrix(1, 0, 0,
                              1, 0, 0)
        context.transform(matrix)

    def inject_mouse_position(self, pos):
        if self.render_mouse:
            self.mouse_icon.position = pos
        self.root_window.inject_mouse_position(pos)

    def inject_mouse_down(self, button):
        self.root_window.inject_mouse_down(button)

    def inject_mouse_up(self, button):
        self.root_window.inject_mouse_up(button)

    def notify_window_resize(self, width, height):
        self.size = Size(width, height)
        self.root_window.size = self.size
        self.csurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.size.width, self.size.height)
        self.context = cairo.Context(self.csurface)

        stack = self.windows[:]
        while stack:
            item = stack.pop()
            item.context = self.context
            if item.children:
                stack.extend(item.children)

    def draw(self):
        #self.setTopZero(ctx)
        #self.context.identity_matrix()
        self.context.set_operator(cairo.OPERATOR_CLEAR)
        self.context.rectangle(0.0, 0.0, self.size.width, self.size.height)
        self.context.fill()
        self.context.set_operator(cairo.OPERATOR_OVER)
        for window in self.windows:
            window.draw()

class TestSurface(Surface):
    def __init__(self, *args, **kwargs):
        super(TestSurface, self).__init__(*args, **kwargs)
        self.root_window.add_child(MyWindow('child', Position(0,0), [500,200], self.context, draggable=True, resizable=True, min_size=Size(40,40)))
        self.root_window.add_child(TestWindow('child2', Position(200,200), [200,200], self.context, draggable=True))
        child3 = TestWindow('child3', Position(300,300), [200,200], self.context, draggable=True)
        child3.add_child(TestWindow('child3-1', Position(10,10), [50,50], self.context, draggable=True))
        self.root_window.add_child(child3)

class WindowSurface(object):

    line_joins = {'miter': cairo.LINE_JOIN_MITER,
                  'round': cairo.LINE_JOIN_ROUND,
                  'bevel': cairo.LINE_JOIN_BEVEL}

    line_caps = {'round': cairo.LINE_CAP_ROUND,
                 'butt': cairo.LINE_CAP_BUTT,
                 'square': cairo.LINE_CAP_SQUARE}

    def __init__(self):
        super(WindowSurface, self).__init__()


    def draw_circle(self, position, size, color=(1,1,1), line_width=1.0, line_color=(0,0,0), start_angle=0.0, end_angle=360.0):
        color = Color.from_value(color)
        line_color = Color.from_value(line_color)
        context = self.context
        position = Position.from_value(position)
        size = Size.from_value(size)
        width = size.width
        height = size.height

        x,y = (self.position.x+position.x+width/2,
               self.position.y+position.y+height/2)

        context.set_line_width(line_width)

        context.save()
        context.translate(x, y)
        context.scale(width/2.0-line_width/2.0, height/2.0-line_width/2.0)
        context.arc(0, 0, 1, start_angle, end_angle * math.pi/180.0)
        context.restore()

        context.set_source_rgba(*color)
        context.fill_preserve()
        context.set_source_rgba(*line_color)
        context.stroke()

    def draw_lines(self, lines, line_color=(0,0,0,1), fill_color=(1,1,1,1), line_width=1, line_join='miter', line_cap='butt'):
        if lines:
            context = self.context
            start_pos = self.position + lines[0]
            context.set_line_width(line_width)
            context.move_to(int(start_pos.x), int(start_pos.y))
            for line in lines[1:]:
                next_pos = self.position+line
                context.line_to(next_pos.x, next_pos.y)
            context.close_path()
            try:
                context.set_line_cap(self.line_joins[line_join])
            except KeyError:
                pass
            try:
                context.set_line_join(self.line_caps[line_cap])
            except KeyError:
                pass
            context.set_source_rgba(*fill_color)
            context.fill_preserve()
            context.set_source_rgba(*line_color)
            context.stroke()


    def draw_rounded_rect(self, position, size, color=(1,1,1), line_width=1, line_color=(0,0,0), corner_radius=0, line_dashed=False, clip=False):
        position = Position.from_value(position)
        size = Size.from_value(size)
        color = Color.from_value(color)
        line_color = Color.from_value(line_color)

        context = self.context
        radius = corner_radius
        degrees = math.pi / 180.0
        x = position.x + self.position.x
        y = position.y + self.position.y
        width = size.width
        height = size.height

        if clip: #clips the entire region so any child windows will be confined to the parent
            context.arc(x + width - radius, y + radius, radius, -90 * degrees, 0 * degrees)
            context.arc(x + width - radius, y + height - radius, radius, 0 * degrees, 90 * degrees)
            context.arc(x + radius, y + height - radius, radius, 90 * degrees, 180 * degrees)
            context.arc(x + radius, y + radius, radius, 180 * degrees, 270 * degrees)
            context.close_path()
            context.clip()

        context.new_path()
        context.arc(x + width - radius - line_width/2.0, y + radius + line_width/2.0, radius, -90 * degrees, 0 * degrees)
        context.arc(x + width - radius - line_width/2.0, y + height - radius - line_width/2.0, radius, 0 * degrees, 90 * degrees)
        context.arc(x + radius + line_width/2.0, y + height - radius - line_width/2.0, radius, 90 * degrees, 180 * degrees)
        context.arc(x + radius + line_width/2.0, y + radius + line_width/2.0, radius, 180 * degrees, 270 * degrees)
        context.close_path()

        context.set_source_rgba(*color)
        context.fill_preserve()
        context.set_source_rgba(*line_color)
        context.set_line_width(line_width)
        context.save()
        if line_dashed:
            context.set_dash([line_width, line_width])
        context.stroke()
        context.restore()

    def render(self):
        if debug:
            self.draw_rounded_rect([0,0], [self.size.width, self.size.height], color=(0,0,1,0.1), line_color=(0,0,1,0.4), line_width=1.5, corner_radius=2, line_dashed=True)

    def draw(self):
        if self.visible:
            self.context.save()
            self.render()
            for child in self.children:
                child.draw()
            self.context.restore()


class Window(WindowEventSource, WindowSurface):
    def __init__(self, name, position=None, size=None, context=None, draggable=False, resizable=False, **kwargs):
        super(Window, self).__init__()
        self.context = context
        self.name = name
        self.rectangle = Rectangle(position, size)
        self.children = []
        self.min_size = kwargs.get('min_size', Size(1,1))
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
        self._resizable = resizable
        self.resizable = resizable
        self.accept('mouse-move', self.process_mouse_move)

        for key, value in kwargs.items():
            setattr(self, key, value)

        if self.draggable:
            self.accept('mouse-left-drag', self.drag)
            self.accept('mouse-left', self.click)
            self.accept('mouse-left-up', self.click_up)

    @property
    def resizable(self):
        return self._resizable

    @resizable.setter
    def resizable(self, value):
        self._resizable = value
        if self._resizable:
            self.init_resize_handles()

    def drag_handle(self, obj, mouse_pos):
        pass

    def drag_bottomright_handle(self, obj, mouse_pos):
        diff = mouse_pos - self.mouse_diff
        old_size = Size.from_value(self.size)
        self.size = self.size + diff
        self.mouse_diff.y = obj.position.y + self.handle_diff.y
        self.mouse_diff.x = obj.position.x + self.handle_diff.x

    def drag_bottomleft_handle(self, obj, mouse_pos):
        diff = mouse_pos - self.mouse_diff
        old_size = Size.from_value(self.size)
        new_pos = Position(self.position.x+diff.x, self.position.y)
        new_size = Size(self.size.width - diff.x, self.size.height + diff.y)
        if new_size.width <= self.min_size.width:
            new_pos.x = self.position.x + self.size.width - self.min_size.width
            new_size.width = self.min_size.width
        self.position = new_pos
        self.size = new_size

        self.mouse_diff.y = obj.position.y + self.handle_diff.y
        self.mouse_diff.x = obj.position.x + self.handle_diff.x

    def drag_topright_handle(self, obj, mouse_pos):
        diff = mouse_pos - self.mouse_diff
        old_size = Size.from_value(self.size)
        new_pos = Position(self.position.x, self.position.y + diff.y)
        new_size = Size(self.size.width + diff.x, self.size.height - diff.y)
        if new_size.height <= self.min_size.height:
            new_pos.y = self.position.y + self.size.height - self.min_size.height
            new_size.height = self.min_size.height

        self.position = new_pos
        self.size = new_size

        self.mouse_diff.y = obj.position.y + self.handle_diff.y
        self.mouse_diff.x = obj.position.x + self.handle_diff.x

    def drag_topleft_handle(self, obj, mouse_pos):
        diff = mouse_pos - self.mouse_diff
        old_size = Size.from_value(self.size)
        new_pos = Position(self.position.x + diff.x, self.position.y + diff.y)
        new_size = Size(self.size.width - diff.x, self.size.height - diff.y)
        if new_size.height <= self.min_size.height:
            new_pos.y = self.position.y + self.size.height - self.min_size.height
            new_size.height = self.min_size.height
        if new_size.width <= self.min_size.width:
            new_pos.x = self.position.x + self.size.width - self.min_size.width
            new_size.width = self.min_size.width

        self.position = new_pos
        self.size = new_size

        self.mouse_diff.y = obj.position.y + self.handle_diff.y
        self.mouse_diff.x = obj.position.x + self.handle_diff.x

    def drag_top_handle(self, obj, mouse_pos):
        diff = mouse_pos - self.mouse_diff
        old_size = Size.from_value(self.size)
        new_pos = Position(self.position.x, self.position.y + diff.y)
        new_size = Size(self.size.width, self.size.height - diff.y)
        if new_size.height <= self.min_size.height:
            new_pos.y = self.position.y + self.size.height - self.min_size.height
            new_size.height = self.min_size.height
        self.position = new_pos
        self.size = new_size

        self.mouse_diff.y = obj.position.y + self.handle_diff.y
        self.mouse_diff.x = obj.position.x + self.handle_diff.x

    def drag_left_handle(self, obj, mouse_pos):
        diff = mouse_pos - self.mouse_diff
        old_size = Size.from_value(self.size)
        new_pos = Position(self.position.x+diff.x, self.position.y)
        new_size = Size(self.size.width - diff.x, self.size.height)
        if new_size.width <= self.min_size.width:
            new_pos.x = self.position.x + self.size.width - self.min_size.width
            new_size.width = self.min_size.width
        self.position = new_pos
        self.size = new_size

        self.mouse_diff.x = obj.position.x + self.handle_diff.x

    def drag_bottom_handle(self, obj, mouse_pos):
        diff = mouse_pos - self.mouse_diff
        old_height = self.size.height
        self.size = Size(self.size.width, self.size.height+diff.y)

        self.mouse_diff.y = obj.position.y + self.handle_diff.y

    def drag_right_handle(self, obj, mouse_pos):
        diff = mouse_pos - self.mouse_diff
        old_width = self.size.width
        self.size = Size(self.size.width + diff.x, self.size.height)

        self.mouse_diff.x = obj.position.x + self.handle_diff.x

    def init_resize_handles(self):
        self.corner_handle_size = Size(20, 20)
        self.edge_buffer = Size(10, 10)
        self.edge_handle_width = 10
        self.handle_diff = Position(0,0)

        self.top_handle = Window('top_handle')
        self.top_handle.accept('drag', self.drag_top_handle)
        self.top_handle.accept('mouse-left', self.handle_click)
        self.top_handle.accept('mouse-left-up', self.handle_click_up)

        self.topleft_handle = Window('topleft_handle')
        self.topleft_handle.accept('drag', self.drag_topleft_handle)
        self.topleft_handle.accept('mouse-left', self.handle_click)
        self.topleft_handle.accept('mouse-left-up', self.handle_click_up)

        self.topright_handle = Window('topright_handle')
        self.topright_handle.accept('drag', self.drag_topright_handle)
        self.topright_handle.accept('mouse-left', self.handle_click)
        self.topright_handle.accept('mouse-left-up', self.handle_click_up)

        self.right_handle = Window('right_handle')
        self.right_handle.accept('drag', self.drag_right_handle)
        self.right_handle.accept('mouse-left', self.handle_click)
        self.right_handle.accept('mouse-left-up', self.handle_click_up)

        self.bottomright_handle = Window('bottomright_handle')
        self.bottomright_handle.accept('drag', self.drag_bottomright_handle)
        self.bottomright_handle.accept('mouse-left', self.handle_click)
        self.bottomright_handle.accept('mouse-left-up', self.handle_click_up)

        self.bottom_handle = Window('bottom_handle')
        self.bottom_handle.accept('drag', self.drag_bottom_handle)
        self.bottom_handle.accept('mouse-left', self.handle_click)
        self.bottom_handle.accept('mouse-left-up', self.handle_click_up)

        self.bottomleft_handle = Window('bottomleft_handle')
        self.bottomleft_handle.accept('drag', self.drag_bottomleft_handle)
        self.bottomleft_handle.accept('mouse-left', self.handle_click)
        self.bottomleft_handle.accept('mouse-left-up', self.handle_click_up)

        self.left_handle = Window('left_handle')
        self.left_handle.accept('drag', self.drag_left_handle)
        self.left_handle.accept('mouse-left', self.handle_click)
        self.left_handle.accept('mouse-left-up', self.handle_click_up)


        self.vertical_edge_size = Size()
        self.horizontal_edge_size = Size()

        self.update_resize_handles()
        self.add_child(self.top_handle)
        self.add_child(self.topleft_handle)
        self.add_child(self.topright_handle)
        self.add_child(self.left_handle)
        self.add_child(self.right_handle)
        self.add_child(self.bottom_handle)
        self.add_child(self.bottomright_handle)
        self.add_child(self.bottomleft_handle)

    def update_resize_handles(self):
        buffer = self.edge_buffer
        top = self.top_handle
        topleft = self.topleft_handle
        topright = self.topright_handle
        right = self.right_handle
        bottomright = self.bottomright_handle
        bottom = self.bottom_handle
        bottomleft = self.bottomleft_handle
        left = self.left_handle
        vertical_edge_size = self.vertical_edge_size
        horizontal_edge_size = self.horizontal_edge_size
        corner_handle_size = self.corner_handle_size
        x, y = self.position.x, self.position.y

        vertical_edge_size.width = self.size.width-2*corner_handle_size.width
        vertical_edge_size.height = self.edge_handle_width

        horizontal_edge_size.width = self.edge_handle_width
        horizontal_edge_size.height = self.size.height-2*corner_handle_size.height

        top.position.x = x + corner_handle_size.width
        top.position.y = y
        top.size = vertical_edge_size

        topleft.position.x = x
        topleft.position.y = y
        topleft.size = corner_handle_size

        topright.position.x = x + self.size.width-corner_handle_size.width
        topright.position.y = y
        topright.size = corner_handle_size

        bottom.position.x = x + corner_handle_size.width
        bottom.position.y = y + self.size.height-vertical_edge_size.height
        bottom.size = vertical_edge_size

        bottomleft.position.x = x
        bottomleft.position.y = y + self.size.height-corner_handle_size.height
        bottomleft.size = corner_handle_size

        bottomright.position.x = x + self.size.width-corner_handle_size.width
        bottomright.position.y = y + self.size.height-corner_handle_size.height
        bottomright.size = corner_handle_size

        right.position.x = x + self.size.width-horizontal_edge_size.width
        right.position.y = y + corner_handle_size.height
        right.size = horizontal_edge_size

        left.position.x = x
        left.position.y = y + corner_handle_size.height
        left.size = horizontal_edge_size

    def drag(self, obj, mouse_pos):
        obj.position = mouse_pos - self.mouse_diff

    def click(self, obj, mouse_pos):
        self.mouse_diff = mouse_pos - obj.position

    def click_up(self, obj, mouse_pos):
        self.mouse_diff = Position(0, 0)

    def handle_click_up(self, obj, mouse_pos):
        self.mouse_diff = Position(0, 0)
        self.handle_diff = Position(0, 0)
        self.dispatch('resize-end', self)

    def handle_click(self, obj, mouse_pos):
        self.mouse_diff = mouse_pos
        self.handle_diff = mouse_pos - obj.position
        self.dispatch('resize-start', self)

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
        if self.mouse_held() and self.mouse_inputs[button]:
            print button+'-up', self.name
            self.mouse_down = False
            self.mouse_inputs[button] = False
            self.dispatch('{}-up'.format(button), self, self.mouse_pos)
        for child in self.children:
            child.inject_mouse_up(button)

    def inject_mouse_position(self, pos):
        mouse_pos = Position.from_value(pos)
        diff = mouse_pos - self.mouse_pos
        old_pos = self.mouse_pos
        self.mouse_pos = mouse_pos
        if diff != Position(0,0):
            self.dispatch('mouse-move', self, old_pos, self.mouse_pos)
            if self.focused and self.mouse_down:
                for button, down in self.mouse_inputs.items():
                    if down:
                        self.dispatch('{}-drag'.format(button), self, self.mouse_pos)
                        self.dispatch('drag', self, self.mouse_pos)
        for child in self.children:
            child.inject_mouse_position(pos)

    def inject_mouse_wheel(self, value):
        self.dispatch('scroll', self, value)

    def grab_focus(self):
        self.focused = True
        if self.parent is not None:
            children = self.parent.children[:]
            children.remove(self)
            children.append(self)

            self.parent.children = children
            parent = self.parent

            while parent is not None:
                parent.grab_focus()
                parent = parent.parent

        self.dispatch('focus', self)

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
            self.dispatch('focus-lost', self)

    def get_root(self):
        parent = self.parent
        if parent is None:
            return self

        while parent is not None:
            root = parent
            parent = parent.parent

        return root

    def mouse_inside(self):
        """
        Checks if the mouse is inside the window taking into account
        all other windows and draw priorities.
        """
        res = self.rectangle.intersects_with(self.mouse_pos)
        if not res:
            return False

        #Check all children of root to see if there is a higher priority
        #window than the current one
        root = self.get_root()
        stack = [root]
        visited = set()
        while stack:
            item = stack[-1]
            intersects_mouse = item.rectangle.intersects_with(self.mouse_pos)
            if item.children and not set(item.children).issubset(visited):
                stack.extend(item.children)
            else:
                if item is self:
                    break
                else:
                    res &= not intersects_mouse
                    visited.add(item)
                    stack.pop()

        return res

    def mouse_held(self):
        res = self.mouse_down
        stack = [self.get_root()]
        visited = set()
        while len(stack) > 0:
            item = stack[-1]
            if item.children and not set(item.children).issubset(visited):
                stack.extend(item.children)
            else:
                if self is not item:
                    res |= item.mouse_down
                visited.add(item)
                stack.pop()
        return res

    def process_mouse_move(self, obj, old_mpos, new_mpos):
        mouse_focus = self.mouse_inside()
        if not self.mouse_held():
            if mouse_focus:
                if not self.mouse_in:
                    print 'mouse-enter', self.name
                    self.dispatch('mouse-enter', self)
                    self.dispatch('hover', self)
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
            child_window.context = self.context
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
        position = Position.from_value(position)
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
        size = Size.from_value(size)
        if size.height <= self.min_size.height:
            size.height = self.min_size.height
        if size.width <= self.min_size.width:
            size.width = self.min_size.width
        diff = size - self.rectangle.size
        if diff.height != 0 or diff.width != 0:
            self.dispatch('resize', self, size)
            for child in self.children:
                pass
            #    child.size = child.size + diff
        self.rectangle.size = size

        if self.resizable:
            self.update_resize_handles()

class MyWindow(Window):
    def render(self):
        self.draw_rounded_rect([0,0], [self.size.width, self.size.height], line_width=2, corner_radius=3)


class TestWindow(Window):

    def draw_test(self, position, size, color=(1,1,1), line_width=1, line_color=(0,0,0), corner_radius=0):
        position = Position.from_value(position)
        size = Size.from_value(size)
        color = Color.from_value(color)
        line_color = Color.from_value(line_color)

        context = self.context
        radius = corner_radius
        degrees = math.pi / 180.0
        x = position.x + self.position.x
        y = position.y + self.position.y
        width = size.width
        height = size.height

        context.new_sub_path()
        context.set_source_rgba(0,0,1)
        context.set_line_width(line_width)
        context.arc(x + width - radius - line_width/2.0, y + radius + line_width/2.0, radius, -90 * degrees, -45 * degrees)
        point = context.get_current_point()
        context.stroke()
        context.move_to(*point)
        context.set_source_rgba(1,0,1)
        context.set_line_width(10)
        context.arc(x + width - radius - line_width/2.0, y + radius + line_width/2.0, radius, -45 * degrees, 0 * degrees)
        context.line_to(x + width - line_width/2.0, y + height - radius - line_width/2.0)
        context.arc(x + width - radius - line_width/2.0, y + height - radius - line_width/2.0, radius, 0 * degrees, 45 * degrees)
        point = context.get_current_point()
        context.stroke()
        context.move_to(*point)
        context.set_source_rgba(1,0,0)
        context.set_line_width(line_width)
        context.arc(x + width - radius - line_width/2.0, y + height - radius - line_width/2.0, radius, 45 * degrees, 90 * degrees)
        context.line_to(x + radius + line_width/2.0, y + height - line_width/2.0)
        context.arc(x + radius + line_width/2.0, y + height - radius - line_width/2.0, radius, 90 * degrees, 135 * degrees)
        point = context.get_current_point()
        context.stroke()
        context.move_to(*point)
        context.set_source_rgba(0,1,0)
        context.set_line_width(line_width)
        context.arc(x + radius + line_width/2.0, y + height - radius - line_width/2.0, radius, 135 * degrees, 180 * degrees)
        context.line_to(x + line_width/2.0, y + radius + line_width/2.0)
        context.arc(x + radius + line_width/2.0, y + radius + line_width/2.0, radius, 180 * degrees, 225 * degrees)
        point = context.get_current_point()
        context.stroke()
        context.move_to(*point)
        context.set_source_rgba(0,0,1)
        context.set_line_width(line_width)
        context.arc(x + radius + line_width/2.0, y + radius + line_width/2.0, radius, 225 * degrees, 270 * degrees)
        context.line_to(x + width - radius - line_width/2.0, y + line_width/2.0)
        context.stroke()

        context.new_sub_path()
        context.arc(x + width - radius - line_width/2.0, y + radius + line_width/2.0, radius, -90 * degrees, 0 * degrees)
        context.arc(x + width - radius - line_width/2.0, y + height - radius - line_width/2.0, radius, 0 * degrees, 90 * degrees)
        context.arc(x + radius + line_width/2.0, y + height - radius - line_width/2.0, radius, 90 * degrees, 180 * degrees)
        context.arc(x + radius + line_width/2.0, y + radius + line_width/2.0, radius, 180 * degrees, 270 * degrees)
        context.close_path()

        context.set_source_rgba(*color)
        context.fill()

    def render(self):
        self.draw_test([0,0], [self.size.width, self.size.height], corner_radius=10)

class Mouse(Window):
    def __init__(self, *args,  **kwargs):
        super(Mouse, self).__init__(*args, **kwargs)
        self.lines = [
                        [0, 0],
                        [0, self.size.height*0.85],
                        [self.size.width*0.32, self.size.height*0.675],
                        [self.size.width*0.52, self.size.height*0.9],
                        [self.size.width*0.72, self.size.height*0.85],
                        [self.size.width*0.52, self.size.height*0.62],
                        [self.size.width*0.92, self.size.height*0.6]
                    ]
    def render(self):
        self.draw_lines(self.lines, line_width=self.size.height/20)

