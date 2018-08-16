import sys

from direct.showbase.DirectObject import DirectObject
from panda3d.core import ClockObject
from direct_gui import ServerGui
from server_network import ServerNetwork


class Server(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        base.accept('escape', sys.exit, [0])
        base.setFrameRateMeter(True)
        globalClock.setFrameRate(60)
        globalClock.setMode(ClockObject.MLimited)

        self.serverGui = ServerGui()
        self.myNetwork = ServerNetwork(self.serverGui)


Server()
base.run()
