from direct.actor.Actor import Actor
from bullet import Bullet


class Weapon:

    def __init__(self, model, hand, reload_time):
        self.reloadTime = reload_time
        self.reloadTimeCount = 0

        self.object_model = model
        self.object_model.reparentTo(hand)
        self.gunHole = self.object_model.exposeJoint(None, 'modelRoot', 'gun_hole')
        self.gunHandle = self.object_model.exposeJoint(None, 'modelRoot', 'gun_handle')
        self.object_model.setHpr(184, 0, 90)
        self.object_model.setPos(self.gunHandle.getPos())

    def fire_with_pos(self, world, x, y, z):
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


class Ak47(Weapon):

    def __init__(self, hand):
        object_model = Actor("models/ak47.egg")
        object_model.setScale(1)

        Weapon.__init__(self, object_model, hand, 10)
