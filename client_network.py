from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from pandac.PandaModules import *
from client_game import ClientGame
from direct_gui import Layout
from msg_id import *


class ClientNetwork:
    def __init__(self, client):
        self.CLIENTS_ID = []
        self.CLIENTS_IP = {}
        self.CLIENTS_USER_NAMES = {}
        self.CLIENTS_READY = {}
        
        self.client = client
        self.client_game = None
        self.Connection = None
        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)

        self.handlers = {
            SMSG_CHAT: self.msg_chat,
            SMSG_INFO: self.handle_server_info,
            # SMSG_DISCONNECT_ACK: self.msgDisconnectAck,
        }

        self.command_handlers = {
            'game_end': self.game_end,
            'info': self.info,
            'start': self.game_start,
        }

    def connect_to_server(self, ip):
        if not self.Connection:
            self.Connection = self.cManager.openTCPClientConnection(ip, 9099, 1)
            if self.Connection:
                self.cReader.addConnection(self.Connection)
                self.send_user_info(self.client.clientGui.username_text.get())
                taskMgr.add(self.read_task, "serverReaderPollTask", -39)
                return "Connection Successful!"
            else:
                return "Connection Failed!"
        else:
            return "Already connected to a server."

    def read_task(self, task):
        while 1:
            (datagram, data, msgID) = self.non_blocking_read(self.cReader)
            if msgID is MSG_NONE:
                break
            else:
                self.handle_datagram(data, msgID)
        return task.cont

    def non_blocking_read(self, qcr):
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
        return datagram, data, msgID

    def handle_datagram(self, data, msgID):
        if msgID in self.handlers.keys():
            self.handlers[msgID](msgID, data)
        else:
            print("Unknown msgID: %d" % msgID)
            print(data)
        return

    def send(self, pkg):
        self.cWriter.send(pkg, self.Connection)

    def send_user_info(self, username):
        pkg = PyDatagram()
        pkg.addUint16(CMSG_INFO)
        pkg.addString(username)
        self.send(pkg)

    def handle_server_info(self, msgID, data):
        self.CLIENTS_ID.clear()
        while data.getRemainingSize() != 0:
            id = data.getUint8()
            username = data.getString()
            ip = data.getString()
            ready = data.getBool()
            self.CLIENTS_ID.append(id)
            self.CLIENTS_USER_NAMES[id] = username
            self.CLIENTS_IP[id] = ip
            self.CLIENTS_READY[id] = ready
        self.create_table_list()

    def send_msg(self, msg):
        pkg = PyDatagram()
        pkg.addUint16(CMSG_CHAT)
        pkg.addString(msg)
        self.send(pkg)

    def msg_chat(self, msgID, data):
        msg = data.getString()
        if msg[:1] == '/':
            msg = msg.strip('/')
            args = msg.split(' ')
            cmd = self.command_handlers.get(args[0], self.invalid_cmd)
            cmd(args)
        else:
            self.client.clientGui.update_chat(msg)
            print(msg)

    def create_table_list(self):
        client_list = []
        name_list = []
        ip_list = []
        ready_list = []
        for id in self.CLIENTS_ID:
            client_list.append(id)
            name_list.append(self.CLIENTS_USER_NAMES[id])
            ip_list.append(self.CLIENTS_IP[id])
            ready_list.append(self.CLIENTS_READY[id])
        self.client.clientGui.update_table(client_list, name_list, ip_list, ready_list)

    def countdown(self, args):
        pass

    def invalid_cmd(self, args):
        print("Invalid command.")
        pass

    def info(self, args):
        pass
        # if value == "no_clients":
        #     GameUI.createWhiteBgUI("Not enough clients connected.")
        # self.displayUI.destroy()

    def game_end(self, args):
        pass
        # if int(value) == self.id:
        #     GameUI.createDisplayUI("You Win!")

    def game_start(self, args):
        self.client_game = ClientGame(self)
        self.command_handlers['count_down'] = self.client_game.count_down
        self.handlers[SERVER_INPUT] = self.client_game.server_input_handler
        self.handlers[GAME_INITIALIZE] = self.client_game.game_initialize
        [obj.destroy() for obj in Layout.obj_list]
