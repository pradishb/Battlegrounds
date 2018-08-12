from direct.directbase.DirectStart import base
import math
import sys
from direct.actor.Actor import AmbientLight, Vec4, DirectionalLight, Vec3, PNMImage, Filename, WindowProperties, GeoMipTerrain
from panda3d.bullet import BulletWorld, BulletRigidBodyNode, BulletDebugNode, BulletTriangleMesh, \
    BulletTriangleMeshShape, BulletBoxShape
from panda3d.core import BitMask32, ClockObject
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import LineSegs, deg2Rad, NodePath


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
        self.debugNP.show()

        # World
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debugNP.node())

        # Terrain
        visNP = base.loader.loadModel('models/terrain.egg')

        mesh = BulletTriangleMesh()
        for x in visNP.findAllMatches('**/+GeomNode'):
            geom = x.node().getGeom(0)
            mesh.addGeom(geom)
        shape = BulletTriangleMeshShape(mesh, dynamic=True)

        body = BulletRigidBodyNode('Bowl')
        bodyNP = base.render.attachNewNode(body)
        bodyNP.node().addShape(shape)
        bodyNP.setPos(0, 0, 1)
        bodyNP.setCollideMask(BitMask32.allOn())
        self.world.attachRigidBody(bodyNP.node())

        visNP.reparentTo(bodyNP)

        shapex = BulletBoxShape(5)
        bodyx = BulletRigidBodyNode('Egg')
        bodyNPx = base.render.attachNewNode(bodyx)
        bodyNPx.setPos(0, 0, 3)
        bodyNPx.node().setMass(100.0)
        bodyNPx.node().addShape(shapex)
        self.world.attachRigidBody(bodyNPx.node())
        # visNP.reparentTo(bodyNPx)


        # Player
        self.players = []
        self.speed = Vec3(0, 0, 0)
        self.walk_speed = 5

        # Camera
        base.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)

        self.initCam()

    def initCam(self):
        base.cam.setHpr(0, -90, 0)
        base.cam.setPos(0, 0, 170)

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
        self.alight.setColor(Vec4(0.5, 0.5, 0.5, 1))
        self.alightNP = base.render.attachNewNode(self.alight)

        self.dlight = DirectionalLight('directionalLight')
        self.dlight.setDirection(Vec3(1, 1, -1))
        self.dlight.setColor(Vec4(1, 1, 1, 1))
        self.dlightNP = base.render.attachNewNode(self.dlight)

        base.render.clearLight()
        base.render.setLight(self.alightNP)
        base.render.setLight(self.dlightNP)

        # Pointer
        self.pointer = self.makeArc()
        self.pointer.setSx(.02)
        self.pointer.setSy(.02)
        self.pointer.setSz(.02)

        # Onscreentext
        font = base.loader.loadFont('./fonts/neuropol.ttf')
        font.setPixelsPerUnit(60)
        self.textObject = OnscreenText(text="No Connection", pos=(0, 0), font=font, scale=0.25, fg=(0, 0, 0, 255))
        self.textObject.setColor(255, 255, 255, 255)

    def makeArc(self, angleDegrees=360, numSteps=16):
        ls = LineSegs()
        ls.setColor(0, 1, 0, 1)
        ls.setThickness(3)
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
