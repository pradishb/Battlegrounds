from direct.directbase.DirectStart import base
import math
import sys
from direct.actor.Actor import Actor, AmbientLight, Vec4, DirectionalLight, Vec3, PNMImage, Filename, WindowProperties, GeoMipTerrain
from panda3d.bullet import BulletCapsuleShape, BulletCharacterControllerNode, ZUp, BulletWorld, BulletHeightfieldShape, \
    BulletRigidBodyNode, BulletDebugNode, BulletSphereShape
from panda3d.core import BitMask32, ClockObject

from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import LineSegs, deg2Rad, NodePath
import weapon


class Player:
    def __init__(self, x, y, z):
        shape = BulletCapsuleShape(.2, .6, ZUp)
        self.playerNode = BulletCharacterControllerNode(shape, 0.4, 'Player')
        self.playerNode.setMaxJumpHeight(2.0)
        self.playerNode.setJumpSpeed(4.0)
        self.playerNP = base.render.attachNewNode(self.playerNode)
        self.playerNP.setPos(x, y, z)
        self.playerNP.setCollideMask(BitMask32.allOn())
        self.playerModel = Actor('models/soldier.egg', {"idle": "models/soldier_ani_idle.egg",
                                                        "walk": "models/soldier_ani_walk.egg",
                                                        "pistol": "models/soldier_ani_pistol.egg",})
        myTexture = base.loader.loadTexture("models/soldier_texture.png")

        self.playerModel.setTexture(myTexture, 1)
        self.playerModel.setH(90)
        self.playerModel.setScale(.06)
        self.playerModel.setZ(-.45)
        self.playerModel.flattenLight()
        self.playerModel.setLightOff()
        self.playerModel.reparentTo(self.playerNP)

        self.playerModel.makeSubpart("legs", ["mixamorig:LeftUpLeg", "mixamorig:RightUpLeg",])
        self.playerModel.makeSubpart("hips", ["mixamorig:Hips"], ["mixamorig:LeftUpLeg", "mixamorig:RightUpLeg", "mixamorig:Spine"])
        self.playerModel.makeSubpart("upperBody", ["mixamorig:Spine"])
        self.playerSpine = self.playerModel.controlJoint(None, 'modelRoot', 'mixamorig:Spine')

        # player weapon
        myWeapon = weapon.Weapon()

        base.taskMgr.add(self.bendBody, "bendBody")

    def clamp(i, mn=-100, mx=100):
        return min(max(i, mn), mx)

    def bendBody(self, task):
        if base.mouseWatcherNode.hasMouse():
            self.playerSpine.setP(base.cam.getP() * 1.5)
        return task.cont



class GameEngine():
    def __init__(self):
        base.setFrameRateMeter(True)
        globalClock.setFrameRate(60)
        globalClock.setMode(ClockObject.MLimited)

        base.accept('f1', self.toggleDebug)
        base.accept('escape', sys.exit, [0])

        self.debugNode = BulletDebugNode('Debug')
        self.debugNode.showWireframe(True)
        self.debugNode.showConstraints(True)
        self.debugNode.showBoundingBoxes(False)
        self.debugNode.showNormals(False)
        self.debugNP = base.render.attachNewNode(self.debugNode)

        # World
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debugNP.node())

        # # HeightField
        self.height = 8.0
        self.img = PNMImage(Filename('models/elevation.png'))
        self.hshape = BulletHeightfieldShape(self.img, self.height, ZUp)
        self.hnode = BulletRigidBodyNode('HGround')
        self.hnode.addShape(self.hshape)
        self.world.attachRigidBody(self.hnode)

        # Terrain
        # visNP = base.loader.loadModel("models/world.egg")
        # geom = visNP.findAllMatches('**/+GeomNode').getPath(0).node().getGeom(0)
        # shape = BulletConvexHullShape()
        # shape.addGeom(geom)
        #
        # body = BulletRigidBodyNode('Egg-%i')
        # bodyNP = base.render.attachNewNode(body)
        # bodyNP.node().addShape(shape)
        # bodyNP.node().setDeactivationEnabled(False)
        # bodyNP.setCollideMask(BitMask32.allOn())
        # bodyNP.setPos(0,0,-10)
        # # bodyNP.setScale(1.5)
        # self.world.attachRigidBody(bodyNP.node())

        # visNP.reparentTo(base.render)


        #huge spere
        radius = 3
        shape = BulletSphereShape(radius)

        node = BulletRigidBodyNode('Box')
        node.setMass(1.0)
        node.addShape(shape)

        np = base.render.attachNewNode(node)
        np.setPos(0, 0, 0)

        self.world.attachRigidBody(node)



        terrain = GeoMipTerrain('terrain')
        terrain.setHeightfield(self.img)

        offset = self.img.getXSize() / 2.0 - 0.5
        rootNP = terrain.getRoot()
        rootNP.reparentTo(base.render)
        rootNP.setSz(self.height)
        rootNP.setPos(-offset, -offset, -self.height / 2.0)
        terrain.generate()

        # Player
        self.players = []
        self.speed = Vec3(0, 0, 0)
        self.walk_speed = 1.5

        # Camera
        base.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)

        self.initCam()
        # taskMgr.add(self.spinCameraTask, "SpinCameraTask")

    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        angleDegrees = task.time * 6.0
        angleRadians = angleDegrees * (math.pi / 180.0)
        base.cam.setPos(20 * math.sin(angleRadians), -20.0 * math.cos(angleRadians), 50)
        base.cam.setHpr(angleDegrees, -45, 0)
        return task.cont

    def initCam(self):
        base.cam.setHpr(-40, -40, 0)
        base.cam.setPos(0, 0, 10)

    # Debug
    def toggleDebug(self):
        if self.debugNP.isHidden():
            self.debugNP.show()
        else:
            self.debugNP.hide()

class ClientGameEngine(GameEngine):
    def __init__(self):
        GameEngine.__init__(self)
        # Light
        self.alight = AmbientLight('ambientLight')
        self.alight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        self.alightNP = base.render.attachNewNode(self.alight)

        self.dlight = DirectionalLight('directionalLight')
        self.dlight.setDirection(Vec3(1, 1, -1))
        self.dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
        self.dlightNP = base.render.attachNewNode(self.dlight)

        base.render.clearLight()
        base.render.setLight(self.alightNP)
        base.render.setLight(self.dlightNP)

        # Pointer
        self.pointer = self.makeArc()
        self.pointer.setSx(.02)
        self.pointer.setSy(.02)
        self.pointer.setSz(.02)

        #Onscreentext
        font = base.loader.loadFont('./fonts/neuropol.ttf')
        font.setPixelsPerUnit(60)
        self.textObject = OnscreenText(text="No Connection", pos=(0, 0), font=font, scale=0.25, fg=(255, 255, 255, 255))
        self.textObject.setColor(255, 255, 255, 255)

    # player animation
    def animate(self, player, xSpeed, ySpeed):
        if (xSpeed == 0 and ySpeed == 0):
            if (player.playerModel.get_current_anim("legs") != "idle"):
                player.playerModel.loop("idle", partName="legs")
                player.playerModel.loop("idle", partName="hips")
                player.playerModel.pose("pistol", 0, partName="upperBody")
        else:
            if (player.playerModel.get_current_anim("legs") != "walk"):
                player.playerModel.loop("walk", partName="legs")
                player.playerModel.loop("idle", partName="hips")
                player.playerModel.pose("pistol", 0, partName="upperBody")
        # if (xSpeed == 0 and ySpeed == 0):
        #     if (player.playerModel.get_current_anim() != "idle"):
        #         player.playerModel.loop("idle")
        # else:
        #     if (player.playerModel.get_current_anim() != "walk"):
        #         player.playerModel.loop("walk")

    def makeArc(self, angleDegrees=360, numSteps=16):
        ls = LineSegs()
        angleRadians = deg2Rad(angleDegrees)
        for i in range(numSteps + 1):
            a = angleRadians * i / numSteps
            y = math.sin(a)
            x = math.cos(a)
            ls.drawTo(x, 0, y)
        node = ls.create()
        return NodePath(node)

    def showPointer(self):
        self.pointer.reparent_to(base.aspect2d)
