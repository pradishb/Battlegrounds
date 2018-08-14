from direct.showbase.ShowBase import ShowBase
from pandac.PandaModules import *
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.showbase.InputStateGlobal import inputState
from direct_gui import ClientGui


IP = '127.0.0.1'
PORT = 9099

MSG_NONE = 0
CMSG_AUTH = 1
SMSG_AUTH_RESPONSE = 2
CMSG_CHAT = 3
SMSG_CHAT = 4
CMSG_DISCONNECT_REQ = 5
SMSG_DISCONNECT_ACK = 6
CLIENT_INPUT = 7
SERVER_INPUT = 8
GAME_INITIALIZE = 9


class Client(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.setFrameRateMeter(True)
        globalClock.setFrameRate(60)
        globalClock.setMode(ClockObject.MLimited)

        self.clientGui = ClientGui()
        # self.gameEngine = ClientGameEngine()
        # self.accept("escape", self.sendMsgDisconnectReq)
        #
        # self.gameStart = False
        # self.myClock = 0
        # self.heading = 0
        # self.pitch = 40
        # self.skip = 0
        # self.loss = 0
        # self.id = 0
        #
        # inputState.watchWithModifiers('forward', 'w')
        # inputState.watchWithModifiers('left', 'a')
        # inputState.watchWithModifiers('reverse', 's')
        # inputState.watchWithModifiers('right', 'd')
        # inputState.watchWithModifiers('shoot', 'mouse1')
        #
        # # GameUI
        # self.healthUI = None
        # self.displayUI = GameUI.createDisplayUI("")
        #
        # self.serverWait = True


Client().run()
