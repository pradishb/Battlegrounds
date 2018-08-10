from direct.directbase.DirectStart import base


class Weapon:
    def __init__(self):
        damage = 10
        range = 20
        rate_of_fire = 1

        object_model = base.loader.loadModel("models/m1911.egg")
        object_model.setScale(0.025)
        object_model.setPos(1, 1, 1)

        object_model.reparentTo(base.render)
