import direct.directbase.DirectStart
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.core import *
from direct.gui.DirectGui import DirectFrame

client_list = [0, 1, 2]
client_names = ["biraj", "pradish", "srijan"]
client_ip = ["192.168.1.100", "192.168.1.105", "192.168.1.10"]
client_ready = [True, False, False]

table_labels = ["id", "name", "ip address", "ready"]
table_size = [.10, .30, .40, .20]

myFrame = DirectFrame(frameColor=(1, 1, 1, 1),
                      frameSize=(-1.2, 1.2, -0.7, 0.7),)

# Add some text
bk_text = "Lobby"
textObject = OnscreenText(text=bk_text, pos=(-1.2, 0.8), scale=0.1, fg=(1, 1, 1, 1), align=TextNode.ALeft, mayChange=1)

button_10 = DirectButton(parent=myFrame, text="Ready", scale=0.1, pos=(1.2, 0, -0.7), extraArgs=[10])

# Create table
table_width = 2.4
table_left = -1.2
current_table_x = table_left
for i in range(0, table_labels.__len__()):
    current_table_x += table_size[i] * table_width
    x_centered = current_table_x - table_size[i] * table_width / 2
    l3 = DirectLabel(parent=myFrame,
                     text=table_labels[i],
                     text_scale=0.6,
                     scale=0.1,
                     pos=(x_centered, 0, 0.6))

# Run the tutorial
base.run()
