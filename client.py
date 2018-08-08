from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *
import direct.directbase.DirectStart
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

import direct.directbase.DirectStart
from direct.showbase.InputStateGlobal import inputState
from direct.showbase.DirectObject import DirectObject
from panda3d.core import Vec3, BitMask32, GeoMipTerrain, AmbientLight, Vec4, DirectionalLight, Filename, PNMImage
from panda3d.bullet import BulletWorld, BulletCapsuleShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletHeightfieldShape
from panda3d.bullet import ZUp
from panda3d.bullet import BulletCharacterControllerNode
from direct.actor.Actor import Actor, WindowProperties
from direct.gui.OnscreenImage import LineSegs, deg2Rad, NodePath
import math
import sys


from direct.gui.DirectGui import *
######################################3
##
## Config
##

IP = '127.0.0.1'
PORT = 9099
USERNAME = "yellow"
PASSWORD = "mypass"

######################################3
##
## Defines
##
## Quote Yellow: This are server opcodes. It tells the server
## or client what pkt it is receiving. Ie if the pkt starts
## with 3, the server knows he has to deal with a chat msg



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

class Player():
    def __init__(self, x, y, z):
        shape = BulletCapsuleShape(.2, .6, ZUp)
        self.playerNode = BulletCharacterControllerNode(shape, 0.4, 'Player')
        self.playerNode.setMaxJumpHeight(2.0)
        self.playerNode.setJumpSpeed(4.0)
        self.playerNP = render.attachNewNode(self.playerNode)
        self.playerNP.setPos(x, y, z)
        self.playerNP.setCollideMask(BitMask32.allOn())
        self.playerModel = Actor('models/soldier.egg', {"idle": "models/soldier_ani_idle.egg",
                                                        "walk": "models/soldier_ani_walk.egg"})
        myTexture = loader.loadTexture("models/soldier_texture.png")
        self.playerModel.setTexture(myTexture, 1)
        self.playerModel.setH(90)
        self.playerModel.setScale(.06)
        self.playerModel.setZ(-.45)
        self.playerModel.flattenLight()
        self.playerModel.setLightOff()
        self.playerModel.reparentTo(self.playerNP)

class GameEngine():
    def initCam(self):
        base.cam.setHpr(-40, -40, 0)
        base.cam.setPos(-25, -30, 30)


class Client(DirectObject):
    def __init__(self):
        ge = GameEngine()
        ge.initCam()
        self.accept("escape", self.sendMsgDisconnectReq)

        self.gameStart = False
        # Create network layer objects
        ## This is madatory code. Don't ask for now, just use it ;)
        ## If something is unclear, just ask.
        base.setFrameRateMeter(True)
        self.accept('f1', self.toggleDebug)
        self.accept('escape', sys.exit, [0])

        self.debugNode = BulletDebugNode('Debug')
        self.debugNode.showWireframe(True)
        self.debugNode.showConstraints(True)
        self.debugNode.showBoundingBoxes(False)
        self.debugNode.showNormals(False)
        self.debugNP = render.attachNewNode(self.debugNode)
        self.debugNP.show()

        # Light
        self.alight = AmbientLight('ambientLight')
        self.alight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        self.alightNP = render.attachNewNode(self.alight)

        self.dlight = DirectionalLight('directionalLight')
        self.dlight.setDirection(Vec3(1, 1, -1))
        self.dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
        self.dlightNP = render.attachNewNode(self.dlight)

        render.clearLight()
        render.setLight(self.alightNP)
        render.setLight(self.dlightNP)

        # World
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debugNP.node())

        # HeightField
        self.height = 8.0
        self.img = PNMImage(Filename('models/elevation.png'))
        self.hshape = BulletHeightfieldShape(self.img, self.height, ZUp)
        self.hnode = BulletRigidBodyNode('HGround')
        self.hnode.addShape(self.hshape)
        self.world.attachRigidBody(self.hnode)

        # Terrian
        terrain = GeoMipTerrain('terrain')
        terrain.setHeightfield(self.img)

        offset = self.img.getXSize() / 2.0 - 0.5
        rootNP = terrain.getRoot()
        rootNP.reparentTo(render)
        rootNP.setSz(self.height)
        rootNP.setPos(-offset, -offset, -self.height / 2.0)
        terrain.generate()

        self.speed = Vec3(0, 0, 0)
        self.walk_speed = 1.5

        self.players = []

        # Camera
        base.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)
        self.heading = 0
        self.pitch = 40

        # Pointer
        # imageObject = self.makeArc()
        # imageObject.setSx(.02)
        # imageObject.setSy(.02)
        # imageObject.setSz(.02)
        # imageObject.reparent_to(aspect2d)

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
        self.cReader.addConnection(self.Connection)

        # Start tasks
        taskMgr.add(self.readTask, "serverReaderPollTask", -39)

        # Send login msg to the server
        ## required to get the whole thing running.
        self.sendMsgAuth()
        self.serverWait = False

    ########################################
    ##
    ## Addition:
    ## If in doubt, don't change the following. Its working.
    ## Here are the basic networking code pieces.
    ## If you have questions, ask...
    ##
    # player movement

    def processInput(self):
        self.speed.setX(0)
        self.speed.setY(0)

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
            # playerNode.doJump()
            inputList[4] = True
        self.sendUserInput(inputList)

    # player animation
    def animate(self):
        for player in self.players:
            if (self.speed.getX() == 0 and self.speed.getY() == 0):
                if (player.playerModel.get_current_anim() != "idle"):
                    player.playerModel.loop("idle")
            else:
                if (player.playerModel.get_current_anim() != "walk"):
                    player.playerModel.loop("walk")

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

        base.cam.setHpr(self.heading, self.pitch, 0)

        self.players[self.id].playerNP.setH(self.heading)
        base.cam.setX(self.players[self.id].playerNP.getX() + 3 * math.sin(math.pi / 180.0 * self.players[self.id].playerNP.getH()))
        base.cam.setY(self.players[self.id].playerNP.getY() - 3 * math.cos(math.pi / 180.0 * self.players[self.id].playerNP.getH()))
        base.cam.setZ(self.players[self.id].playerNP.getZ() - 0.05 * self.pitch + .7)

    # Update
    def update(self, task):
        dt = globalClock.getDt()
        self.moveCamera()
        if(not self.serverWait):
            self.processInput()
            self.animate()
            self.world.doPhysics(dt)
            self.serverWait = True
        return task.cont

    def makeArc(angleDegrees=360, numSteps=16):
        ls = LineSegs()

        angleRadians = deg2Rad(angleDegrees)

        for i in range(numSteps + 1):
            a = angleRadians * i / numSteps
            y = math.sin(a)
            x = math.cos(a)

            ls.drawTo(x, 0, y)

        node = ls.create()
        return NodePath(node)

    # Debug
    def toggleDebug(self):
        if self.debugNP.isHidden():
            self.debugNP.show()
        else:
            self.debugNP.hide()

    def sendUserInput(self, inputArr = [], *args):
        pkg = PyDatagram()

        pkg.addUint16(CLIENT_INPUT)

        # pkg.addString("hehehe")
        # print(inputArr[0])
        # val = phaser(inputArr[0], inputArr[1], inputArr[2], inputArr[3], inputArr[4])
        pkg.addBool(inputArr[0])
        pkg.addBool(inputArr[1])
        pkg.addBool(inputArr[2])
        pkg.addBool(inputArr[3])
        pkg.addBool(inputArr[4])

        # Now lets send the whole thing...
        self.send(pkg)

    def serverInputHanlder(self, msgID, data):
        if(data.getRemainingSize() != 0):
            playerId = data.getUint32()
            if data.getBool():
                self.speed.setY(self.walk_speed)
            if data.getBool():
                self.speed.setX(-self.walk_speed)
            if data.getBool():
                self.speed.setY(-self.walk_speed)
            if data.getBool():
                self.speed.setX(self.walk_speed)
            if data.getBool():
                print()
                # playerNode.doJump()
            self.players[playerId].playerNP.node().setLinearMovement(self.speed, True)
        self.serverWait = False

    def gameInitialize(self, msgID, data):
        playerCount = data.getUint32()
        for i in range(0, playerCount):
            playerId = data.getUint32()
            x = data.getFloat32()
            y = data.getFloat32()
            self.players.append(Player(x, y, 4))
            self.world.attachCharacter(self.players[i].playerNP.node())
        self.id = data.getUint32()
        taskMgr.add(self.update, 'update')

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

        #########################################################
        ##
        ## This handles the sending of the auth request.
        ##

        ## 1st. We need to create a buffer 

        pkg = PyDatagram()

        ## 2nd. We put a UInt16 type Number in it. Here its CMSG_AUTH
        ## what means that the corresponding Value is "1"
        pkg.addUint16(CMSG_AUTH)

        ## 3rd. We add the username to the buffer after the UInt.
        pkg.addString(USERNAME)

        ## 4th. We add the password for the username after the username
        pkg.addString(PASSWORD)

        ## Now that we have a Buffer consisting of a Number and 2 Strings
        ## we can send it.
        self.send(pkg)

    def sendMsgDisconnectReq(self):
        #####################################################
        ##
        ## This is not used right now, but can be used to tell the
        ## server that the client is disconnecting cleanly.
        ##
        pkg = PyDatagram()

        ## Will be a short paket... we are just sending
        ## the Code for disconnecting. The server doesn't
        ## need more information anyways...
        pkg.addUint16(CMSG_DISCONNECT_REQ)
        self.send(pkg)

    def msgAuthResponse(self, msgID, data):

        ##################################################
        ##
        ## Here we are going to compare the auth response
        ## we got from the server. Yellow kept it short, but
        ## if the server sends a 0 here, it means, the User
        ## doesn't exist. 1 means: user/pwd combination
        ## successfull. If the server sends a 2: Wrong PWD.
        ## Note that its a security risk to do so. That way
        ## you can easily spy for existing users and then
        ## check for their passwords, but its a good example
        ## to show, how what is working.

        flag = data.getUint32()
        if flag == 0:
            print("Unknown user")

        if flag == 2:
            print("Wrong pass, please try again...")

        if flag == 1:
            print("Authentication Successfull")

    def msgChat(self, msgID, data):

        ##########################################################
        ##
        ## Here comes the interaction with the data sent from the server...
        ## Due to the fact that the server does not send any data the
        ## client could display, its only here to show you how it COULD
        ## be used. Of course you can do anything with "data". The
        ## raw print to console should only show a example.
        ##

        print(data.getString())

    def msgDisconnectAck(self, msgID, data):

        ###########################################################
        ##
        ## If the server sends a "close" command to the client, this
        ## would be handled here. Due to the fact that he doesn't do
        ## that, its just another example that does show what would
        ## be an example about how to do it. I would be careful with
        ## the example given here... In that case everything a potential
        ## unfriendly person needs to do is sending you a paket with a
        ## 6 in it coming from the server (not sure if it even needs to
        ## be from the server) the application will close... You might
        ## want to do a double checking with the server again to ensure
        ## that he sent you the paket... But thats just a advice ;)
        ##

        ## telling the Manager to close the connection
        self.cManager.closeConnection(self.Connection)

        ## saying good bye
        sys.exit()

    def send(self, pkg):
        self.cWriter.send(pkg, self.Connection)

    def quit(self):
        self.cManager.closeConnection(self.Connection)
        sys.exit()



######################################################################
##
## OK! After all of this preparation lets create a Instance of the
## Client Class created above. Call it as you wish. Make sure that you
## use the right Instance name in the dictionary "Handlers" as well...
##

aClient = Client()

######################################################################
##
## That is the second piece of code from the
## def handleDatagram(self, data, msgID): - Method. If you have
## trouble understanding this, please ask.
##

Handlers = {
    SMSG_AUTH_RESPONSE: aClient.msgAuthResponse,
    SMSG_CHAT: aClient.msgChat,
    SMSG_DISCONNECT_ACK: aClient.msgDisconnectAck,
    SERVER_INPUT: aClient.serverInputHanlder,
    GAME_INITIALIZE: aClient.gameInitialize,
}

#######################################################################
##
## As Examples for other Instance names:
##
## justAExample = Client()
##
## Handlers = {
##    SMSG_AUTH_RESPONSE  : justAExample.msgAuthResponse,
##    SMSG_CHAT           : justAExample.msgChat,
##    SMSG_DISCONNECT_ACK : justAExample.msgDisconnectAck,
##    }


########################################################################
##
## We need that loop. Otherwise it would run once and then quit.
##

base.run()
