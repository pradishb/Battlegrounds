import sys

from direct.showbase.DirectObject import DirectObject
from panda3d.core import ClockObject
from direct_gui import ClientGui
from client_network import ClientNetwork


class Client(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        base.accept('escape', sys.exit, [0])
        base.setFrameRateMeter(True)
        globalClock.setFrameRate(60)
        globalClock.setMode(ClockObject.MLimited)

        self.myNetwork = ClientNetwork(self)
        self.clientGui = ClientGui(self)


Client()
base.run()
