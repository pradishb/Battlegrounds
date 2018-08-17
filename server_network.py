from direct.distributed.PyDatagram import PyDatagram
from pandac.PandaModules import *
from direct.distributed.PyDatagramIterator import PyDatagramIterator

from server_game import ServerGame
from direct_gui import Layout
from msg_id import *

PORT = 9099


class ServerNetwork:
    def __init__(self, gui):
        self.CLIENTS_ID = []
        self.RELATION_OBJ_ID = {}
        self.CLIENTS_IP = {}
        self.CLIENTS_USER_NAMES = {}
        self.CLIENTS_READY = {}
        self.CLIENT_INPUT_RECEIVED = []

        self.gui = gui
        self.server_game = None
        self.playerCount = 0
        self.min_player = 1

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
        # self.game_start()

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
                self.CLIENTS_ID.append(id)
                self.RELATION_OBJ_ID[id] = newConnection
                self.RELATION_OBJ_ID[newConnection] = id
                self.CLIENTS_IP[id] = netAddress.getIpString()
                self.CLIENTS_USER_NAMES[id] = "Unknown"
                self.CLIENTS_READY[id] = False
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
        for c in self.CLIENTS_ID:
            self.cWriter.send(pkg, self.RELATION_OBJ_ID[c])

    def broadcastMsg(self, msg):
        pkg = PyDatagram()
        pkg.addUint16(SMSG_CHAT)
        pkg.addString(msg)
        self.broadcast_pkg(pkg)

    def msg_chat(self, msgID, data, client):
        msg = data.getString()
        chat_msg = "%s: %s" % (self.CLIENTS_USER_NAMES[self.RELATION_OBJ_ID[client]], msg)
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
        for id in self.CLIENTS_ID:
            pkg.addUint8(id)
            pkg.addString(self.CLIENTS_USER_NAMES[id])
            pkg.addString(self.CLIENTS_IP[id])
            pkg.addBool(self.CLIENTS_READY[id])
        self.broadcast_pkg(pkg)

    def handle_client_info(self, msgID, data, client):
        self.CLIENTS_USER_NAMES[self.RELATION_OBJ_ID[client]] = data.getString()
        self.create_table_list()
        self.send_server_info()
        chat_msg = "Server : " + self.CLIENTS_USER_NAMES[self.RELATION_OBJ_ID[client]] + " has joined the lobby."
        self.broadcastMsg(chat_msg)
        self.gui.update_chat(chat_msg)

    def handle_client_ready_signal(self, args, client):
        self.CLIENTS_READY[self.RELATION_OBJ_ID[client]] = True
        self.create_table_list()
        self.send_server_info()
        if self.playerCount >= self.min_player and all(v for k, v in self.CLIENTS_READY.items()):
            chat_msg = "/start"
            self.broadcastMsg(chat_msg)
            self.gui.update_chat(chat_msg)
            self.server_game = ServerGame(self)
            self.server_game.count_down_start()
            [obj.destroy() for obj in Layout.obj_list]

    def create_table_list(self):
        client_list = []
        name_list = []
        ip_list = []
        ready_list = []
        for my_id in self.CLIENTS_ID:
            client_list.append(my_id)
            name_list.append(self.CLIENTS_USER_NAMES[my_id])
            ip_list.append(self.CLIENTS_IP[my_id])
            ready_list.append(self.CLIENTS_READY[my_id])

        self.gui.update_table(client_list, name_list, ip_list, ready_list)
