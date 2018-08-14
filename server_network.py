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

CLIENTS_ID = []
RELATION_OBJ_ID = {}
CLIENTS_IP = {}
CLIENTS_USER_NAMES = {}
CLIENTS_READY = {}
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
            CMSG_CHAT: self.msg_chat,
            CMSG_INFO: self.handle_client_info,
        }

        self.command_handlers = {
            "ready": self.handle_client_ready_signal
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
                id = self.playerCount
                CLIENTS_ID.append(id)
                RELATION_OBJ_ID[id] = newConnection
                RELATION_OBJ_ID[newConnection] = id
                CLIENTS_IP[id] = netAddress.getIpString()
                CLIENTS_USER_NAMES[id] = "Unknown"
                CLIENTS_READY[id] = False
                self.clientsAlive[id] = newConnection
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
        for c in CLIENTS_ID:
            self.cWriter.send(pkg, RELATION_OBJ_ID[c])

    def broadcastMsg(self, msg):
        pkg = PyDatagram()
        pkg.addUint16(SMSG_CHAT)
        pkg.addString(msg)
        self.broadcast_pkg(pkg)

    def msg_chat(self, msgID, data, client):
        msg = data.getString()
        chat_msg = "%s: %s" % (CLIENTS_USER_NAMES[RELATION_OBJ_ID[client]], msg)
        self.broadcastMsg(chat_msg)
        self.gui.update_chat(chat_msg)
        if msg[:1] == '/':
            msg = msg.strip('/')
            args = msg.split(' ')
            cmd = self.command_handlers.get(args[0], "invalid")
            cmd(args, client)

    def send_server_info(self):
        pkg = PyDatagram()
        pkg.addUint16(SMSG_INFO)
        for id in CLIENTS_ID:
            pkg.addUint8(id)
            pkg.addString(CLIENTS_USER_NAMES[id])
            pkg.addString(CLIENTS_IP[id])
            pkg.addBool(CLIENTS_READY[id])
        self.broadcast_pkg(pkg)

    def handle_client_info(self, msgID, data, client):
        CLIENTS_USER_NAMES[RELATION_OBJ_ID[client]] = data.getString()
        self.create_table_list()
        self.send_server_info()
        chat_msg = "Server : " + CLIENTS_USER_NAMES[RELATION_OBJ_ID[client]] + " has joined the lobby."
        self.broadcastMsg(chat_msg)
        self.gui.update_chat(chat_msg)

    def handle_client_ready_signal(self, args, client):
        CLIENTS_READY[RELATION_OBJ_ID[client]] = True
        self.create_table_list()
        self.send_server_info()

    def create_table_list(self):
        client_list = []
        name_list = []
        ip_list = []
        ready_list = []
        for my_id in CLIENTS_ID:
            client_list.append(my_id)
            name_list.append(CLIENTS_USER_NAMES[my_id])
            ip_list.append(CLIENTS_IP[my_id])
            ready_list.append(CLIENTS_READY[my_id])

        self.gui.update_table(client_list, name_list, ip_list, ready_list)
