from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3, KeyboardButton

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.xSpeed = 0
        self.ySpeed = 0


        # Disable the camera trackball controls.
        self.disableMouse()

        # self.useDrive()
        # self.useTrackball()

        # Load the environment model.
        self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

        # ...or register event handlers
        self.accept("w", self.start_moving_forward)
        self.accept("w-up", self.stop_moving_forward)
        self.accept("s", self.start_moving_backward)
        self.accept("s-up", self.stop_moving_backward)
        self.accept("a", self.start_moving_left)
        self.accept("a-up", self.stop_moving_left)
        self.accept("d", self.start_moving_right)
        self.accept("d-up", self.stop_moving_right)

        self.taskMgr.add(self.moveCameraTask, "SpinCameraTask")

    def start_moving_forward(self):
        self.ySpeed = 1

    def stop_moving_forward(self):
        self.ySpeed = 0

    def start_moving_backward(self):
        self.ySpeed = -1

    def stop_moving_backward(self):
        self.ySpeed = 0

    def start_moving_left(self):
        self.xSpeed = -1

    def stop_moving_left(self):
        self.xSpeed = 0

    def start_moving_right(self):
        self.xSpeed = 1

    def stop_moving_right(self):
        self.xSpeed = 0

    def moveCameraTask(self, task):
        self.camera.setPos(self.camera.getX()  + self.xSpeed, self.camera.getY(), self.camera.getZ())
        self.camera.setPos(self.camera.getX(), self.camera.getY() + self.ySpeed, self.camera.getZ())
        return Task.cont

app = MyApp()
app.run()