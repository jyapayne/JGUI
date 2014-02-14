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
    def __init__(self, width=1000, height=1000):
        ShowBase.__init__(self)
        self._render = True
        self.width = width
        self.height = height
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setSize(width, height)
        base.setBackgroundColor(0.5,1,1,1)
        base.cam.setPos(0,-10,0)
        base.win.requestProperties(props)
        c = CardMaker('plane')
        c.setFrame(-1, 1, 1, -1)
        c.setHasUvs(True)
        screen = render2d.attachNewNode(c.generate())
        screen.setTransparency(TransparencyAttrib.MAlpha)
        screen.setPos(0,0,0)

        self.surf = TestSurface([width, height])

        cairoTexture = Texture()
        cairoTexture.setMagfilter(Texture.FTNearest)
        cairoTexture.setMinfilter(Texture.FTNearest)
        cairoTexture.setXSize(width)
        cairoTexture.setYSize(height)
        cairoTexture.setFormat(cairoTexture.FRgba8)
        cairoTexture.setup2dTexture(width, height, Texture.TUnsignedByte, Texture.FRgba32)
        self.cairoTexture = cairoTexture
        screen.setTexture(cairoTexture)
        self.screen = screen

        self.accept('mouse1', self.click, ['mouse-left'])
        self.accept('mouse1-up', self.up, ['mouse-left'])
        self.accept('mouse2', self.click, ['mouse-middle'])
        self.accept('mouse2-up', self.up, ['mouse-middle'])
        self.accept('mouse3', self.click, ['mouse-right'])
        self.accept('mouse3-up', self.up, ['mouse-right'])
        self.accept('window-event', self.windowEvent)

        #taskMgr.setupTaskChain('move_chain', numThreads=1, threadPriority=TPLow, frameBudget=0.00001)
        #taskMgr.setupTaskChain('draw_chain', numThreads=2, threadPriority=TPHigh, frameSync=True)
        taskMgr.add(self.mousemove, 'mousemove')
        taskMgr.add(self.drawall, 'draw')

    def click(self, button):
        self.surf.inject_mouse_down(button)

    def up(self, button):
        self.surf.inject_mouse_up(button)

    def windowEvent(self, window):
        ShowBase.windowEvent(self, window) #call the super method to handle all other cases
        if window.isClosed():
            self._render = False
            return
        width, height = window.getXSize(), window.getYSize()
        if width != self.width or height != self.height:
            #self._render = False
            #while self.surf.drawing:
            #    pass
            #taskMgr.remove('mousemove')
            #taskMgr.remove('draw')
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
            #self._render = True
            #taskMgr.add(self.mousemove, 'mousemove', taskChain='move_chain')
            #taskMgr.add(self.drawall, 'draw', taskChain='move_chain')

    def drawall(self, task):
        if self._render:
            self.surf.draw()
            ri = self.cairoTexture.modifyRamImage()
            ri.setData(self.surf.csurface.get_data())
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
