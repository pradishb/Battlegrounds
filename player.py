from direct.actor.Actor import Actor
from panda3d.bullet import BulletCapsuleShape, BulletCharacterControllerNode, ZUp
from weapon import Weapon
from animation import Animation
from raycollider import RayCollider, LineSeg


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
        self.spineExpose = self.playerModel.exposeJoint(None, 'modelRoot', 'mixamorig:Spine')

        # player weapon
        myWeapon = Weapon()
        myWeapon.object_model.reparentTo(self.hand)

        # player animation
        self.animation = Animation(self)

        self.model = loader.loadModel("smiley")
        self.model.reparentTo(render)
        self.model.setScale(0.1)
        base.taskMgr.add(self.bendBody, "bendBody")
        self.playerSpine.setH(-15)

    def bendBody(self, task):
        if base.mouseWatcherNode.hasMouse():
            self.model.setPos(self.spineExpose, 0, 0, 0)
            obj = RayCollider.getObjectHit()
            self.model.lookAt(obj)
            self.playerSpine.setP(self.model.getP())
        return task.cont
