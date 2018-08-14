from pandac.PandaModules import *


class ClientNetwork:
    def __init__(self):
        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)

    def connect_to_server(self):
        self.Connection = self.cManager.openTCPClientConnection("127.0.0.1", 9099, 1)

        if self.Connection:
            self.cReader.addConnection(self.Connection)
            return True
            # taskMgr.add(self.readTask, "serverReaderPollTask", -39)
            # self.sendMsgAuth()
        else:
            return False

