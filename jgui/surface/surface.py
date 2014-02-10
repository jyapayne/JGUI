import cairo
import pango
import pangocairo as pc
import gtk
import math
from .structures import Size, Position, Rectangle, Color, BorderRadius, Padding, Gradient, RadialGradient
from ..events.events import WindowEventSource
from ..logger import log

debug = True

class Surface(object):
    def __init__(self, size=None, context=None, render_mouse=True):
        self.size = Size.from_value(size)
        if context is None:
            self.csurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.size.width, self.size.height)
            self.context = cairo.Context(self.csurface)
        else:
            self.context = context
        self.root_window = Window('root', position=Position(0,0), size=self.size, context=self.context)
        self.render_mouse = render_mouse
        if self.render_mouse:
            self.mouse_icon = Mouse('mouse', position=Position(0, 0), size=Size(12,20), context=self.context)
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



class WindowSurface(object):

    line_joins = {'miter': cairo.LINE_JOIN_MITER,
                  'round': cairo.LINE_JOIN_ROUND,
                  'bevel': cairo.LINE_JOIN_BEVEL}

    line_caps = {'round': cairo.LINE_CAP_ROUND,
                 'butt': cairo.LINE_CAP_BUTT,
                 'square': cairo.LINE_CAP_SQUARE}

    font_weights = {'bold': pango.WEIGHT_BOLD,
                    'normal': pango.WEIGHT_NORMAL,
                    'book': pango.WEIGHT_BOOK,
                    'heavy': pango.WEIGHT_HEAVY,
                    'light': pango.WEIGHT_LIGHT,
                    'medium': pango.WEIGHT_MEDIUM,
                    'semibold': pango.WEIGHT_SEMIBOLD,
                    'thin': pango.WEIGHT_THIN,
                    'ultrabold': pango.WEIGHT_ULTRABOLD,
                    'ultraheavy': pango.WEIGHT_ULTRAHEAVY,
                    'ultralight': pango.WEIGHT_ULTRALIGHT}

    font_styles = {'italic': pango.STYLE_ITALIC,
                   'oblique': pango.STYLE_OBLIQUE,
                   'normal': pango.STYLE_NORMAL}

    wrap_modes = {'word': pango.WRAP_WORD,
                  'char': pango.WRAP_CHAR,
                  'word_char': pango.WRAP_WORD_CHAR}

    font_map = pc.cairo_font_map_get_default()
    font_list = [f.get_name() for f in font_map.list_families()]

    filters = {'none': cairo.FILTER_FAST,
               'good': cairo.FILTER_GOOD,
               'best': cairo.FILTER_BEST,
               'bilinear': cairo.FILTER_BILINEAR,
               'gaussian': cairo.FILTER_GAUSSIAN,
               'nearest' : cairo.FILTER_NEAREST}

    def __init__(self):
        super(WindowSurface, self).__init__()

    def load_image(self, image_path):
        if image_path is not None:
            if isinstance(image_path, basestring):
                return gtk.gdk.pixbuf_new_from_file(image_path)
            else:
                return image_path

    def draw_circle(self, position, size, color=(1,1,1,1), line_width=1.0, line_color=(0,0,0,1), start_angle=0.0, end_angle=360.0):
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

        context.set_source_rgba(color.r, color.g, color.b, color.a)
        context.fill_preserve()
        context.set_source_rgba(line_color.r, line_color.g, line_color.b, line_color.a)
        context.stroke()

    def draw_image(self, image, position, size,
                   filter='none',
                   stretch_horizontal=False,
                   stretch_vertical=False,
                   keep_ratio=False,
                   center_horizontal=True,
                   center_vertical=True, image_offset=(0, 0)):

        context = self.context
        position = Position.from_value(position)
        offset = Position.from_value(image_offset)
        size = Size.from_value(size)
        width = size.width
        height = size.height

        x,y = (self.position.x+position.x,
               self.position.y+position.y)

        context.rectangle(x, y, width, height)
        context.clip()

        if isinstance(image, basestring):
            image = self.load_image(image)

        im_width = image.get_width()
        im_height = image.get_height()

        new_height = height
        new_width = width

        if keep_ratio:
            aspect_ratio = im_width/float(im_height)
            if width >= height:
                if im_height < im_width:
                    new_height = width/aspect_ratio
                else:
                    new_width = aspect_ratio * height
            else:
                if im_height > im_width:
                    new_width = aspect_ratio * height
                else:
                    new_height = width/aspect_ratio

        if center_horizontal:
            x += width/2.0 - new_width/2.0
            if x < self.position.x:
                x = self.position.x
        if center_vertical:
            y += height/2.0 - new_height/2.0
            if y < self.position.y:
                y = self.position.y

        im_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(new_width), int(new_height))

        sp = cairo.SurfacePattern(im_surf)

        ct2 = cairo.Context(im_surf)
        ct2.set_source(sp)

        ct3 = gtk.gdk.CairoContext(ct2)

        new_scale_x = 1
        new_scale_y = 1

        if stretch_horizontal or keep_ratio:
            new_scale_x = new_width/float(im_width)
        if stretch_vertical or keep_ratio:
            new_scale_y = new_height/float(im_height)

        ct3.scale(new_scale_x, new_scale_y)

        ct3.set_source_pixbuf(image, -offset.x, -offset.y)
        ct3.get_source().set_filter(self.filters[filter])
        ct3.paint()

        context.set_source_surface(im_surf,x,y)
        context.paint()


    def draw_text(self, text, position, font_size=12,
                  font_weight='normal',
                  font_style='normal', font_color=(0,0,0,1),
                  font_family='Sans', word_wrap='word',
                  alignment=pango.ALIGN_LEFT, line_width=1.0,
                  background_color=(1,1,1,0), fill_color=None):

        color = Color.from_value(font_color)
        background_color = Color.from_value(background_color)
        position = Position.from_value(position)
        context = self.context
        font_weight = self.font_weights[font_weight]
        font_style = self.font_styles[font_style]

        pc_context = pc.CairoContext(context)
        pc_context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        layout = pc_context.create_layout()
        font = pango.FontDescription('{} {}'.format(font_family, font_size))
        font.set_weight(font_weight)
        font.set_style(font_style)

        layout.set_font_description(font)
        layout.set_text(text)
        layout.set_wrap(self.wrap_modes[word_wrap])
        width = self.size.width - (self.padding.left + self.padding.right)
        layout.set_width(int(width*pango.SCALE))
        layout.set_alignment(alignment)

        context.set_line_width(line_width)
        context.set_source_rgba(font_color.r, font_color.g, font_color.b, font_color.a)

        extents = context.text_extents(text)

        x,y = (self.position.x+position.x+self.padding.left,
               self.position.y+position.y+self.padding.top)

        context.move_to(x, y)
        pc_context.update_layout(layout)
        pc_context.show_layout(layout)


    def draw_lines(self, lines, line_color=(0,0,0,1), background_color=(1,1,1,1), line_width=1, line_join='miter', line_cap='butt'):
        if lines:
            line_color = Color.from_value(line_color)
            background_color = Color.from_value(background_color)
            context = self.context
            start_pos = self.position + lines[0]
            context.set_line_width(line_width)
            context.move_to(start_pos.x, start_pos.y)
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
            context.set_source_rgba(background_color.r, background_color.g, background_color.b, background_color.a)
            context.fill_preserve()
            context.set_source_rgba(line_color.r, line_color.g, line_color.b, line_color.a)
            context.stroke()

    def render_radial_gradient(self, gradient, inner_radius=None, outer_radius=None):
        context = self.context
        position = self.position
        size = self.size
        gradient = RadialGradient.from_value(gradient)
        rp = cairo.RadialGradient(gradient.start_position.x*float(size.width) + position.x,
                                  gradient.start_position.y*float(size.height) + position.y,
                                  inner_radius or gradient.inner_radius,
                                  gradient.end_position.x*float(size.width) + position.x,
                                  gradient.end_position.y*float(size.height) + position.y,
                                  outer_radius or gradient.outer_radius)
        for gstop in gradient.stops:
            rp.add_color_stop_rgba(gstop.offset, gstop.color.r, gstop.color.g,
                                   gstop.color.b, gstop.color.a)
        if gradient.stops:
            context.save()
            context.set_source(rp)
            context.fill_preserve()
            context.restore()

    def render_linear_gradient(self, gradient):
        context = self.context
        position = self.position
        size = self.size
        gradient = Gradient.from_value(gradient)
        lp = cairo.LinearGradient(gradient.start_position.x*float(size.width) + position.x,
                                  gradient.start_position.y*float(size.height) + position.y,
                                  gradient.end_position.x*float(size.width) + position.x,
                                  gradient.end_position.y*float(size.height) + position.y)
        for gstop in gradient.stops:
            lp.add_color_stop_rgba(gstop.offset, gstop.color.r, gstop.color.g,
                                   gstop.color.b, gstop.color.a)
        if gradient.stops:
            context.save()
            context.set_source(lp)
            context.fill_preserve()
            context.restore()

    def draw_rounded_rect(self, position, size, background_color=(1,1,1), line_width=1, line_color=(0,0,0), corner_radius=0, line_dashed=False, clip=False, gradient=()):
        position = Position.from_value(position)
        size = Size.from_value(size)
        background_color = Color.from_value(background_color)
        line_color = Color.from_value(line_color)
        corner_radius = BorderRadius.from_value(corner_radius)
        gradient = Gradient.from_value(gradient)

        context = self.context
        radius = corner_radius
        degrees = math.pi / 180.0
        x = position.x + self.position.x
        y = position.y + self.position.y
        width = size.width
        height = size.height

        if clip: #clips the entire region so any child windows will be confined to the parent
            context.new_path()
            context.arc(x + width - radius.topright - line_width/2.0,
                        y + radius.topright + line_width/2.0,
                        radius.topright+self.border_width/2.0, -90 * degrees, 0 * degrees)
            context.arc(x + width - radius.bottomright - line_width/2.0,
                        y + height - radius.bottomright - line_width/2.0,
                        radius.bottomright+self.border_width/2.0, 0 * degrees, 90 * degrees)
            context.arc(x + radius.bottomleft + line_width/2.0,
                        y + height - radius.bottomleft - line_width/2.0,
                        radius.bottomleft+self.border_width/2.0, 90 * degrees, 180 * degrees)
            context.arc(x + radius.topleft + line_width/2.0,
                        y + radius.topleft + line_width/2.0,
                        radius.topleft+self.border_width/2.0, 180 * degrees, 270 * degrees)
            context.close_path()
            context.clip()

        context.new_path()
        context.arc(x + width - radius.topright - line_width/2.0,
                    y + radius.topright + line_width/2.0,
                    radius.topright, -90 * degrees, 0 * degrees)
        context.arc(x + width - radius.bottomright - line_width/2.0,
                    y + height - radius.bottomright - line_width/2.0,
                    radius.bottomright, 0 * degrees, 90 * degrees)
        context.arc(x + radius.bottomleft + line_width/2.0,
                    y + height - radius.bottomleft - line_width/2.0,
                    radius.bottomleft, 90 * degrees, 180 * degrees)
        context.arc(x + radius.topleft + line_width/2.0,
                    y + radius.topleft + line_width/2.0,
                    radius.topleft, 180 * degrees, 270 * degrees)
        context.close_path()

        if gradient.stops:
            if gradient._type == 'linear':
                self.render_linear_gradient(gradient)
            elif gradient._type == 'radial':
                self.render_radial_gradient(gradient)
            else:
                context.set_source_rgba(background_color.r, background_color.g, background_color.b, background_color.a)
        else:
            context.set_source_rgba(background_color.r, background_color.g, background_color.b, background_color.a)

        context.fill_preserve()
        context.set_source_rgba(line_color.r, line_color.g, line_color.b, line_color.a)
        context.set_line_width(line_width)
        context.save()
        if line_dashed:
            context.set_dash([line_width, line_width])
        context.stroke()
        context.restore()

        if clip: #clips the entire region so any child windows will be confined to the parent
            context.new_path()
            context.arc(x + width - radius.topright - line_width/2.0,
                        y + radius.topright + line_width/2.0,
                        radius.topright-self.border_width/2.0, -90 * degrees, 0 * degrees)
            context.arc(x + width - radius.bottomright - line_width/2.0,
                        y + height - radius.bottomright - line_width/2.0,
                        radius.bottomright-self.border_width/2.0, 0 * degrees, 90 * degrees)
            context.arc(x + radius.bottomleft + line_width/2.0,
                        y + height - radius.bottomleft - line_width/2.0,
                        radius.bottomleft-self.border_width/2.0, 90 * degrees, 180 * degrees)
            context.arc(x + radius.topleft + line_width/2.0,
                        y + radius.topleft + line_width/2.0,
                        radius.topleft-self.border_width/2.0, 180 * degrees, 270 * degrees)
            context.close_path()
            context.clip()


    def render(self):
        if debug and not self.ignore_debug:
            self.draw_rounded_rect([0,0], [self.size.width, self.size.height], background_color=(0,0,1,0.1), line_color=(0,0,1,0.4), line_width=self.border_width+0.5, corner_radius=self.border_radius, line_dashed=True)

    def draw(self):
        if self.visible:
            self.context.save()
            self.render()
            for child in self.children:
                child.draw()
            self.context.restore()


class Window(WindowEventSource, WindowSurface):
    def __init__(self, name, **kwargs):
        super(Window, self).__init__()
        self._draggable = False
        self._resizable = False
        self._root = None

        self.name = name

        position = Position.from_value(kwargs.pop('position', Position()))
        size = Size.from_value(kwargs.pop('size', Size()))
        self._context = kwargs.pop('context', None)
        self.min_size = Size.from_value(kwargs.pop('min_size', Size(1,1)))
        self.max_size = Size.from_value(kwargs.pop('max_size', Size(-1,-1)))
        self.corner_handle_size = Size.from_value(kwargs.pop('corner_handle_size', Size(20, 20)))
        self.edge_handle_width = kwargs.pop('edge_handle_width', 10)
        self.edge_handle_buffer = Size.from_value(kwargs.pop('edge_handle_buffer', Size(5, 5)))
        self.border_width = kwargs.pop('border_width', 1)
        self.border_color = Color.from_value(kwargs.pop('border_color', (0,0,0,0)))
        self.background_color = Color.from_value(kwargs.pop('background_color', (0,0,0,0)))
        self.background_image = self.load_image(kwargs.pop('background_image', None))
        self.background_image_filter = kwargs.pop('background_image_filter','none')
        self.background_image_stretch_horizontal = kwargs.pop('background_image_stretch_horizontal', False)
        self.background_image_stretch_vertical = kwargs.pop('background_image_stretch_vertical', False)
        self.background_image_keep_ratio = kwargs.pop('background_image_keep_ratio', False)
        self.background_image_center_horizontal = kwargs.pop('background_image_center_horizontal', True)
        self.background_image_center_vertical = kwargs.pop('background_image_center_vertical', True)
        self.background_image_offset = Position.from_value(kwargs.pop('background_image_offset', (0, 0)))

        self.gradient = Gradient.from_value(kwargs.pop('gradient', ()))

        self.border_radius = BorderRadius.from_value(kwargs.pop('border_radius', 1))
        self.padding = Padding.from_value(kwargs.pop('padding', 0))
        self.dashed_border = kwargs.pop('dashed_border', False)
        self.clip_children = kwargs.pop('clip_children', False)
        self.ignore_debug = kwargs.pop('ignore_debug', False)

        self.rectangle = Rectangle()
        self.children = []
        self.parent = None
        self.mouse_pos = Position(size.width/2, size.height/2)
        self.mouse_diff = Position(0, 0)
        self.mouse_in = False
        self.mouse_hover = False
        self.mouse_down = False
        self.mouse_inputs = dict.fromkeys(self.mouse_button_down_events, False)
        self.focused = False
        self.visible = True
        self.accept('mouse-move', self.process_mouse_move)
        self.size = size
        self.position = position
        self.context = self._context
        self.resizable = kwargs.pop('resizable', self._resizable)
        self.draggable = kwargs.pop('draggable', self._draggable)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def render(self):
        super(Window, self).render()
        self.draw_rounded_rect([0,0], [self.size.width, self.size.height],
                               background_color=self.background_color,
                               line_color=self.border_color,
                               line_width=self.border_width,
                               corner_radius=self.border_radius,
                               line_dashed=self.dashed_border,
                               clip=self.clip_children, gradient=self.gradient)

        if self.background_image is not None:
            self.draw_image(self.background_image, [0, 0], self.size,
                            filter=self.background_image_filter,
                            stretch_horizontal=self.background_image_stretch_horizontal,
                            stretch_vertical=self.background_image_stretch_vertical,
                            keep_ratio=self.background_image_keep_ratio,
                            center_horizontal=self.background_image_center_horizontal,
                            center_vertical=self.background_image_center_vertical,
                            image_offset=self.background_image_offset)

    @property
    def resizable(self):
        return self._resizable

    @resizable.setter
    def resizable(self, value):
        if not self._resizable and value:
            self.init_resize_handles()
        elif not value and self._resizable:
            self.remove_resize_handles()
        self._resizable = value

    @property
    def draggable(self):
        return self._draggable

    @draggable.setter
    def draggable(self, value):
        self._draggable = value
        self.enable_drag(self._draggable)

    def enable_drag(self, value):
        if value:
            self.accept('mouse-left-drag', self.drag)
            self.accept('mouse-left', self.click)
            self.accept('mouse-left-up', self.click_up)
        else:
            self.reject('mouse-left-drag', self.drag)
            self.reject('mouse-left', self.click)
            self.reject('mouse-left-up', self.click_up)

    def _restrict_pos_size_height(self, new_pos, new_size):
        if new_size.height <= self.min_size.height:
            new_pos.y = self.position.y + self.size.height - self.min_size.height
            new_size.height = self.min_size.height

        if self.max_size.height > -1 and new_size.height >= self.max_size.height:
            new_pos.y = self.position.y + self.size.height - self.max_size.height
            new_size.height = self.max_size.height

        return new_pos, new_size

    def _restrict_pos_size_width(self, new_pos, new_size):

        if new_size.width <= self.min_size.width:
            new_pos.x = self.position.x + self.size.width - self.min_size.width
            new_size.width = self.min_size.width

        if self.max_size.width > -1 and new_size.width >= self.max_size.width:
            new_pos.x = self.position.x + self.size.width - self.max_size.width
            new_size.width = self.max_size.width

        return new_pos, new_size

    def _restrict_pos_size(self, new_pos, new_size):
        self._restrict_pos_size_height(new_pos, new_size)
        self._restrict_pos_size_width(new_pos, new_size)
        return new_pos, new_size

    def drag_bottomright_handle(self, obj, mouse_pos):
        diff = mouse_pos - self.mouse_diff
        old_size = Size.from_value(self.size)
        self.size = self.size + diff
        self.mouse_diff.y = obj.position.y + self.handle_diff.y
        self.mouse_diff.x = obj.position.x + self.handle_diff.x

    def drag_bottomleft_handle(self, obj, mouse_pos):
        diff = mouse_pos - self.mouse_diff
        old_size = Size.from_value(self.size)
        new_pos = Position(self.position.x + diff.x, self.position.y)
        new_size = Size(self.size.width - diff.x, self.size.height + diff.y)

        new_pos, new_size = self._restrict_pos_size_width(new_pos, new_size)

        if self.draggable:
            self.position = new_pos
            self.size = new_size
        else:
            self.size = [self.size.width, new_size.height]

        self.mouse_diff.y = obj.position.y + self.handle_diff.y
        self.mouse_diff.x = obj.position.x + self.handle_diff.x

    def drag_topright_handle(self, obj, mouse_pos):
        diff = mouse_pos - self.mouse_diff
        old_size = Size.from_value(self.size)
        new_pos = Position(self.position.x, self.position.y + diff.y)
        new_size = Size(self.size.width + diff.x, self.size.height - diff.y)

        new_pos, new_size = self._restrict_pos_size_height(new_pos, new_size)

        if self.draggable:
            self.position = new_pos
            self.size = new_size
        else:
            self.size = [new_size.width, self.size.height]

        self.mouse_diff.y = obj.position.y + self.handle_diff.y
        self.mouse_diff.x = obj.position.x + self.handle_diff.x

    def drag_topleft_handle(self, obj, mouse_pos):
        diff = mouse_pos - self.mouse_diff
        old_size = Size.from_value(self.size)
        new_pos = Position(self.position.x + diff.x, self.position.y + diff.y)
        new_size = Size(self.size.width - diff.x, self.size.height - diff.y)

        new_pos, new_size = self._restrict_pos_size(new_pos, new_size)

        if self.draggable:
            self.position = new_pos
            self.size = new_size

        self.mouse_diff.y = obj.position.y + self.handle_diff.y
        self.mouse_diff.x = obj.position.x + self.handle_diff.x

    def drag_top_handle(self, obj, mouse_pos):
        diff = mouse_pos - self.mouse_diff
        old_size = Size.from_value(self.size)
        new_pos = Position(self.position.x, self.position.y + diff.y)
        new_size = Size(self.size.width, self.size.height - diff.y)

        new_pos, new_size = self._restrict_pos_size(new_pos, new_size)

        if self.draggable:
            self.position = new_pos
            self.size = new_size

        self.mouse_diff.y = obj.position.y + self.handle_diff.y
        self.mouse_diff.x = obj.position.x + self.handle_diff.x

    def drag_left_handle(self, obj, mouse_pos):
        diff = mouse_pos - self.mouse_diff
        old_size = Size.from_value(self.size)
        new_pos = Position(self.position.x+diff.x, self.position.y)
        new_size = Size(self.size.width - diff.x, self.size.height)

        new_pos, new_size = self._restrict_pos_size(new_pos, new_size)

        if self.draggable:
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

    def remove_resize_handles(self):
        self.remove_child(self.top_handle)
        self.remove_child(self.topleft_handle)
        self.remove_child(self.topright_handle)
        self.remove_child(self.left_handle)
        self.remove_child(self.right_handle)
        self.remove_child(self.bottom_handle)
        self.remove_child(self.bottomright_handle)
        self.remove_child(self.bottomleft_handle)
        self.top_handle = None
        self.topleft_handle = None
        self.topright_handle = None
        self.left_handle = None
        self.right_handle = None
        self.bottom_handle = None
        self.bottomright_handle = None
        self.bottomleft_handle = None

    def init_resize_handles(self):
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

        self.add_child(self.top_handle)
        self.add_child(self.topleft_handle)
        self.add_child(self.topright_handle)
        self.add_child(self.left_handle)
        self.add_child(self.right_handle)
        self.add_child(self.bottom_handle)
        self.add_child(self.bottomright_handle)
        self.add_child(self.bottomleft_handle)
        self.update_resize_handles()

    def update_resize_handles(self):
        buffer = self.edge_handle_buffer
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

        vertical_edge_size.width = self.size.width - 2*corner_handle_size.width
        vertical_edge_size.height = self.edge_handle_width

        horizontal_edge_size.width = self.edge_handle_width
        horizontal_edge_size.height = self.size.height - 2*corner_handle_size.height

        top.position.x = x + corner_handle_size.width
        top.position.y = y - buffer.height
        top.size = vertical_edge_size + [0, buffer.height]

        topleft.position.x = x - buffer.width
        topleft.position.y = y - buffer.height
        topleft.size = corner_handle_size + buffer

        topright.position.x = x + self.size.width - corner_handle_size.width
        topright.position.y = y - buffer.height
        topright.size = corner_handle_size + buffer

        bottom.position.x = x + corner_handle_size.width
        bottom.position.y = y + self.size.height - vertical_edge_size.height
        bottom.size = vertical_edge_size + [0, buffer.height]

        bottomleft.position.x = x - buffer.width
        bottomleft.position.y = y + self.size.height - corner_handle_size.height
        bottomleft.size = corner_handle_size + buffer

        bottomright.position.x = x + self.size.width-corner_handle_size.width
        bottomright.position.y = y + self.size.height-corner_handle_size.height
        bottomright.size = corner_handle_size + buffer

        right.position.x = x + self.size.width-horizontal_edge_size.width
        right.position.y = y + corner_handle_size.height
        right.size = horizontal_edge_size + [buffer.width, 0]

        left.position.x = x - buffer.width
        left.position.y = y + corner_handle_size.height
        left.size = horizontal_edge_size + [buffer.width, 0]

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

    def get_clip_parent(self):
        parent = self.parent
        l = []
        while parent is not None:
            if parent.clip_children:
                l.append(parent)
            parent = parent.parent
        if l:
            return l[-1]

    def inject_mouse_down(self, button):
        if self.mouse_inside():
            log(button, self.name)
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
            log(button+'-up', self.name)
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
        parent = self
        #Reorder all the windows so that they are drawn on top
        while parent is not None:
            if parent.parent is not None:
                children = parent.parent.children[:]
                children.remove(parent)
                children.append(parent)

                parent.parent.children = children

            parent = parent.parent

        self.dispatch('focus', self)

    def release_focus(self):
        if self.focused:
            log('released', self.name)
            self.focused = False
            self.mouse_down = False
            #clear events that may have been triggered
            #eg. User clicks on one window, holds, and
            #then releases on another
            for key in self.mouse_inputs:
                self.mouse_inputs[key] = False
            self.dispatch('focus-lost', self)

    @property
    def root(self):
        if self._root is None:
            parent = self.parent
            if parent is None:
                return self

            while parent is not None:
                root = parent
                parent = parent.parent

            self._root = root
        return self._root

    def mouse_inside(self):
        """
        Checks if the mouse is inside the window taking into account
        all other windows and draw priorities.
        """
        rec = self.rectangle
        clip_parent = self.get_clip_parent()
        if clip_parent is not None:
            rec = self.rectangle.intersection(clip_parent.rectangle)
        res = rec.intersects_with(self.mouse_pos)
        if not res:
            return False

        #Check all children of root to see if there is a higher priority
        #window than the current one
        root = self.root
        stack = [root]
        visited = set()
        while stack:
            item = stack[-1]
            rec = item.rectangle
            clip_parent = item.get_clip_parent()
            if clip_parent is not None:
                rec = item.rectangle.intersection(clip_parent.rectangle)
            intersects_mouse = rec.intersects_with(self.mouse_pos)
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
        stack = [self.root]
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
                    log('mouse-enter', self.name)
                    self.dispatch('mouse-enter', self)
                    self.dispatch('hover', self)
                self.mouse_in = True
            else:
                if self.mouse_in:
                    log('mouse-leave', self.name)
                    self.dispatch('mouse-leave', self)
                self.mouse_in = False

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context):
        self._context = context
        for child in self.children:
            child.context = self._context

    def add_child(self, child_window):
        if child_window not in self.children:
            child_window.parent = self
            child_window.position = child_window.position + self.position +\
                                    [self.border_width/2, self.border_width/2] +\
                                    [self.padding.left, self.padding.top]
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

        if self.max_size.width > -1 and size.width >= self.max_size.width:
            size.width = self.max_size.width
        if self.max_size.height > -1 and size.height >= self.max_size.height:
            size.height = self.max_size.height

        diff = size - self.rectangle.size
        if diff.height != 0 or diff.width != 0:
            self.dispatch('resize', self, size)
            for child in self.children:
                pass
            #    child.size = child.size + diff
        self.rectangle.size = size

        if self.resizable:
            self.update_resize_handles()

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


class TextWindow(Window):

    def __init__(self, name, text, *args, **kwargs):
        super(TextWindow, self).__init__(name, *args, **kwargs)
        self.font_size = kwargs.pop('font_size', 12)
        self.font_style = kwargs.pop('font_style', 'normal')
        self.font_weight = kwargs.pop('font_weight', 'normal')
        self.font_family = kwargs.pop('font_family', 'Sans')
        self.word_wrap = kwargs.pop('word_wrap', 'word')
        self.font_color = Color.from_value(kwargs.pop('font_color', (0,0,0,1)))
        self.text = text

    def render(self):
        super(TextWindow, self).render()
        self.draw_text(self.text, [0,0],
                       self.font_size, font_weight=self.font_weight,
                       font_style=self.font_style, font_family=self.font_family,
                       font_color=self.font_color, word_wrap=self.word_wrap)

class ImageWindow(Window):
    def __init__(self, name, image_path, *args, **kwargs):
        super(ImageWindow, self).__init__(name, *args, **kwargs)
        self.image_path = image_path
        self.image = self.load_image(self.image_path)

    def render(self):
        self.draw_image(self.image, [0,0], self.size)
        super(ImageWindow, self).render()

