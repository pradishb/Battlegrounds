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
        self.count_down_time = 0

        self.client_received_list = []
        self.listPkg = PyDatagram()
        self.clientInputList = PyDatagram()
        self.clientInputList.addUint16(SERVER_INPUT)
        self.clientInputList.addUint64(self.serverClock)
        self.clientsAlive = []
        self.clientsDead = []
        self.display_text = GameUI.createDisplayUI("Loading...")
        self.count = 0

    def count_down_start(self):
        taskMgr.doMethodLater(1.0, self.count_down, 'Count Down')
        # taskMgr.doMethodLater(1.0, self.debug_count, 'Debug Count')

    def count_down(self, task):
        if self.count_down_time == -1:
            taskMgr.remove('Count Down')
            self.network.handlers[CLIENT_INPUT] = self.client_input_handler
            self.game_start()
        else:
            self.network.broadcastMsg("/count_down " + str(self.count_down_time))
            self.display_text.setText(str(self.count_down_time))
            self.count_down_time -= 1
        return task.again

    def debug_count(self, task):
        print(self.count)
        self.count = 0
        return task.again

    # to send game's initial stats
    def game_start(self):
        base.oobe()
        self.display_text.setText("Begin")
        pkg = PyDatagram()
        pkg.addUint16(GAME_INITIALIZE)
        pkg.addUint32(self.network.playerCount)
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
        self.clientsAlive = self.network.CLIENTS_ID.copy()
        self.display_text.destroy()

    def client_input_handler(self, msgID, data, client):
        found = False
        client_clock = data.getUint64()
        # print('my time is', self.serverClock, 'client clock is', clientClock)
        if client_clock == self.serverClock:
            for c in self.client_received_list:
                if c == client:
                    found = True
                    break
            if not found:
                self.client_received_list.append(client)
                player = self.gameEngine.players[self.network.RELATION_OBJ_ID[client]]

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
                    player_hit_id = data.getString()
                    if player_hit_id != "None":
                        player_hit_id = int(player_hit_id)
                        self.gameEngine.players[player_hit_id].health -= 30
                        if self.gameEngine.players[player_hit_id].health <= 0:
                            self.gameEngine.players[player_hit_id].health = 0
                            if player_hit_id in self.clientsAlive:
                                self.clientsAlive.pop(player_hit_id)
                                self.clientsDead.append(player_hit_id)
                    player.weapon.fire_with_pos(self.gameEngine.world, x, y, z)
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

                self.clientInputList.addUint32(self.network.RELATION_OBJ_ID[client])
                self.clientInputList.addBool(True)
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
                self.broadcast_task()

    def broadcast_task(self):
        if self.client_received_list.__len__() >= self.clientsAlive.__len__():
            # print("Broadcasting. Server Clock = " + str(self.serverClock))
            for c in self.network.CLIENTS_ID:
                self.network.cWriter.send(self.clientInputList, self.network.RELATION_OBJ_ID[c])
            self.serverClock += 1
            self.clientInputList = PyDatagram()
            self.clientInputList.addUint16(SERVER_INPUT)
            self.clientInputList.addUint64(self.serverClock)
            for client_id in self.clientsDead:
                self.clientInputList.addUint32(client_id)
                self.clientInputList.addBool(False)
            self.client_received_list.clear()
            self.update()
        else:
            pass
            # print("Waiting for all inputs. Server Clock = " +
            #       str(self.serverClock), "remaining users = " +
            #       str(self.clientsAlive.__len__() - self.client_received_list.__len__()))

    # Update
    def update(self):
        dt = globalClock.getDt()
        self.gameEngine.world.doPhysics(dt)
