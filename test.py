#!/usr/bin/env python
import cairo
import pygame
import array
import math
import sys

import direct.directbase.DirectStart
from pandac.PandaModules import *

from jgui.surface.surface import *

Width, Height = 1024, 1024
props = WindowProperties()
props.setSize(1024,1024)
base.setBackgroundColor(0.5,1,1,1)
base.cam.setPos(0,-10,0)
base.win.requestProperties(props)
c = CardMaker('plane')
c.setFrame(-1, 1, 1, -1)
c.setHasUvs(True)
screen = render2d.attachNewNode(c.generate())
#screen = loader.loadModel('plane')
screen.setTransparency(TransparencyAttrib.MAlpha)
screen.setTwoSided(True)
#screen.setScale(2)

surf = Surface([Width, Height])

cairoTexture = Texture()
cairoTexture.setXSize(Width)
cairoTexture.setYSize(Height)
cairoTexture.setFormat(cairoTexture.FRgba8)
cairoTexture.setup2dTexture(Width, Height, Texture.TUnsignedByte, Texture.FRgba32)

screen.setTexture(cairoTexture)
#screen.reparentTo(render2d)

def click():
    surf.inject_mouse_down('mouse-left')
def up():
    surf.inject_mouse_up('mouse-left')

base.accept('mouse1', click)
base.accept('mouse1-up', up)

def drawall(task):
    surf.draw()
    cairoTexture.setRamImage(surf.csurface.get_data())
    return task.cont

def mousemove(task):
    if base.mouseWatcherNode.hasMouse():
        x = base.win.getXSize() * (1 + base.mouseWatcherNode.getMouseX()) / 2
        y = base.win.getYSize() * (1 - base.mouseWatcherNode.getMouseY()) / 2
        surf.inject_mouse_position([x, y])
    return task.cont

taskMgr.add(mousemove, 'mousemove')
taskMgr.add(drawall, 'draw')
run()
