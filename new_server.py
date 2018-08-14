from direct.showbase.ShowBase import ShowBase
from panda3d.core import ClockObject
from direct_gui import ServerGui
from server_network import ServerNetwork


class Server(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.setFrameRateMeter(True)
        globalClock.setFrameRate(60)
        globalClock.setMode(ClockObject.MLimited)

        self.serverGui = ServerGui()
        self.myNetwork = ServerNetwork(self.serverGui)


Server().run()
