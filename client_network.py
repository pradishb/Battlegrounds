from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from pandac.PandaModules import *

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


class ClientNetwork:
    def __init__(self):
        self.Connection = None
        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)

        self.handlers = {
            # SMSG_AUTH_RESPONSE: self.msgAuthResponse,
            SMSG_CHAT: self.msgChat,
            # SMSG_DISCONNECT_ACK: self.msgDisconnectAck,
            # SERVER_INPUT: self.serverInputHanlder,
            # GAME_INITIALIZE: self.gameInitialize,
        }

    def connect_to_server(self, ip):
        if not self.Connection:
            self.Connection = self.cManager.openTCPClientConnection(ip, 9099, 1)

            if self.Connection:
                self.cReader.addConnection(self.Connection)
                self.send_user_info("lmao")
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

    def msgChat(self, msgID, data):
        msg = data.getString()
        if msg[:1] == '/':
            msg = msg.strip('/')
            self.console_cmd_executor(msg)
        else:
            print(msg)

    def console_cmd_executor(self, msg):
        temp = msg.split(' ')
        switcher = {
            'timeToStart': self.countdown,
            'game_end': self.game_end,
            'info': self.info,
            }
        fucn = switcher.get(temp[0], "invalid")
        fucn(temp[1])

    def countdown(self, value):
        print(value)

    def invalid(self, value):
        print("Invalid command for " + value)

    def info(self, value):
        pass
        # if value == "no_clients":
        #     GameUI.createWhiteBgUI("Not enough clients connected.")
            # self.displayUI.destroy()

    def game_end(self, value):
        pass
        # if int(value) == self.id:
        #     GameUI.createDisplayUI("You Win!")
