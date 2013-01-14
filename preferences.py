from Tkinter import *
import threading
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper
from PyObjCTools.KeyValueCoding import *


dictionary = {}
dictionary[u'username'] = u'pbkxxxx.xxx'
dictionary[u"password"] = u'xxxxxxxx'
NSUserDefaultsController.sharedUserDefaultsController().setInitialValues_(dictionary)

defaults = NSUserDefaultsController.sharedUserDefaultsController().values()

class Preferences(threading.Thread):
    
    def __init__(self):
        self.window = Tk()
        self.window.title("KNetConnect Preferences")
        self.window.resizable(width=FALSE, height=FALSE)
        self.window.geometry("400x200+500+250")
        self.window.mainloop()

if __name__ == '__main__':
    Preferences()
