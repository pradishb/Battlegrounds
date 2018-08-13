from direct.actor.Actor import Actor
from panda3d.core import NodePath
from bullet import Bullet


class Weapon:
    object_model = NodePath()

    def __init__(self):
        damage = 10
        range = 20
        self.mouseDelay = 50
        self.mouseDelayCount = 0

        Weapon.object_model = Actor("models/m1911.egg")
        Weapon.object_model.setScale(0.35)
        Weapon.object_model.setPos(0, 0.5, 0)
        Weapon.object_model.setHpr(90, -90, 0)
        self.gunHole = self.object_model.exposeJoint(None, 'modelRoot', 'gunhole')

    def fireWithPos(self, world, x, y, z):
        b = Bullet(world, self.gunHole)
        b.initializeWithPos(x, y, z)
        b.shoot()

    def get_reload(self):
        if self.mouseDelayCount <= 0:
            self.mouseDelayCount = self.mouseDelay
            return True
        return False

    def update_reload_time(self):
        self.mouseDelayCount -= 1

