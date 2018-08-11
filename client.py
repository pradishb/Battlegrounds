from panda3d.bullet import ZUp
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.showbase.InputStateGlobal import inputState

from game import ClientGameEngine
from player import Player
from bullet import Bullet
from raycollider import RayCollider
import math
import sys

IP = '127.0.0.1'
PORT = 9099
USERNAME = "yellow"
PASSWORD = "mypass"

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

class Client(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.gameEngine = ClientGameEngine()
        self.myBullet = Bullet(self.gameEngine.world)
        self.accept("escape", self.sendMsgDisconnectReq)

        self.gameStart = False
        self.myClock = 0
        self.heading = 0
        self.pitch = 40



        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('left', 'a')
        inputState.watchWithModifiers('reverse', 's')
        inputState.watchWithModifiers('right', 'd')
        inputState.watchWithModifiers('jump', 'space')

        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)

        self.Connection = self.cManager.openTCPClientConnection(IP, PORT, 1)

        if(self.Connection):
            self.cReader.addConnection(self.Connection)
            taskMgr.add(self.readTask, "serverReaderPollTask", -39)
            self.sendMsgAuth()
        self.serverWait = True

    # player inputs
    def processInput(self):
        self.gameEngine.speed.setX(0)
        self.gameEngine.speed.setY(0)
        inputList = [False] * 5
        if inputState.isSet('forward'):
            inputList[0] = True
        if inputState.isSet('left'):
            inputList[1] = True
        if inputState.isSet('reverse'):
            inputList[2] = True
        if inputState.isSet('right'):
            inputList[3] = True
        if inputState.isSet('jump'):
            self.myBullet.update()
            # playerNode.doJump()
            inputList[4] = True
        self.sendUserInput(inputList)

    def moveCamera(self):
        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()

        if base.win.movePointer(0, 300, 300):
            self.heading = self.heading - (x - 300) * 0.2
            self.pitch = self.pitch - (y - 300) * 0.2
            if (self.pitch < -30.0):
                self.pitch = -30.0
            elif (self.pitch > 45.0):
                self.pitch = 45.0

        self.gameEngine.players[self.id].playerNP.lookAt(RayCollider.getObjectHit())
        base.cam.setHpr(self.heading, self.pitch, 0)
        base.cam.setX(self.gameEngine.players[self.id].playerNP.getX() + 2 * math.sin(
            math.pi / 180.0 * self.heading))
        base.cam.setY(self.gameEngine.players[self.id].playerNP.getY() - 2 * math.cos(
            math.pi / 180.0 * self.heading))
        base.cam.setZ(self.gameEngine.players[self.id].playerNP.getZ() - 0.03 * self.pitch + .5)
        base.cam.setPos(base.cam, .5, 0, 0)

    # Update
    def update(self, task):
        self.moveCamera()
        if(not self.serverWait):
            self.processInput()
            self.serverWait = True
        dt = globalClock.getDt()
        self.gameEngine.world.doPhysics(dt)
        return task.cont

    def sendUserInput(self, inputArr = [], *args):
        pkg = PyDatagram()
        pkg.addUint16(CLIENT_INPUT)
        pkg.addUint64(self.myClock)
        pkg.addBool(inputArr[0])
        pkg.addBool(inputArr[1])
        pkg.addBool(inputArr[2])
        pkg.addBool(inputArr[3])
        pkg.addBool(inputArr[4])
        pkg.addFloat32(self.heading % 360)
        # Now lets send the whole thing...
        self.send(pkg)

    def serverInputHanlder(self, msgID, data):
        serverClock = data.getUint64()
        if self.myClock == serverClock:
            while(data.getRemainingSize() != 0):
                playerId = data.getUint32()
                player = self.gameEngine.players[playerId].playerNP
                player.setX(data.getFloat32())
                player.setY(data.getFloat32())
                player.setZ(data.getFloat32())
                h = data.getFloat32()
                if(playerId != self.id):
                    # player.setH(h)
                    pass

                xSpeed = data.getFloat32()
                ySpeed = data.getFloat32()
                self.gameEngine.players[playerId].animation.animate(xSpeed, ySpeed)

            self.myClock += 1
            self.serverWait = False

    def gameInitialize(self, msgID, data):
        self.gameEngine.textObject.destroy()
        playerCount = data.getUint32()
        for i in range(0, playerCount):
            playerId = data.getUint32()
            x = data.getFloat32()
            y = data.getFloat32()
            self.gameEngine.players.append(Player(x, y, 4))
            self.gameEngine.world.attachCharacter(self.gameEngine.players[playerId].playerNP.node())
        self.gameEngine.showPointer()
        self.id = data.getUint32()
        taskMgr.add(self.update, 'update')
        self.serverWait = False

    def readTask(self, task):
        while 1:
            (datagram, data, msgID) = self.nonBlockingRead(self.cReader)
            if msgID is MSG_NONE:
                break
            else:
                self.handleDatagram(data, msgID)

        return task.cont

    def nonBlockingRead(self, qcr):
        """
        Return a datagram iterator and type if data is available on the
        queued connection reader
        """
        if self.cReader.dataAvailable():
            datagram = NetDatagram()
            if self.cReader.getData(datagram):
                data = PyDatagramIterator(datagram)
                msgID = data.getUint16()
            else:
                data = None
                msgID = MSG_NONE
        else:
            datagram = None
            data = None
            msgID = MSG_NONE
        # Note, return datagram to keep a handle on the data
        return (datagram, data, msgID)

    def handleDatagram(self, data, msgID):
        """
        Check if there's a handler assigned for this msgID.
        Since we don't have case statements in python,
        we're using a dictionary to avoid endless elif statements.
        """

        ########################################################
        ##
        ## Of course you can use as an alternative smth like this:
        ## if msgID == CMSG_AUTH: self.msgAuth(msgID, data, client)
        ## elif...

        if msgID in Handlers.keys():
            Handlers[msgID](msgID, data)
        else:
            print("Unknown msgID: %d" % msgID)
            print(data)
        return

    def sendMsgAuth(self):
        pkg = PyDatagram()
        pkg.addUint16(CMSG_AUTH)
        pkg.addString(USERNAME)
        pkg.addString(PASSWORD)
        self.send(pkg)

    def sendMsgDisconnectReq(self):
        pkg = PyDatagram()
        pkg.addUint16(CMSG_DISCONNECT_REQ)
        self.send(pkg)

    def msgAuthResponse(self, msgID, data):
        flag = data.getUint32()
        if flag == 0:
            print("Unknown user")

        if flag == 2:
            print("Wrong pass, please try again...")

        if flag == 1:
            print("Authentication Successfull")

    def msgChat(self, msgID, data):
        msg = data.getString()
        if (msg[:1] == '/'):
            msg = msg.strip('/')
            self.consoleCmdExecutor(msg)
        else:
            print(msg)

    def msgDisconnectAck(self, msgID, data):
        self.cManager.closeConnection(self.Connection)
        sys.exit()

    def send(self, pkg):
        self.cWriter.send(pkg, self.Connection)

    def quit(self):
        self.cManager.closeConnection(self.Connection)
        sys.exit()

    def consoleCmdExecutor(self,msg):
        temp = []
        temp = msg.split(' ')
        switcher = {
            'timeToStart': self.countdown,
            'begin' : self.begin            #game startwas already takken
            }
        fucn = switcher.get(temp[0],"error")
        fucn(temp[1])


    def countdown(self,value):
        self.gameEngine.textObject.setText(str(int(value)-1))

    def error(self,value):
        print("Invalid command for " + value)

    def begin(self,value):
        self.gameEngine.textObject.setText("Begin")

aClient = Client()

Handlers = {
    SMSG_AUTH_RESPONSE: aClient.msgAuthResponse,
    SMSG_CHAT: aClient.msgChat,
    SMSG_DISCONNECT_ACK: aClient.msgDisconnectAck,
    SERVER_INPUT: aClient.serverInputHanlder,
    GAME_INITIALIZE: aClient.gameInitialize,
}

if __name__ == '__main__':
    # IP = input("Enter server's IP: ")
    base.run()