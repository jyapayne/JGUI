from testclasses import *
from PyQt4 import QtGui,  QtCore
import sys, array
from cStringIO import StringIO

class JGUIWidget(QtGui.QWidget):
    def __init__(self, width, height, parent=None):
        super(JGUIWidget, self).__init__(parent)
        self.surf = TestSurface([width, height])
        self.setGeometry(0,0, width, height)
        self.width = width
        self.height = height
        self.setWindowTitle("JGUI Qt")
        redrawTimer = QtCore.QTimer(self)
        self.connect(redrawTimer,  QtCore.SIGNAL("timeout()"), self, QtCore.SLOT("update()"))
        redrawTimer.start(1000/60)
        self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        self.button = QtGui.QPushButton('Test', self)
        self.button.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        layout = QtGui.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignBottom)
        layout.addWidget(self.button)

        self.paintSurface = QtGui.QPainter(self)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.surf.inject_mouse_down('mouse-left')
        if event.button() == QtCore.Qt.RightButton:
            self.surf.inject_mouse_down('mouse-right')
        if event.button() == QtCore.Qt.MiddleButton:
            self.surf.inject_mouse_down('mouse-middle')

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.surf.inject_mouse_up('mouse-left')
        if event.button() == QtCore.Qt.RightButton:
            self.surf.inject_mouse_up('mouse-right')
        if event.button() == QtCore.Qt.MiddleButton:
            self.surf.inject_mouse_up('mouse-middle')

    def resizeEvent(self, event):
        size = event.size()
        self.width = size.width()
        self.height = size.height()
        self.surf.notify_window_resize(size.width(), size.height())

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseMove and self is source:
            pos = event.pos()
            self.surf.inject_mouse_position([pos.x(), pos.y()])
        return QtGui.QMainWindow.eventFilter(self, source, event)

    def paintEvent(self,  event):
        self.surf.draw()
        img = QtGui.QImage(self.surf.csurface.get_data(), self.width, self.height, QtGui.QImage.Format_ARGB32)
        self.paintSurface.begin(self)
        self.paintSurface.drawImage(0, 0, img)
        self.paintSurface.end()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    widget = JGUIWidget(800, 600)
    widget.show()
    app.installEventFilter(widget)
    sys.exit(app.exec_())
