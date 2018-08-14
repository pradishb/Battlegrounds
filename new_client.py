from direct.showbase.ShowBase import ShowBase
from panda3d.core import ClockObject
from direct_gui import ClientGui
from client_network import ClientNetwork


class Client(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.setFrameRateMeter(True)
        globalClock.setFrameRate(60)
        globalClock.setMode(ClockObject.MLimited)

        self.clientGui = ClientGui(self)
        self.myNetwork = ClientNetwork(self.clientGui)


Client().run()
