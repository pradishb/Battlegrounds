from pandac.PandaModules import *
from direct.distributed.PyDatagram import PyDatagram
from direct.showbase.InputStateGlobal import inputState

from game import ClientGameEngine
from player import Player
from raycollider import RayCollider
from gameui import GameUI
import math


class ClientGame:
    def __init__(self, network):
        self.gameEngine = ClientGameEngine()
        self.network = network
        # self.accept("escape", self.sendMsgDisconnectReq)

        self.gameStart = False
        self.myClock = 0
        self.heading = 0
        self.pitch = 40
        self.skip = 0
        self.loss = 0
        self.id = 0

        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('left', 'a')
        inputState.watchWithModifiers('reverse', 's')
        inputState.watchWithModifiers('right', 'd')
        inputState.watchWithModifiers('shoot', 'mouse1')

        # GameUI
        self.healthUI = None
        self.displayUI = GameUI.createDisplayUI("")

        self.serverWait = True

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
                    player.weapon.fireWithPos(self.gameEngine.world, x, y, z)
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

    def game_end(self, value):
        if int(value) == self.id:
            GameUI.createDisplayUI("You Win!")

