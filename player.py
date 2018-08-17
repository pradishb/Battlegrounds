from direct.actor.Actor import Actor
from panda3d.bullet import BulletCharacterControllerNode, ZUp, BulletCylinderShape
from panda3d.core import NodePath
from weapon import Ak47
from animation import Animation
from raycollider import RayCollider


class Player:
    def __init__(self, x, y, z, id):
        self.health = 100
        radius = .15
        height = 1
        shape = BulletCylinderShape(radius, height, ZUp)
        self.playerNode = BulletCharacterControllerNode(shape, 0.4, str(id))
        self.playerNode.setMaxJumpHeight(2.0)
        self.playerNode.setJumpSpeed(4.0)
        self.playerNP = base.render.attachNewNode(self.playerNode)
        self.playerNP.setPos(x, y, z)
        self.playerModel = Actor('models/soldier.egg', {"idle": "models/soldier_ani_idle.egg",
                                                        "walk": "models/soldier_ani_walk.egg",
                                                        "pistol": "models/soldier_ani_pistol.egg",
                                                        "death": "models/soldier_ani_death.egg",})

        self.playerModel.makeSubpart("legs", ["mixamorig:LeftUpLeg", "mixamorig:RightUpLeg"])
        self.playerModel.makeSubpart("hips", ["mixamorig:Hips"], ["mixamorig:LeftUpLeg", "mixamorig:RightUpLeg", "mixamorig:Spine"])
        self.playerModel.makeSubpart("upperBody", ["mixamorig:Spine"])
        self.playerModel.pose("idle", 0, partName="hips")

        self.playerModel.setH(90)
        self.playerModel.setScale(.06)
        self.playerModel.setZ(-.45)
        self.playerModel.flattenLight()
        # self.playerModel.setLightOff()self.playerSpine
        self.playerModel.reparentTo(self.playerNP)

        self.playerSpine = self.playerModel.controlJoint(None, 'modelRoot', 'mixamorig:Spine')
        self.hand = self.playerModel.exposeJoint(None, 'modelRoot', 'mixamorig:RightHand')
        self.spineExpose = self.playerModel.exposeJoint(None, 'modelRoot', 'mixamorig:Spine')
        self.playerSpine.setH(-7)

        # player weapon
        self.weapon = Ak47(self.hand)

        # player animation
        self.xSpeed = 0
        self.ySpeed = 0
        self.animation = Animation(self)

        self.model = NodePath("MySpineNode")

    def bendBody(self):
        self.model.setPos(self.spineExpose, 0, 0, 0)
        obj = RayCollider.getObjectHit()
        self.model.lookAt(obj)
        self.playerSpine.setP(self.model.getP())
