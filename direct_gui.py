from direct.gui.DirectGui import *
from panda3d.core import *


class LobbyGui:
    def __init__(self):
        self.dialog = None

        self.chat_values = [["asdf"]]

        self.lobby_text = DirectLabel(text="Lobby", scale=0.05)
        self.lobby_table = DirectScrolledFrame(frameColor=(1, 1, 1, 1),
                                               frameSize=(-1.2, 1.2, -0.35, 0.35),
                                               canvasSize=(-1.2, 1.1, -0.6, 0.6), )
        self.chat_text = DirectLabel(text="Chat", scale=0.05)
        self.chat_box = DirectScrolledFrame(frameColor=(1, 1, 1, 1),
                                            frameSize=(-1.2, 1.2, -0.2, 0.2),
                                            canvasSize=(-1.2, 1.1, -0.6, 0.6), )

    def update_table(self, client_list, name_list, ip_list, ready_list):
        table_labels = ["id", "name", "ip address", "ready"]
        table_values = [client_list, name_list, ip_list, ready_list]
        table_size = [.10, .30, .40, .20]
        Layout.create_table(self.lobby_table, 2.4, -1.2, 0.6, table_labels, table_size, table_values, 0)

    def update_chat(self, msg):
        self.chat_values[0].append(msg)
        Layout.create_table(self.chat_box, 2.4, -1.2, 0.6, None, [1], self.chat_values, None)


class ClientGui(LobbyGui):
    def __init__(self, client):
        LobbyGui.__init__(self)
        self.client = client
        self.client_info_frame = DirectFrame(frameColor=(1, 1, 1, 0),
                                             frameSize=(0, 2.4, -0.07, 0), )
        self.username_label = DirectLabel(parent=self.client_info_frame, text="Username", scale=0.05,
                                          pos=(.12, 0, -0.05))
        self.username_text = DirectEntry(parent=self.client_info_frame, text="", scale=0.05, initialText="",
                                         focus=1, pos=(0.3, 0, -0.05))
        self.server_ip_label = DirectLabel(parent=self.client_info_frame, text="Server IP", scale=0.05,
                                           pos=(1, 0, -0.05))
        self.server_ip_text = DirectEntry(parent=self.client_info_frame, text="", scale=0.05, initialText="127.0.0.1",
                                          focus=1, pos=(1.15, 0, -0.05))
        self.connect_server_button = DirectButton(parent=self.client_info_frame, text="Connect Server", scale=0.05,
                                                  command=self.connect_button_handler, pos=(2, 0, -0.05))
        self.ready_button = DirectButton(text="Ready", scale=0.05,
                                         command=self.send_ready_signal)
        self.init_layout()

    def init_layout(self):
        # Layout.add_object(self.server_ip_text, 0.05, 0)
        # Layout.add_object(self.connect_server_button, 0.05, 0)
        Layout.add_object_left(self.client_info_frame, 1, 0)
        Layout.add_object(self.lobby_text, 0.05, -0.05)
        Layout.add_object(self.lobby_table, 1, 0.05)
        Layout.add_object(self.chat_text, 0.05, -0.05)
        Layout.add_object(self.chat_box, 1, 0.05)
        Layout.add_object(self.ready_button, 0.05, -0.05)

    def connect_button_handler(self):
        self.del_dialog(0)
        msg = self.client.myNetwork.connect_to_server(self.server_ip_text.get())
        self.dialog = OkDialog(text=msg, command=self.del_dialog)

    def send_ready_signal(self):
        self.del_dialog(0)
        if self.client.myNetwork.Connection:
            self.client.myNetwork.send_msg("/ready")

    def del_dialog(self, arg):
        if self.dialog:
            self.dialog.destroy()


class ServerGui(LobbyGui):
    def __init__(self):
        LobbyGui.__init__(self)
        self.init_layout()

    def init_layout(self):
        Layout.add_object(self.lobby_text, 0.05, -0.05)
        Layout.add_object(self.lobby_table, 1, 0.05)
        Layout.add_object(self.chat_text, 0.05, -0.05)
        Layout.add_object(self.chat_box, 1, 0.05)


class Layout:
    spacing = 0.05
    start_y = 0.9
    start_x = -1.2
    obj_list = []

    @staticmethod
    def add_object(obj, scale, offset):
        Layout.obj_list.append(obj)
        width = obj.getWidth() * scale
        height = obj.getHeight() * scale
        obj.setPos(Layout.start_x + width / 2, 0, + Layout.start_y - height / 2)
        Layout.start_y -= height + Layout.spacing + offset

    @staticmethod
    def add_object_left(obj, scale, offset):
        Layout.obj_list.append(obj)
        height = obj.getHeight() * scale
        obj.setPos(Layout.start_x, 0, + Layout.start_y)
        Layout.start_y -= height + Layout.spacing + offset

    @staticmethod
    def create_table(parent, width, left, start_y, table_labels, label_size, table_values, my_id):
        # Create table
        [i.remove_node() for i in parent.canvas.getChildren()]  # clear the table first
        table_width = width
        table_left = left
        current_table_x = table_left
        line_height = 0.1
        for i in range(0, table_values.__len__()):
            my_y = start_y
            current_table_x += label_size[i] * table_width
            x_centered = current_table_x - label_size[i] * table_width / 2
            if table_labels:
                my_y -= line_height
                DirectLabel(parent=parent.canvas,
                            text=table_labels[i],
                            text_scale=0.6,
                            scale=0.1,
                            pos=(x_centered, 0, my_y))

            for j in range(0, table_values[i].__len__()):
                bg = (1, 1, 1, 1)
                if my_id:
                    if j == my_id:
                        bg = (1, 1, 0, 1)
                my_y -= line_height
                DirectLabel(parent=parent.canvas,
                            text=str(table_values[i][j]),
                            text_scale=0.6,
                            scale=0.1,
                            pos=(x_centered, 0, my_y),
                            text_bg=bg)
