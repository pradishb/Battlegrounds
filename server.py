from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *
import direct.directbase.DirectStart
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from direct.gui.DirectGui import *
import sys

import random 
######################################3
##
## Config
##

PORT = 9099

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


##################################################################
##
## This is just a demo how to implement Users. Of course you can
## use any other method of doing it... reading a plaintext file,
## decrypting it, using your systems users, asking a Database...
##

USERS = {
    'yellow': 'mypass',
    'tester': 'anotherpass'
}

###################################################################
##
## Creating a dictionary for the clients. Thats how we can adress
## them later on. For now they are adressed by their IP, but that
## isn't the best solution. What if 2 clients have the same IP?
## You can find of course any other working solution that will avoid
## this. Feel free to distribute it! As for the Demo its OK as is.
##

CLIENTS = {}


class Server(DirectObject):

    def __init__(self):
        ## If you press Escape @ the server window, the server will quit.
        self.accept("escape", self.quit)
        self.lastConnection = None
        self.clientInputDict = {}
        self.serverClock = 0

        self.randomValue = {}

        self.playerCount = 0
        self.listenStat = 1
        self.listPkg = PyDatagram()
        # Create network layer objects

        # Deals with the basic network stuff
        self.cManager = QueuedConnectionManager()

        # Listens for new connections and queue's them
        self.cListener = QueuedConnectionListener(self.cManager, 0)

        # Reads data send to the server
        self.cReader = QueuedConnectionReader(self.cManager, 0)

        # Writes / sends data to the client
        self.cWriter = ConnectionWriter(self.cManager, 0)

        # open a server socket on the given port. Args: (port,timeout)
        self.tcpSocket = self.cManager.openTCPServerRendezvous(PORT, 1)

        # Tell the listener to listen for new connections on this socket
        self.cListener.addConnection(self.tcpSocket)

        # Start Listener task
        taskMgr.add(self.listenTask, "serverListenTask", -40)

        # Start Read task

        taskMgr.add(self.readTask, "serverReadTask", -39)
        #taskMgr.add(self.broadcastTask, "broadcastTask")

    def listenTask(self, task):
        """
        Accept new incoming connections from the client
        """
        # Run this task after the dataLoop

        # If there's a new connection Handle it
        if (self.listenStat < 1800):
            x = 0
            y = 0
            timeToStart = 0
            ranVal = {}
            x = int(self.listenStat/60)
            if(x == (self.listenStat/60)):
                self.timeToStart = 30 -x 
                print(self.timeToStart)
                self.broadcastMsg(str(self.timeToStart))

            self.listenStat += 1 
            if self.cListener.newConnectionAvailable():
                rendezvous = PointerToConnection()
                netAddress = NetAddress()
                newConnection = PointerToConnection()

                if self.cListener.getNewConnection(rendezvous, netAddress, newConnection):
                    newConnection = newConnection.p()
                    # tell the Reader that there's a new connection to read from
                    self.cReader.addConnection(newConnection)
                    CLIENTS[newConnection] = netAddress.getIpString()
                    self.lastConnection = newConnection
                    print("Got a connection!")
                    self.playerCount += 1 
                else:
                    print("getNewConnection returned false")
            #creating random value for clients
        return task.cont

    def readTask(self, task):
        """
        If there's any data received from the clients,
        get it and send it to the handlers.
        """
        while 1:
            (datagram, data, msgID) = self.nonBlockingRead(self.cReader)
            if msgID is MSG_NONE:
                # got nothing todo
                break
            else:
                # Got a datagram, handle it
                self.handleDatagram(data, msgID, datagram.getConnection())

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

    def handleDatagram(self, data, msgID, client):
        """
        Check if there's a handler assigned for this msgID.
        Since we dont have case statements in python,
        I'm using a dictionary to avoid endless elif statements.
        """

        ########################################################
        ##
        ## Of course you can use as an alternative smth like this:
        ## if msgID == CMSG_AUTH: self.msgAuth(msgID, data, client)
        ## elif...

        if msgID in Handlers.keys():
            Handlers[msgID](msgID, data, client)
        else:
            print("Unknown msgID: %d" % msgID)
            print(data)
        return

    def msgAuth(self, msgID, data, client):

        #########################################################
        ##
        ## Okay... The client sent us some Data. We need to extract
        ## the data the same way it was placed into the buffer.
        ## Its like "first in, first out"
        ##

        username = data.getString()
        password = data.getString()

        ## Now that we have the username and pwd, we need to
        ## determine if the client has the right user/pwd-combination.
        ## this variable will be sent later to the client, so lets
        ## create/define it here.
        flag = None

        if not username in USERS.keys():
            # unknown user
            ## That 0 is going to be sent later on. The client knows with
            ## that 0 that the username was not allowed.
            flag = 0
        elif USERS[username] == password:
            # authenticated, come on in
            flag = 1
            # CLIENTS[username] = 1
            print("User: %s, logged in with pass: %s" % (username, password))
        else:
            # Wrong password, try again or bugger off
            flag = 2

        ## again... If you have read the client.py first, you know what
        ## I want to say. Do not use this type in a productive system.
        ## If you want to use it, just define 0 and 1.
        ## 1 -> Auth OK
        ## 0 -> Username/Password combination not correct.
        ## Otherwise its far too easy to get into the system...

        ## Creating a buffer to hold the data that is going to be sent.
        pkg = PyDatagram()

        ## The first Bytes we send to the client in that paket will be
        ## the ones that classify them as what they are. Here they mean
        ## "Hi Client! I am an Auth Response from the server."
        ## How does the client know that? Well, because both have a
        ## definition saying "SMSG_AUTH_RESPONSE  = 2"
        ## Due to shorter Network Pakets Yellow used Numbers instead
        ## of the whole Name. So you will see a 2 in the paket if you
        ## catch it somewhere...
        pkg.addUint16(SMSG_AUTH_RESPONSE)

        ## Now we are sending, if the auth was
        ## successfull ("1") or not ("0" or "2")
        pkg.addUint32(flag)

        ## Now lets send the whole story...
        self.cWriter.send(pkg, client)

    def msgChat(self, msgID, data, client):

        #########################################################
        ##
        ## This is again only an example showing you what you CAN
        ## do with the received code... Example: Sending it back.
        # print 'ChatMsg: ',chatMsg

        ## If you have trouble with the print command:
        ## print 'ChatMsg: ',data.GetString() does the same.
        ## Attention! The (partial) content of "data" is lost after the
        ## first getString()!!!
        ## If you want to test the above example, comment the
        ## next line out...

        print("ChatMsg: %s" % data.getString())

    def msgDisconnectReq(self, msgID, data, client):
        pkg = PyDatagram()
        pkg.addUint16(SMSG_DISCONNECT_ACK)
        self.cWriter.send(pkg, client)
        del CLIENTS[client]
        self.cReader.removeConnection(client)

    def quit(self):
        self.cManager.closeConnection(self.tcpSocket)
        sys.exit()

    def clientInputHandler(self, msgID, data, client):
        
        w = data.getBool()
        a = data.getBool()
        s = data.getBool()
        d = data.getBool()
        space = data.getBool()
        self.val = [w,a,s,d,space]
        self.clientInputDict[client] = self.val
        pkg = PyDatagram()
        pkg.addUint16(SERVER_INPUT)
        pkg.addBool(w)
        pkg.addBool(a)
        pkg.addBool(s)
        pkg.addBool(d)
        pkg.addBool(space)
        self.cWriter.send(pkg,client)

    def broadcastTask(self, task):
        print("Broadcasting. Server Clock = " + str(self.serverClock))
        # for c in CLIENTS:
        #     print(c)
        # pkg = PyDatagram()
        self.serverClock += 1
        print()
        return task.cont

    #sabai krua boardcasting garnae ko lagi ho 
    def broadcastMsg(self, msg):
        pkg = PyDatagram()
        pkg.addUint16(SMSG_CHAT)
        pkg.addString(msg)
        # print(CLIENTS)
        for c in CLIENTS:
            # print(c)
            self.cWriter.send(pkg,c)

    #to send game's initial stats
    def gameStart(self):
        playerId = 0
        ranValPkg = PyDatagram()
        ranValPkg.addUint16(SMSG_CHAT)
        ranValPkg.addUint32(self.playerCount) 
        for client in CLIENTS:
            ranValPkg.addString(client)
            ranValPkg.addUint16(player_id)
            ranValPkg.addfloat(random.randint(1,5))
            ranValPkg.addfloat(random.randint(1,5))
            playerId += playerId
        for client in CLIENTS:
            self.cWriter.send(self,ranValPkg,client)

# create a server object on port 9099
serverHandler = Server()

# install msg handlers
## For detailed information see def handleDatagram(self, data, msgID, client):
Handlers = {
    CMSG_AUTH: serverHandler.msgAuth,
    CMSG_CHAT: serverHandler.msgChat,
    CMSG_DISCONNECT_REQ: serverHandler.msgDisconnectReq,
    CLIENT_INPUT: serverHandler.clientInputHandler,
}

base.run()