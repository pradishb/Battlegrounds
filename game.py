import direct.directbase.DirectStart
from direct.actor.Actor import Actor, AmbientLight, Vec4, DirectionalLight, Vec3, PNMImage, Filename, WindowProperties, \
    GeoMipTerrain
from panda3d.bullet import BulletCapsuleShape, BulletCharacterControllerNode, ZUp, BulletWorld, BulletHeightfieldShape, \
    BulletRigidBodyNode
from panda3d.core import BitMask32


class Player():
    def __init__(self, x, y, z):
        shape = BulletCapsuleShape(.2, .6, ZUp)
        self.playerNode = BulletCharacterControllerNode(shape, 0.4, 'Player')
        self.playerNode.setMaxJumpHeight(2.0)
        self.playerNode.setJumpSpeed(4.0)
        self.playerNP = render.attachNewNode(self.playerNode)
        self.playerNP.setPos(x, y, z)
        self.playerNP.setCollideMask(BitMask32.allOn())
        self.playerModel = Actor('models/soldier.egg', {"idle": "models/soldier_ani_idle.egg",
                                                        "walk": "models/soldier_ani_walk.egg"})
        myTexture = loader.loadTexture("models/soldier_texture.png")
        self.playerModel.setTexture(myTexture, 1)
        self.playerModel.setH(90)
        self.playerModel.setScale(.06)
        self.playerModel.setZ(-.45)
        self.playerModel.flattenLight()
        self.playerModel.setLightOff()
        self.playerModel.reparentTo(self.playerNP)

class GameEngine():
    def __init__(self):
        base.setFrameRateMeter(True)
        # Light
        self.alight = AmbientLight('ambientLight')
        self.alight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        self.alightNP = render.attachNewNode(self.alight)

        self.dlight = DirectionalLight('directionalLight')
        self.dlight.setDirection(Vec3(1, 1, -1))
        self.dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
        self.dlightNP = render.attachNewNode(self.dlight)

        render.clearLight()
        render.setLight(self.alightNP)
        render.setLight(self.dlightNP)

        # World
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))

        # HeightField
        self.height = 8.0
        self.img = PNMImage(Filename('models/elevation.png'))
        self.hshape = BulletHeightfieldShape(self.img, self.height, ZUp)
        self.hnode = BulletRigidBodyNode('HGround')
        self.hnode.addShape(self.hshape)
        self.world.attachRigidBody(self.hnode)

        # Terrian
        terrain = GeoMipTerrain('terrain')
        terrain.setHeightfield(self.img)

        offset = self.img.getXSize() / 2.0 - 0.5
        rootNP = terrain.getRoot()
        rootNP.reparentTo(render)
        rootNP.setSz(self.height)
        rootNP.setPos(-offset, -offset, -self.height / 2.0)
        terrain.generate()

        self.speed = Vec3(0, 0, 0)
        self.walk_speed = 1.5

        self.players = []

        # Camera
        base.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)

        # Pointer
        # imageObject = self.makeArc()
        # imageObject.setSx(.02)
        # imageObject.setSy(.02)
        # imageObject.setSz(.02)
        # imageObject.reparent_to(aspect2d)]

    def initCam(self):
        base.cam.setHpr(-40, -40, 0)
        base.cam.setPos(-25, -30, 30)
