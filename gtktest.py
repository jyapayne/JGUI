from testclasses import *
import pygtk, gtk, gobject, cairo
from gtk import gdk

class JGUIWidget(gtk.DrawingArea):
    buttons = {1:'mouse-left',
               2:'mouse-middle',
               3:'mouse-right'}

    def __init__(self, width, height):
        super(JGUIWidget, self).__init__()
        self.surf = TestSurface([width, height])
        self.connect("expose_event", self.expose)
        self.connect("motion_notify_event", self.mousemoved)
        self.connect("button_press_event", self.mouse_down)
        self.connect("button_release_event", self.mouse_up)
        self.connect("configure_event", self.resize_win)
        self.connect("scroll_event", self.mouse_scroll)
        self.add_events(gdk.BUTTON_PRESS_MASK | gdk.BUTTON_RELEASE_MASK | gdk.POINTER_MOTION_MASK)
        gobject.timeout_add(int((1.0/60.0)*1000), self.tick)
        self.width, self.height = width, height
        self.set_size_request(width, height)

    def mouse_up(self, widget, event):
        self.surf.inject_mouse_up(self.buttons[event.button])

    def mouse_down(self, widget, event):
        if event.type == gtk.gdk.BUTTON_PRESS:
            self.surf.inject_mouse_down(self.buttons[event.button])
        elif event.type == gtk.gdk._2BUTTON_PRESS:
            self.surf.inject_mouse_double(self.buttons[event.button])

    def mouse_scroll(self, widget, event):
        if event.direction == gtk.gdk.SCROLL_UP:
            direction = 1
        else:
            direction = -1
        self.surf.inject_mouse_wheel(direction)

    def resize_win(self, widget, event):
        self.surf.notify_window_resize(event.width, event.height)

    def tick(self):
        self.alloc = self.get_allocation()
        rect = gdk.Rectangle(self.alloc.x, self.alloc.y, self.alloc.width, self.alloc.height)
        self.window.invalidate_rect(rect, True)
        return True

    def expose(self, widget, event):
        self.surf.draw()
        context = widget.window.cairo_create()
        #Just set the source image to be the cairo image surface of the Surface object
        context.set_source_surface(self.surf.csurface, 0, 0)
        context.paint()

    def mousemoved(self, widget, event):
        self.surf.inject_mouse_position([event.x, event.y])


class GTKJGUI(object):
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('JGUI Test')
        self.window.connect("realize", self.realize)
        self.window.connect("delete_event", gtk.main_quit)
        self.drawingarea = JGUIWidget(800, 800)
        self.window.add(self.drawingarea)
        self.drawingarea.show()
        self.window.show()
        gtk.main()

    def realize(self, widget):
        pixmap = gtk.gdk.Pixmap(None, 1, 1, 1)
        color = gtk.gdk.Color()
        cursor = gtk.gdk.Cursor(pixmap, pixmap, color, color, 0, 0)
        widget.window.set_cursor(cursor)

if __name__ == '__main__':
    GTKJGUI()
