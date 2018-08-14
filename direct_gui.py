from direct.gui.DirectGui import *
from panda3d.core import *


class LobbyGui:
    def __init__(self):
        my_id = 1

        client_list = [0, 1, 2]
        client_names = ["biraj", "pradish", "srijan"]
        client_ip = ["192.168.1.100", "192.168.1.105", "192.168.1.10"]
        client_ready = [True, False, False]

        chat_values = [["Server : hello", "me : hi"]]
        chat_size = [1]

        table_labels = ["id", "name", "ip address", "ready"]
        table_values = [client_list, client_names, client_ip, client_ready]
        table_size = [.10, .30, .40, .20]

        lobby_text = DirectLabel(text="Lobby", scale=0.1)
        lobby_table = DirectScrolledFrame(frameColor=(1, 1, 1, 1),
                                          frameSize=(-1.2, 1.2, -0.35, 0.35),
                                          canvasSize=(-1.2, 1.1, -0.35, 0.35), )
        chat_text = DirectLabel(text="Chat", scale=0.1)
        chat_box = DirectScrolledFrame(frameColor=(1, 1, 1, 1),
                                       frameSize=(-1.2, 1.2, -0.2, 0.2),
                                       canvasSize=(-1.2, 1.1, -0.2, 0.2), )
        ready_button = DirectButton(text="Ready", scale=0.1)

        Layout.create_table(lobby_table, 2.4, -1.2, 0.35, table_labels, table_size, table_values, my_id)
        Layout.create_table(chat_box, 2.4, -1.2, 0.2, None, chat_size, chat_values, None)

        Layout.add_object(lobby_text, 0.1, -0.05)
        Layout.add_object(lobby_table, 1, 0.05)
        Layout.add_object(chat_text, 0.1, -0.05)
        Layout.add_object(chat_box, 1, 0.05)
        Layout.add_object(ready_button, 0.1, -0.05)


class Layout:
    spacing = 0.05
    start_y = 0.9
    start_x = -1.2

    @staticmethod
    def add_object(obj, scale, offset):
        width = obj.getWidth() * scale
        height = obj.getHeight() * scale
        obj.setPos(Layout.start_x + width / 2, 0, + Layout.start_y - height / 2)
        Layout.start_y -= height + Layout.spacing + offset

    @staticmethod
    def create_table(parent, width, left, start_y, table_labels, label_size, table_values, my_id):
        # Create table
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
