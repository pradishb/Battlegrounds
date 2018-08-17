from direct.showbase.ShowBase import ShowBase
from panda3d.bullet import ZUp
from pandac.PandaModules import *
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.showbase.InputStateGlobal import inputState

from game import ClientGameEngine
from player import Player
from raycollider import RayCollider
from gameui import GameUI
from direct_gui import ClientGui
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

    # player inputs
    def processInput(self):
        self.gameEngine.speed.setX(0)
        self.gameEngine.speed.setY(0)
        inputList = [False] * 9
        if inputState.isSet('forward'):
            inputList[0] = True
        if inputState.isSet('left'):
            inputList[1] = True
        if inputState.isSet('reverse'):
            inputList[2] = True
        if inputState.isSet('right'):
            inputList[3] = True
        if inputState.isSet('shoot'):
            if self.gameEngine.players[self.id].weapon.get_reload():
                pos = RayCollider.getBulletHitPos()
                inputList[4] = True
                inputList[5] = pos.getX()
                inputList[6] = pos.getY()
                inputList[7] = pos.getZ()
                inputList[8] = RayCollider.playerHitId

        self.sendUserInput(inputList)

    def sendUserInput(self, inputArr = [], *args):
        pkg = PyDatagram()
        pkg.addUint16(CLIENT_INPUT)
        pkg.addUint64(self.myClock)
        pkg.addBool(inputArr[0])
        pkg.addBool(inputArr[1])
        pkg.addBool(inputArr[2])
        pkg.addBool(inputArr[3])
        pkg.addBool(inputArr[4])
        if inputArr[4]:
            pkg.addFloat32(inputArr[5])
            pkg.addFloat32(inputArr[6])
            pkg.addFloat32(inputArr[7])
            pkg.addString(str(inputArr[8]))
        pkg.addFloat32(self.gameEngine.players[self.id].playerNP.getH() % 360)
        pkg.addFloat32(self.gameEngine.players[self.id].playerSpine.getP() % 360)
        # Now lets send the whole thing...
        self.send(pkg)

    def serverInputHanlder(self, msgID, data):
        serverClock = data.getUint64()
        if self.myClock == serverClock:
            while(data.getRemainingSize() != 0):
                playerId = data.getUint32()
                player = self.gameEngine.players[playerId]
                player.playerNP.setX(data.getFloat32())
                player.playerNP.setY(data.getFloat32())
                player.playerNP.setZ(data.getFloat32())
                h = data.getFloat32()
                p = data.getFloat32()
                player.xSpeed = data.getFloat32()
                player.ySpeed = data.getFloat32()
                shoot = data.getBool()
                x, y, z = 0, 0, 0
                if shoot:
                    x = data.getFloat32()
                    y = data.getFloat32()
                    z = data.getFloat32()
                    player.weapon.fire_with_pos(self.gameEngine.world, x, y, z)
                    player.animation.current = "shoot"
                if playerId != self.id:
                    player.playerNP.setH(h)
                    player.playerSpine.setP(p)

                player.health = data.getUint8()
                if playerId == self.id:
                    self.healthUI.setText("Health : " + str(player.health))
                    if player.health == 0:
                        self.gameover()

            self.myClock += 1
            self.serverWait = False

    def moveCamera(self):
        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()

        if base.win.movePointer(0, 300, 300):
            self.heading = self.heading - (x - 300) * 0.2
            self.pitch = self.pitch - (y - 300) * 0.2
            if (self.pitch < -45.0):
                self.pitch = -45.0
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
        if not self.serverWait:
            self.processInput()
            self.gameEngine.players[self.id].weapon.update_reload_time()
            self.serverWait = True
        else:
            self.loss += 1
        # if self.myClock > 0:
        #     print("loss % =", self.loss * 100.0 / (self.loss + self.myClock))
        dt = globalClock.getDt()
        self.gameEngine.players[self.id].bendBody()
        self.gameEngine.world.doPhysics(dt)
        return task.cont

    def gameInitialize(self, msgID, data):
        self.displayUI.destroy()
        playerCount = data.getUint32()
        for i in range(0, playerCount):
            playerId = data.getUint32()
            x = data.getFloat32()
            y = data.getFloat32()
            self.gameEngine.players.append(Player(x, y, 20, playerId))
            self.gameEngine.world.attachCharacter(self.gameEngine.players[playerId].playerNP.node())
        self.gameEngine.showPointer()
        self.id = data.getUint32()
        self.healthUI = GameUI.createWhiteBgUI("")
        self.serverWait = False
        taskMgr.add(self.update, 'update')

    def gameover(self):
        taskMgr.remove('update')
        taskMgr.add(self.gameEngine.deathCamTask, "DeathCameraTask")
        self.gameEngine.myId = self.id

        gameoverDisplay = GameUI.createDisplayUI("Game Over!")


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
            print("Authentication Successful")

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
        temp = msg.split(' ')
        switcher = {
            'timeToStart': self.countdown,
            'game_end': self.game_end,
            'info': self.info,
            }
        fucn = switcher.get(temp[0], "invalid")
        fucn(temp[1])

    def countdown(self, value):
        self.displayUI.setText(value)

    def invalid(self, value):
        GameUI.createWhiteBgUI("Invalid command for " + value)

    def info(self, value):
        if value == "no_clients":
            GameUI.createWhiteBgUI("Not enough clients connected.")
            self.displayUI.destroy()

    def game_end(self, value):
        if int(value) == self.id:
            GameUI.createDisplayUI("You Win!")

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