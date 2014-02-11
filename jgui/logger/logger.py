from __future__ import print_function
import jgui.settings as settings

def log(*args):
    if settings.DEBUG:
        print(*args)
