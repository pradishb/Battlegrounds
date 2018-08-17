from pandac.PandaModules import *
from direct.distributed.PyDatagram import PyDatagram
from direct.showbase.InputStateGlobal import inputState

from game import ClientGameEngine
from player import Player
from raycollider import RayCollider
from gameui import GameUI
from msg_id import *
import math


class ClientGame:
    def __init__(self, network):
        self.gameEngine = ClientGameEngine()
        self.network = network
        # self.accept("escape", self.sendMsgDisconnectReq)

        self.gameStart = False
        self.my_clock = 0
        self.player_count = 0
        self.heading = 0
        self.pitch = 40
        self.skip = 0
        self.loss = 0
        self.id = 0
        self.win = False
        self.lose = False

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
    def process_input(self):
        self.gameEngine.speed.setX(0)
        self.gameEngine.speed.setY(0)
        input_list = [False] * 9
        if inputState.isSet('forward'):
            input_list[0] = True
        if inputState.isSet('left'):
            input_list[1] = True
        if inputState.isSet('reverse'):
            input_list[2] = True
        if inputState.isSet('right'):
            input_list[3] = True
        if inputState.isSet('shoot'):
            if self.gameEngine.players[self.id].weapon.get_reload():
                pos = RayCollider.getBulletHitPos()
                input_list[4] = True
                input_list[5] = pos.getX()
                input_list[6] = pos.getY()
                input_list[7] = pos.getZ()
                input_list[8] = RayCollider.playerHitId

        self.send_user_input(input_list)

    def send_user_input(self, inputArr=[], *args):
        pkg = PyDatagram()
        pkg.addUint16(CLIENT_INPUT)
        pkg.addUint64(self.my_clock)
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
        self.network.send(pkg)

    def server_input_handler(self, msgID, data):
        server_clock = data.getUint64()
        if self.my_clock == server_clock:
            alive_count = 0
            while data.getRemainingSize() != 0:
                player_id = data.getUint32()
                player = self.gameEngine.players[player_id]
                alive = data.getBool()
                if alive:
                    alive_count += 1
                    player.playerNP.setX(data.getFloat32())
                    player.playerNP.setY(data.getFloat32())
                    player.playerNP.setZ(data.getFloat32())
                    h = data.getFloat32()
                    p = data.getFloat32()
                    player.xSpeed = data.getFloat32()
                    player.ySpeed = data.getFloat32()
                    shoot = data.getBool()
                    if shoot:
                        x = data.getFloat32()
                        y = data.getFloat32()
                        z = data.getFloat32()
                        player.weapon.fire_with_pos(self.gameEngine.world, x, y, z)
                        player.animation.current = "shoot"
                    if player_id != self.id:
                        player.playerNP.setH(h)
                        player.playerSpine.setP(p)

                    player.health = data.getUint8()
                    if player_id == self.id:
                        self.healthUI.setText("Health : " + str(player.health))
                else:
                    player.health = 0
                    if not self.lose and player_id == self.id:
                        self.healthUI.setText("Health : 0")
                        self.game_over()
            if alive_count == 1 and self.gameEngine.players[self.id].health > 0 and not self.win:
                self.you_win()

            self.my_clock += 1
            self.serverWait = False

    def move_camera(self):
        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()

        if base.win.movePointer(0, 300, 300):
            self.heading = self.heading - (x - 300) * 0.2
            self.pitch = self.pitch - (y - 300) * 0.2
            if self.pitch < -45.0:
                self.pitch = -45.0
            elif self.pitch > 45.0:
                self.pitch = 45.0

        self.gameEngine.players[self.id].playerNP.lookAt(RayCollider.getBulletHitPos())
        base.cam.setHpr(self.heading, self.pitch, 0)
        base.cam.setX(self.gameEngine.players[self.id].playerNP.getX() + 2 * math.sin(
            math.pi / 180.0 * self.heading))
        base.cam.setY(self.gameEngine.players[self.id].playerNP.getY() - 2 * math.cos(
            math.pi / 180.0 * self.heading))
        base.cam.setZ(self.gameEngine.players[self.id].playerNP.getZ() - 0.03 * self.pitch + .5)
        base.cam.setPos(base.cam, .5, 0, 0)

    # Update
    def update(self, task):
        if not self.lose:
            self.move_camera()
            if not self.serverWait:
                self.process_input()
                self.gameEngine.players[self.id].weapon.update_reload_time()
                self.serverWait = True
            else:
                self.loss += 1
            # if self.myClock > 0:
            #     print("loss % =", self.loss * 100.0 / (self.loss + self.myClock))
            self.gameEngine.players[self.id].bendBody()
        dt = globalClock.getDt()
        self.gameEngine.world.doPhysics(dt)
        return task.cont

    def count_down(self, args):
        self.displayUI.setText(args[1]) if args[1] != "0" else self.displayUI.setText("Begin")

    def game_initialize(self, msgID, data):
        self.displayUI.destroy()
        self.player_count = data.getUint32()
        for i in range(0, self.player_count):
            player_id = data.getUint32()
            x = data.getFloat32()
            y = data.getFloat32()
            self.gameEngine.players.append(Player(x, y, 20, player_id))
            self.gameEngine.world.attachCharacter(self.gameEngine.players[player_id].playerNP.node())
        self.gameEngine.showPointer()
        self.id = data.getUint32()
        print(self.id)
        self.healthUI = GameUI.createWhiteBgUI("")
        self.serverWait = False
        taskMgr.add(self.update, 'update')

    def game_over(self):
        self.lose = True
        taskMgr.add(self.gameEngine.deathCamTask, "DeathCameraTask")
        self.gameEngine.myId = self.id

        gameoverDisplay = GameUI.createDisplayUI("Game Over!")

    def you_win(self):
        self.win = True
        GameUI.createDisplayUI("You Win!")
