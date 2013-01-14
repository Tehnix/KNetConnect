"""
Author: Christian Laustsen
License: BSD (See accompanying LICENSE file)

Description: Create a menulet in the system tray, and automate the process of connecting to 
the K-Net and logging in to the server with ssh.

"""

import urllib2
import webbrowser
import paramiko
import threading
import time
import objc, re, os
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper
from PyObjCTools.KeyValueCoding import *

import preferences


DEBUG = False

KNET_SERVER = 'fw2.k-net.dk'
USERNAME = getKey(preferences.defaults, u'username')
PASSWORD = getKey(preferences.defaults, u'password')

STATUS_IMAGES = {
    'idle': 'images/idle.png',
    'active': 'images/active.png',
    'pause': 'images/pause.png'
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

def invokePreferences():
    thread = threading.Thread(
        target=preferences.Preferences()
    )
    thread.start()


class Timer(NSObject):
    """
    Create a menulet in the system tray, and automate the process of connecting to 
    the K-Net and logging in to the server with ssh.
    
    """
    
    images = {}
    statusbar = None
    menuitems = {}
    checkForConnection = True
    lastCheck = time.time()
    ssh = None
    state = 'idle'
    
    def applicationDidFinishLaunching_(self, notification):
        """Initialize the application, putting an icon in the system tray, etc."""
        self.statusbar = NSStatusBar.systemStatusBar()
        self.statusitem = NSStatusBar.systemStatusBar().statusItemWithLength_(NSVariableStatusItemLength)
        self.statusitem.setHighlightMode_(1)
        self.statusitem.setToolTip_('KNet Connect')
        self.images = self.setUpImages()
        self.statusitem.setImage_(self.images['idle']) # Set initial image
        self.addMenuItems(self.statusitem)
        self.startTimer()
    
    def setState(self, state):
        """Set the state and change the picture if there is one."""
        if self.state != state:
            self.state = state
            if self.state in self.images:
                self.statusitem.setImage_(self.images[self.state])
    
    def closeConnection(self):
        """Close the ssh connection."""
        try:
            self.ssh.close()
        except AttributeError:
            pass
    
    def setUpImages(self):
        """Make objects of all the images, and store them in the instance variable."""
        images = {}
        for i in STATUS_IMAGES.keys():
            images[i] = NSImage.alloc().initByReferencingFile_(STATUS_IMAGES[i])
        return images
    
    def addMenuItems(self, statusitem):
        """Add menut items to the menu object."""
        items = [
            ['connection', 'Connecting...', '', ''],
            [],
            ['pause', 'Stop Connecting', 'pause:', ''],
            [],
            ['preferences', 'Preferences...', 'preferences:', ''],
            ['helpcenter', 'Help Center', 'helpcenter:', ''],
            [],
            ['quit', 'Quit                ', 'terminate:', '']
        ]
        menu = NSMenu.alloc().init()
        for item in items:
            if item:
                keyName, name, action, key = item
                menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(name, action, key)
                self.menuitems[keyName] = menuItem
            else:
                menuItem = NSMenuItem.separatorItem()
            menu.addItem_(menuItem)
        statusitem.setMenu_(menu) # Bind it to the status item
    
    def startTimer(self):
        """Execute the tick_() function on a regular interval."""
        self.timer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(
            START_TIME, 10.0, self, 'tick:', None, True
        )
        NSRunLoop.currentRunLoop().addTimer_forMode_(self.timer, NSDefaultRunLoopMode)
        self.timer.fire()
    
    def checkConnection(self):
        """Check if we are connected to the internet, or if we need to log in to K-Net."""
        conn, resp = testInternetConnection(CONNECTION_TEST_SITES)
        isKNet = "K-Net Login" in resp
        if conn and not isKNet:
            self.menuitems['connection'].setTitle_('Connected')
            self.setState('active')
        elif isKNet:
            self.menuitems['connection'].setTitle_('Connecting...')
            self.setState('idle')
            self.closeConnection()
            self.ssh = connectToKNet()
        else:
            self.menuitems['connection'].setTitle_('No Internet')
            self.setState('idle')
        lastCheck = time.time()
    
    def tick_(self, notification):
        """This gets executed on a regular interval."""
        if DEBUG: print self.state
        if self.checkForConnection:
            self.checkConnection()
    
    def pause_(self, notification):
        """Stop/Start checking if we are connected."""
        if DEBUG: print "pausing..."
        if self.checkForConnection:
            self.checkForConnection = False
            self.menuitems['pause'].setTitle_('Resume Connecting')
            self.setState('pause')
            self.closeConnection()
        else:
            self.checkForConnection = True
            if time.time() - lastCheck < 7:
                self.checkConnection()
            self.setState('idle')
            self.menuitems['connection'].setTitle_('Connecting...')
            self.menuitems['pause'].setTitle_('Stop Connecting')
    
    #def preferences_(self, notification):
    #    invokePreferences()
    
    def helpcenter_(self, notification):
        """Opens a webbrowser and directs to the github README."""
        webbrowser.open('https://github.com/Tehnix/KNetConnect', new=2)
        

if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = Timer.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()
    app.closeConnection()
