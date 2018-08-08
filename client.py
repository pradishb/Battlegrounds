from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.showbase.InputStateGlobal import inputState
from panda3d.bullet import BulletDebugNode
from direct.gui.OnscreenImage import LineSegs, deg2Rad, NodePath

from direct.gui.OnscreenText import OnscreenText

from game import Player, GameEngine
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
        self.gameEngine = GameEngine()
        self.gameEngine.initCam()
        self.accept("escape", self.sendMsgDisconnectReq)

        self.gameStart = False
        self.myClock = 0
        self.heading = 0
        self.pitch = 40
        # Create network layer objects
        ## This is madatory code. Don't ask for now, just use it ;)
        ## If something is unclear, just ask.
        self.accept('f1', self.toggleDebug)
        self.accept('escape', sys.exit, [0])

        self.debugNode = BulletDebugNode('Debug')
        self.debugNode.showWireframe(True)
        self.debugNode.showConstraints(True)
        self.debugNode.showBoundingBoxes(False)
        self.debugNode.showNormals(False)
        self.debugNP = render.attachNewNode(self.debugNode)
        self.debugNP.show()
        self.gameEngine.world.setDebugNode(self.debugNP.node())

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

        taskMgr.add(self.readTask, "serverReaderPollTask", -39)

        self.sendMsgAuth()
        self.serverWait = False

    # player movement

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
            # playerNode.doJump()
            inputList[4] = True
        self.sendUserInput(inputList)

    # player animation
    def animate(self):
        for player in self.gameEngine.players:
            if (self.gameEngine.speed.getX() == 0 and self.gameEngine.speed.getY() == 0):
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

    # Update
    def update(self, task):
        dt = globalClock.getDt()
        self.moveCamera()
        if(not self.serverWait):
            self.processInput()
            self.animate()
            self.gameEngine.world.doPhysics(dt)
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
                if data.getBool():
                    self.gameEngine.speed.setY(self.gameEngine.walk_speed)
                if data.getBool():
                    self.gameEngine.speed.setX(-self.gameEngine.walk_speed)
                if data.getBool():
                    self.gameEngine.speed.setY(-self.gameEngine.walk_speed)
                if data.getBool():
                    self.gameEngine.speed.setX(self.gameEngine.walk_speed)
                if data.getBool():
                    print()
                    # playerNode.doJump()
                h = data.getFloat32()
                self.gameEngine.players[playerId].playerNP.setH(h)
                self.gameEngine.players[playerId].playerNP.node().setLinearMovement(self.gameEngine.speed, True)

            base.cam.setHpr(self.heading, self.pitch, 0)
            base.cam.setX(self.gameEngine.players[self.id].playerNP.getX() + 3 * math.sin(
                math.pi / 180.0 * self.gameEngine.players[self.id].playerNP.getH()))
            base.cam.setY(self.gameEngine.players[self.id].playerNP.getY() - 3 * math.cos(
                math.pi / 180.0 * self.gameEngine.players[self.id].playerNP.getH()))
            base.cam.setZ(self.gameEngine.players[self.id].playerNP.getZ() - 0.05 * self.pitch + .7)
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
            self.gameEngine.world.attachCharacter(self.gameEngine.players[i].playerNP.node())
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
        msg = data.getString()
        if (msg[:1] == '/'):
            msg = msg.strip('/')
            self.consoleCmdExecutor(msg)
        else:
            print(msg)

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
        #x = 
        #try:
        #    switch():
        #     switch(TimeUntilStart):
        #except nosuchcommandexpet:
        #    print
        #except Exception as e:
        #    print(e)


        #print(Invalid h)
        ##consoleCmdExecutor()
        #throw ene
        #self.gameEngine.textObject.setText(msg)
        


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
if __name__ == '__main__':
    # IP = input("Enter server's IP: ")
    base.run()