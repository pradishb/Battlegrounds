from direct.actor.Actor import Actor
from panda3d.core import NodePath
from bullet import Bullet


class Weapon:
    object_model = NodePath()

    def __init__(self):
        damage = 10
        range = 20
        self.reloadTime = 20
        self.reloadTimeCount = 0

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
        if self.reloadTimeCount <= 0:
            self.reloadTimeCount = self.reloadTime
            return True
        return False

    def update_reload_time(self):
        self.reloadTimeCount -= 1

