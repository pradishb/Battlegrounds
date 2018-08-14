from direct.distributed.PyDatagram import PyDatagram
from pandac.PandaModules import *
from direct.distributed.PyDatagramIterator import PyDatagramIterator

PORT = 9099

MSG_NONE = 0
CMSG_INFO = 1
SMSG_INFO = 2
CMSG_CHAT = 3
SMSG_CHAT = 4
CMSG_DISCONNECT_REQ = 5
SMSG_DISCONNECT_ACK = 6
CLIENT_INPUT = 7
SERVER_INPUT = 8
GAME_INITIALIZE = 9

CLIENTS = {}
CLIENTS_ID = {}
CLIENTS_USER_NAMES = {}
CLIENT_INPUT_RECEIVED = []


class ServerNetwork:
    def __init__(self, gui):
        self.gui = gui
        self.playerCount = 0
        self.clientsAlive = {}

        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)
        self.tcpSocket = self.cManager.openTCPServerRendezvous(PORT, 1)
        self.cListener.addConnection(self.tcpSocket)

        self.handlers = {
            CMSG_CHAT: self.msgChat,
            CMSG_INFO: self.handle_client_info,
        }

        taskMgr.add(self.listenTask, "serverListenTask", -40)
        taskMgr.add(self.readTask, "serverReadTask", -39)

    def listenTask(self, task):
        if self.cListener.newConnectionAvailable():
            rendezvous = PointerToConnection()
            netAddress = NetAddress()
            newConnection = PointerToConnection()

            if self.cListener.getNewConnection(rendezvous, netAddress, newConnection):
                newConnection = newConnection.p()
                # tell the Reader that there's a new connection to read from
                self.cReader.addConnection(newConnection)
                CLIENTS[newConnection] = netAddress.getIpString()
                CLIENTS_ID[newConnection] = self.playerCount
                CLIENTS_USER_NAMES[newConnection] = "Unknown"
                self.clientsAlive[self.playerCount] = newConnection
                self.playerCount += 1
                self.create_table_list()
            else:
                print("getNewConnection returned false")
        return task.cont

    def readTask(self, task):
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
        return (datagram, data, msgID)

    def handleDatagram(self, data, msgID, client):
        if msgID in self.handlers.keys():
            self.handlers[msgID](msgID, data, client)
        else:
            print("Unknown msgID: %d" % msgID)
            print(data)
        return

    def broadcast_pkg(self, pkg):
        for c in CLIENTS:
            self.cWriter.send(pkg, c)

    def broadcastMsg(self, msg):
        pkg = PyDatagram()
        pkg.addUint16(SMSG_CHAT)
        pkg.addString(msg)
        self.broadcast_pkg(pkg)

    def msgChat(self, msgID, data, client):
        print("ChatMsg: %s" % data.getString())

    def send_server_info(self):
        pkg = PyDatagram()
        pkg.addUint16(SMSG_INFO)
        for client, ip in CLIENTS.items():
            pkg.addUint8(CLIENTS_ID[client])
            pkg.addString(CLIENTS_USER_NAMES[client])
            pkg.addString(ip)
            pkg.addBool(False)
        self.broadcast_pkg(pkg)

    def handle_client_info(self, msgID, data, client):
        CLIENTS_USER_NAMES[client] = data.getString()
        self.create_table_list()
        self.send_server_info()

    def create_table_list(self):
        client_list = []
        name_list = []
        ip_list = []
        ready_list = []
        for client, ip in CLIENTS.items():
            client_list.append(CLIENTS_ID[client])
            name_list.append(CLIENTS_USER_NAMES[client])
            ip_list.append(ip)
            ready_list.append(False)

        self.gui.update_table(client_list, name_list, ip_list, ready_list)
