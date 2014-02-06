#!/usr/bin/env python
import cairo
import pygame
import array
import math
import sys

from direct.showbase.ShowBase import ShowBase
from pandac.PandaModules import *

from testclasses import *

class Test(ShowBase):
    def __init__(self, width=1024, height=1024):
        ShowBase.__init__(self)
        self._render = True
        self.width = width
        self.height = height
        props = WindowProperties()
        props.setSize(width, height)
        base.setBackgroundColor(0.5,1,1,1)
        base.cam.setPos(0,-3.7,0)
        base.win.requestProperties(props)
        base.disableMouse()
        c = CardMaker('plane')
        c.setFrame(-1, 1, 1, -1)
        c.setHasUvs(True)
        screen = render2d.attachNewNode(c.generate())
        screen.setTransparency(TransparencyAttrib.MAlpha)
        screen.setTwoSided(True)

        self.surf = TestSurface([width, height])

        cairoTexture = Texture()
        cairoTexture.setXSize(width)
        cairoTexture.setYSize(height)
        cairoTexture.setFormat(cairoTexture.FRgba8)
        cairoTexture.setup2dTexture(width, height, Texture.TUnsignedByte, Texture.FRgba32)
        self.cairoTexture = cairoTexture
        screen.setTexture(cairoTexture)
        self.screen = screen
#screen.reparentTo(render2d)

        self.accept('mouse1', self.click)
        self.accept('mouse1-up', self.up)


        taskMgr.add(self.mousemove, 'mousemove')
        taskMgr.add(self.drawall, 'draw')
        self.accept('window-event', self.windowEvent)

    def click(self):
        self.surf.inject_mouse_down('mouse-left')

    def up(self):
        self.surf.inject_mouse_up('mouse-left')

    def windowEvent(self, window):
        ShowBase.windowEvent(self, window) #call the super method to handle all other cases
        if window.isClosed():
            self._render = False
            return
        width, height = window.getXSize(), window.getYSize()
        if width != self.width or height != self.height:
            self.width, self.height = width, height
            cairoTexture = Texture()
            cairoTexture.setMagfilter(Texture.FTNearest)
            cairoTexture.setMinfilter(Texture.FTNearest)
            cairoTexture.setXSize(self.width)
            cairoTexture.setYSize(self.height)
            cairoTexture.setFormat(cairoTexture.FRgba8)
            cairoTexture.setup2dTexture(width, height, Texture.TUnsignedByte, Texture.FRgba32)
            self.cairoTexture = cairoTexture
            self.screen.setTexture(cairoTexture)
            self.surf.notify_window_resize(window.getXSize(), window.getYSize())

    def drawall(self, task):
        if self._render:
            self.surf.draw()
            self.cairoTexture.setRamImage(self.surf.csurface.get_data())
            return task.cont

    def mousemove(self, task):
        if self._render:
            if base.mouseWatcherNode.hasMouse():
                x = base.win.getXSize() * (1 + base.mouseWatcherNode.getMouseX()) / 2
                y = base.win.getYSize() * (1 - base.mouseWatcherNode.getMouseY()) / 2
                self.surf.inject_mouse_position([x, y])
            return task.cont

if __name__ == '__main__':
    Test().run()
