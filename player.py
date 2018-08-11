from direct.actor.Actor import Actor
from panda3d.bullet import BulletCapsuleShape, BulletCharacterControllerNode, ZUp, BulletCylinderShape
from weapon import Weapon
from animation import Animation
from raycollider import RayCollider


class Player:
    def __init__(self, x, y, z, id):
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
        self.playerSpine.setH(-15)
        self.hand = self.playerModel.exposeJoint(None, 'modelRoot', 'mixamorig:RightHand')
        self.spineExpose = self.playerModel.exposeJoint(None, 'modelRoot', 'mixamorig:Spine')

        # player weapon
        self.weapon = Weapon()
        self.weapon.object_model.reparentTo(self.hand)

        # player animation
        self.animation = Animation(self)

        self.model = loader.loadModel("smiley")
        self.model.reparentTo(render)
        self.model.setScale(0.1)

    def bendBody(self):
        self.model.setPos(self.spineExpose, 0, 0, 0)
        obj = RayCollider.getObjectHit()
        # RayCollider.cameraToPointer.update(self.hand.getPos(base.render), obj)
        self.model.lookAt(obj)
        self.playerSpine.setP(self.model.getP())