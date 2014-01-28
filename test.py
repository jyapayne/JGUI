#!/usr/bin/env python
import cairo
import pygame
import array
import math
import sys

import direct.directbase.DirectStart
from pandac.PandaModules import *

from jgui.surface.surface import *

props = WindowProperties()
props.setSize(1024,1024)
base.setBackgroundColor(0.5,1,1,1)
base.cam.setPos(0,-10,0)
base.win.requestProperties(props)
screen = loader.loadModel('/home/joey/Creationista/models/plane.egg.pz')
screen.setTransparency(TransparencyAttrib.MAlpha)
screen.setTwoSided(True)
screen.setScale(2)
Width, Height = 1024, 1024

surf = Surface([Width, Height])

cairoTexture = Texture()
cairoTexture.setFormat(cairoTexture.FRgba8)
cairoTexture.setup2dTexture(Width, Height, Texture.CMDefault, Texture.FRgba32)

screen.setTexture(cairoTexture)
screen.reparentTo(render2d)

def drawall(task):
    surf.draw()
    cairoTexture.setRamImage(surf.csurface.get_data())
    return task.cont

taskMgr.add(drawall, 'draw')
run()
