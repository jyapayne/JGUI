JGUI
====

A general purpose, batteries included, vector based GUI library made in python and pycairo. It's goal is to be reusable, multiplatform and visually scalable. As long as you have a cairo surface or something that can display an array of pixels, this library should work. 

Right now I have an example in test.py that tests the functionality in panda3d. Go to panda3d.org to download it and then run the script with python test.py.


Startup Guide
-------------

Install python-cairo, python-gobject, python-gi-cairo

On Ubuntu:

    sudo apt-get install python-cairo python-gobject python-gi-cairo -y

To run test.py and gtktest.py, you'll need panda3d and pygtk respectively

    sudo apt-get install python-gtk2

You'll have to go to https://www.panda3d.org/download.php?sdk&version=1.8.1 to get the latest version, or compile it from source if your OS isn't supported.

After that, you should be able to run

    python test.py
    
or

    python gtktest.py
    
Screenshots
-----------

![ScreenShot](https://raw.github.com/jyapayne/JGUI/master/screenshots/Multiple_windows_with_subwindows_and_background_images.png)

![ScreenShot](https://raw.github.com/jyapayne/JGUI/master/screenshots/gradients.png)
