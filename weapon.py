from direct.actor.Actor import Actor
from panda3d.core import NodePath
from bullet import Bullet


class Weapon:
    object_model = NodePath()

    def __init__(self):
        damage = 10
        range = 20
        rate_of_fire = 1

        Weapon.object_model = Actor("models/m1911.egg")
        Weapon.object_model.setScale(0.35)
        Weapon.object_model.setPos(0, 0.5, 0)
        Weapon.object_model.setHpr(90, -90, 0)
        self.gunHole = self.object_model.exposeJoint(None, 'modelRoot', 'gunhole')


    def fire(self, world, shootPos):
        b = Bullet(world, self.gunHole.getPos(render), shootPos)

