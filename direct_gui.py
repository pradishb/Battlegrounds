from direct.gui.DirectGui import *
from panda3d.core import *


class LobbyGui:
    def __init__(self):
        my_id = 1

        client_list = [0, 1, 2]
        client_names = ["biraj", "pradish", "srijan"]
        client_ip = ["192.168.1.100", "192.168.1.105", "192.168.1.10"]
        client_ready = [True, False, False]

        table_labels = ["id", "name", "ip address", "ready"]
        table_values = [client_list, client_names, client_ip, client_ready]
        table_size = [.10, .30, .40, .20]

        lobby_text = DirectLabel(text="Lobby", scale=0.1)
        lobby_table = DirectScrolledFrame(frameColor=(1, 1, 1, 1),
                                       frameSize=(-1.2, 1.2, -0.35, 0.35),
                                       canvasSize=(-1.2, 1.1, -0.35, 0.35),)
        chat_text = DirectLabel(text="Chat", scale=0.1)
        chat_box = DirectScrolledFrame(frameColor=(1, 1, 1, 1),
                                       frameSize=(-1.2, 1.2, -0.2, 0.2),
                                       canvasSize=(-1.2, 1.1, -0.2, 0.2), )
        ready_button = DirectButton(text="Ready", scale=0.1)

        # Create table
        table_width = 2.4
        table_left = -1.2
        current_table_x = table_left
        start_y = 0.35
        line_height = 0.1
        for i in range(0, table_labels.__len__()):
            current_table_x += table_size[i] * table_width
            x_centered = current_table_x - table_size[i] * table_width / 2
            DirectLabel(parent=lobby_table.canvas,
                        text=table_labels[i],
                        text_scale=0.6,
                        scale=0.1,
                        pos=(x_centered, 0, start_y - line_height))
            for j in range(0, table_values[i].__len__()):
                bg = ((1, 1, 0, 1) if j == my_id else (1, 1, 1, 1))
                DirectLabel(parent=lobby_table.canvas,
                            text=str(table_values[i][j]),
                            text_scale=0.6,
                            scale=0.1,
                            pos=(x_centered, 0, start_y - (j + 2) * line_height),
                            text_bg=bg)
        # Layout.add_object(lobby_text, 0.1)
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
        print(obj.getHeight())
        obj.setPos(Layout.start_x + width / 2, 0, + Layout.start_y - height / 2)
        Layout.start_y -= height + Layout.spacing + offset
