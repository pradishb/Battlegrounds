from direct.directbase.DirectStart import base
from panda3d.core import NodePath

class Weapon:
    object_model = NodePath()

    def __init__(self):
        damage = 10
        range = 20
        rate_of_fire = 1

        Weapon.object_model = base.loader.loadModel("models/m1911.egg")
        Weapon.object_model.setScale(0.5)
        Weapon.object_model.setPos(1, 1, 1)
