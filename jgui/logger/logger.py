from __future__ import print_function
from jgui.settings import DEBUG

def log(*args):
    if DEBUG:
        print(*args)
