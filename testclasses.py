from jgui.surface import Surface, Window, Position, Size, Color, TextWindow, ImageWindow
import math

class TestSurface(Surface):
    def __init__(self, *args, **kwargs):
        super(TestSurface, self).__init__(*args, **kwargs)
        my_win = Window('child',
                        position=[0,0],
                        size=[500,200],
                        max_size=[600, -1],
                        draggable=True,
                        resizable=True,
                        min_size=Size(40,40),
                        border_width=5,
                        border_radius=[40,20],
                        border_color=(0,0,0),
                        background_color=(1,1,1),
                        clip_children=True,
                        ignore_debug=True,
                        background_image='/home/joey/Pictures/wrench.png',
                        background_image_filter='bilinear')

        my_win.add_child(TextWindow('text','Micro Bean is the best bean ever.',
                                    position=[20,20], size=[100, 50],
                                    resizable=True, clip_children=True,
                                    font_color=(1,0,1), padding=20,
                                    draggable=True))

        self.root_window.add_child(my_win)
        self.root_window.add_child(TestWindow('child2', position=[200,200],
                                              size=[200,200], draggable=True))

        self.root_window.add_child(ImageWindow('image', image_path='/home/joey/Pictures/wrench.png',
                                               position=[0,200], size=[200,200],
                                               draggable=True, resizable=True))

        child3 = TestWindow('child3', position=[300,300],
                            size=[200,200], draggable=True)
        child3.add_child(TestWindow('child3-1', position=[10,10],
                                    size=[50,50], draggable=True,
                                    resizable=True))

        self.root_window.add_child(child3)


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
        self.draw_test([0,0], [self.size.width, self.size.height], corner_radius=20)
