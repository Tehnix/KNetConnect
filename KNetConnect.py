import objc, re, os
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper
import urllib2
import webbrowser
import paramiko

DEBUG = False

KNET_SERVER = 'fw2.k-net.dk'
USERNAME = 'username'
PASSWORD = 'password'

STATUS_IMAGES = {
    'idle': 'images/idle.png',
    'active': 'images/active.png'
}
START_TIME = NSDate.date()
CONNECTION_TEST_SITES = [
    'http://173.194.32.0',
    'http://google.com',
    'http://98.138.253.109',
    'http://212.112.131.20'
]

def testInternetConnection(testIPs):
    for test in testIPs:
        try:
            res = urllib2.urlopen(test, timeout=1)
            return (True, res.read())
        except urllib2.URLError: 
            pass
        except ValueError:
            pass
    return (False, "")
    

def connectToKNet():
    if DEBUG: print "Trying to connect to KNet..."
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(KNET_SERVER, username=USERNAME, password=PASSWORD)
    stdin, stdout, stderr = ssh.exec_command('ls')
    return ssh


class Timer(NSObject):
    
    images = {}
    statusbar = None
    internet = False
    ssh = None
    state = 'idle'
    
    def applicationDidFinishLaunching_(self, notification):
        self.statusbar = NSStatusBar.systemStatusBar()
        self.statusitem = NSStatusBar.systemStatusBar().statusItemWithLength_(NSVariableStatusItemLength)
        self.statusitem.setHighlightMode_(1)
        self.statusitem.setToolTip_('KNet Connect')
        self.images = self.setUpImages()
        self.statusitem.setImage_(self.images['idle']) # Set initial image
        self.addMenuItems(self.statusitem)
        self.startTimer()
    
    def setState(self, state):
        if self.state != state:
            self.state = state
            if self.state in self.images:
                self.statusitem.setImage_(self.images[self.state])
    
    def setUpImages(self):
        images = {}
        for i in STATUS_IMAGES.keys():
            images[i] = NSImage.alloc().initByReferencingFile_(STATUS_IMAGES[i])
        return images
    
    def addMenuItems(self, statusitem):
        items = [
            ['Preferences...', 'preferences:', ''],
            ['Help Center', 'helpcenter:', ''],
            [],
            ['Quit KNetConnect', 'terminate:', '']
        ]
        menu = NSMenu.alloc().init()
        for item in items:
            if item:
                name, action, key = item
                menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(name, action, key)
            else:
                menuItem = NSMenuItem.separatorItem()
            menu.addItem_(menuItem)
        statusitem.setMenu_(menu) # Bind it to the status item
    
    def startTimer(self):
        self.timer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(
            START_TIME, 10.0, self, 'tick:', None, True
        )
        NSRunLoop.currentRunLoop().addTimer_forMode_(self.timer, NSDefaultRunLoopMode)
        self.timer
    
    def checkConnection(self):
        conn, resp = testInternetConnection(CONNECTION_TEST_SITES)
        isKNet = "K-Net Login" in resp
        if conn and not isKNet:
            self.internet = True
            self.setState('active')
        elif isKNet:
            self.setState('idle')
            self.internet = False
            try:
                self.ssh.close()
            except AttributeError:
                pass
            self.ssh = connectToKNet()
        else:
            self.internet = False
            self.setState('idle')
    
    def tick_(self, notification):
        if DEBUG: print self.state
        self.checkConnection()
    
    def helpcenter_(self, notification):
        """Opens a webbrowser and directs to the github README."""
        webbrowser.open('https://github.com/Tehnix/KNetConnect', new=2)


if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = Timer.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()
    try:
        app.ssh.close()
    except AttributeError:
        pass
