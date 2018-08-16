import random

from direct.distributed.PyDatagram import PyDatagram

from game import GameEngine
from player import Player
from gameui import GameUI
from msg_id import *


class ServerGame:

    def __init__(self, network):
        self.gameEngine = GameEngine()
        self.network = network

        self.lastConnection = None
        self.serverClock = 0
        self.lobbyWaitTime = 6
        self.randomValue = {}

        self.playerCount = 0
        self.listenStat = 1
        self.listPkg = PyDatagram()
        self.clientInputList = PyDatagram()
        self.clientInputList.addUint16(SERVER_INPUT)
        self.clientInputList.addUint64(self.serverClock)
        self.clientsAlive = {}

        self.displayText = GameUI.createDisplayUI("Loading...")

    # to send game's initial stats
    def game_start(self):
        self.displayText.setText("Begin")
        pkg = PyDatagram()
        pkg.addUint16(GAME_INITIALIZE)
        pkg.addUint32(self.playerCount)
        for client_id in self.network.CLIENTS_ID:
            x = random.randint(1, 5)
            y = random.randint(1, 5)
            self.gameEngine.players.append(Player(x, y, 20, client_id))
            self.gameEngine.world.attachCharacter(self.gameEngine.players[client_id].playerNP.node())
            pkg.addUint32(client_id)
            pkg.addFloat32(x)
            pkg.addFloat32(y)
        for client_id in self.network.CLIENTS_ID:
            temp = pkg.__copy__()
            temp.addUint32(client_id)
            self.network.cWriter.send(temp, self.network.RELATION_OBJ_ID[client_id])
        # taskMgr.add(self.update, 'update')
        self.displayText.destroy()

    def client_input_handler(self, msgID, data, client):
        found = False
        client_clock = data.getUint64()
        # print('my time is', self.serverClock, 'client clock is', clientClock)
        if client_clock == self.serverClock:
            for c in CLIENT_INPUT_RECEIVED:
                if c == client:
                    found = True
                    break
            if not found:
                CLIENT_INPUT_RECEIVED.append(client)
                player = self.gameEngine.players[CLIENTS_ID[client]]

                x, y, z = 0, 0, 0
                w = data.getBool()
                a = data.getBool()
                s = data.getBool()
                d = data.getBool()
                shoot = data.getBool()
                if shoot:
                    x = data.getFloat32()
                    y = data.getFloat32()
                    z = data.getFloat32()
                    playerHitId = data.getString()
                    if playerHitId != "None":
                        playerHitId = int(playerHitId)
                        self.gameEngine.players[playerHitId].health -= 30
                        if self.gameEngine.players[playerHitId].health <= 0:
                            self.gameEngine.players[playerHitId].health = 0
                            if playerHitId in self.clientsAlive:
                                self.clientsAlive.pop(playerHitId)
                    player.weapon.fireWithPos(self.gameEngine.world, x, y, z)
                h = data.getFloat32()
                p = data.getFloat32()

                if w:
                    self.gameEngine.speed.setY(self.gameEngine.walk_speed)
                if a:
                    self.gameEngine.speed.setX(-self.gameEngine.walk_speed)
                if s:
                    self.gameEngine.speed.setY(-self.gameEngine.walk_speed)
                if d:
                    self.gameEngine.speed.setX(self.gameEngine.walk_speed)

                player.playerNP.setH(h)
                player.playerSpine.setP(p)
                player.playerNP.node().setLinearMovement(self.gameEngine.speed, True)

                self.clientInputList.addUint32(CLIENTS_ID[client])
                self.clientInputList.addFloat32(player.playerNP.getX())
                self.clientInputList.addFloat32(player.playerNP.getY())
                self.clientInputList.addFloat32(player.playerNP.getZ())
                self.clientInputList.addFloat32(player.playerNP.getH())
                self.clientInputList.addFloat32(player.playerSpine.getP())
                self.clientInputList.addFloat32(self.gameEngine.speed.getX())
                self.clientInputList.addFloat32(self.gameEngine.speed.getY())
                self.clientInputList.addBool(shoot)
                if shoot:
                    self.clientInputList.addFloat32(x)
                    self.clientInputList.addFloat32(y)
                    self.clientInputList.addFloat32(z)
                self.clientInputList.addUint8(player.health)
                self.gameEngine.speed.setX(0)
                self.gameEngine.speed.setY(0)

    def broadcastTask(self, task):
        if CLIENT_INPUT_RECEIVED.__len__() >= self.clientsAlive.__len__():
            # print("Broadcasting. Server Clock = " + str(self.serverClock))
            for c in CLIENTS:
                self.cWriter.send(self.clientInputList, c)

            self.serverClock += 1
            self.X = self.Y = 0
            self.clientInputList = PyDatagram()
            self.clientInputList.addUint16(SERVER_INPUT)
            self.clientInputList.addUint64(self.serverClock)
            CLIENT_INPUT_RECEIVED.clear()
            if self.clientsAlive.__len__() == 1:
                self.broadcastMsg("/game_end " + str(self.clientsAlive.popitem()[0]))
        else:
            pass
            # print("Waiting for all inputs. Server Clock = " +
            #       str(self.serverClock), "remaining users = " +
            #       str(self.clientsAlive.__len__() - CLIENT_INPUT_RECEIVED.__len__()))

        return task.cont

    # Update
    def update(self, task):
        dt = globalClock.getDt()
        self.gameEngine.world.doPhysics(dt)
        return task.cont
