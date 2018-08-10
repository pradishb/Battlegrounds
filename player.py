from direct.actor.Actor import Actor
from panda3d.bullet import BulletCapsuleShape, BulletCharacterControllerNode, ZUp
from weapon import Weapon
from animation import Animation


class Player:
    def __init__(self, x, y, z):
        shape = BulletCapsuleShape(.2, .6, ZUp)
        self.playerNode = BulletCharacterControllerNode(shape, 0.4, 'Player')
        self.playerNode.setMaxJumpHeight(2.0)
        self.playerNode.setJumpSpeed(4.0)
        self.playerNP = base.render.attachNewNode(self.playerNode)
        self.playerNP.setPos(x, y, z)
        self.playerModel = Actor('models/soldier.egg', {"idle": "models/soldier_ani_idle.egg",
                                                        "walk": "models/soldier_ani_walk.egg",
                                                        "pistol": "models/soldier_ani_pistol.egg",})

        self.playerModel.makeSubpart("legs", ["mixamorig:LeftUpLeg", "mixamorig:RightUpLeg"])
        self.playerModel.makeSubpart("hips", ["mixamorig:Hips"], ["mixamorig:LeftUpLeg", "mixamorig:RightUpLeg", "mixamorig:Spine"])
        self.playerModel.makeSubpart("upperBody", ["mixamorig:Spine"])

        self.playerModel.setH(90)
        self.playerModel.setScale(.06)
        self.playerModel.setZ(-.45)
        self.playerModel.flattenLight()
        # self.playerModel.setLightOff()
        self.playerModel.reparentTo(self.playerNP)

        self.playerSpine = self.playerModel.controlJoint(None, 'modelRoot', 'mixamorig:Spine')
        self.hand = self.playerModel.exposeJoint(None, 'modelRoot', 'mixamorig:RightHand')

        # player weapon
        myWeapon = Weapon()
        myWeapon.object_model.reparentTo(self.hand)

        # player animation
        self.animation = Animation(self)

        base.taskMgr.add(self.bendBody, "bendBody")

    def bendBody(self, task):
        if base.mouseWatcherNode.hasMouse():
            self.playerSpine.setP(base.cam.getP() * 1.5)
        return task.cont
