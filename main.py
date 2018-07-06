import direct.directbase.DirectStart
from direct.showbase.InputStateGlobal import inputState
from direct.showbase.DirectObject import DirectObject
from panda3d.core import Vec3, BitMask32, GeoMipTerrain, AmbientLight, Vec4, DirectionalLight, Filename, PNMImage
from panda3d.bullet import BulletWorld, BulletCapsuleShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletHeightfieldShape
from panda3d.bullet import ZUp
from panda3d.bullet import BulletCharacterControllerNode
from direct.actor.Actor import Actor, WindowProperties
import math

#Debug
def toggleDebug():
    if debugNP.isHidden():
        debugNP.show()
    else:
        debugNP.hide()

o = DirectObject()
o.accept('f1', toggleDebug)

debugNode = BulletDebugNode('Debug')
debugNode.showWireframe(True)
debugNode.showConstraints(True)
debugNode.showBoundingBoxes(False)
debugNode.showNormals(False)
debugNP = render.attachNewNode(debugNode)
debugNP.show()

# Light
alight = AmbientLight('ambientLight')
alight.setColor(Vec4(0.2, 0.2, 0.2, 1))
alightNP = render.attachNewNode(alight)

dlight = DirectionalLight('directionalLight')
dlight.setDirection(Vec3(1, 1, -1))
dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
dlightNP = render.attachNewNode(dlight)

render.clearLight()
render.setLight(alightNP)
render.setLight(dlightNP)

# World
world = BulletWorld()
world.setGravity(Vec3(0, 0, -9.81))
world.setDebugNode(debugNP.node())

#HeightField
height = 8.0
img = PNMImage(Filename('models/elevation.png'))
hshape = BulletHeightfieldShape(img, height, ZUp)
hnode = BulletRigidBodyNode('HGround')
hnode.addShape(hshape)
world.attachRigidBody(hnode)

#Terrian
terrain = GeoMipTerrain('terrain')
terrain.setHeightfield(img)

offset = img.getXSize() / 2.0 - 0.5
rootNP = terrain.getRoot()
rootNP.reparentTo(render)
rootNP.setSz(height)
rootNP.setPos(-offset, -offset, -height / 2.0)
terrain.generate()

#Player
speed = Vec3(0, 0, 0)

shape = BulletCapsuleShape(.25, .75, ZUp)
playerNode = BulletCharacterControllerNode(shape, 0.4, 'Player')
playerNode.setMaxJumpHeight(2.0)
playerNode.setJumpSpeed(4.0)
playerNP = render.attachNewNode(playerNode)
playerNP.setPos(-2, 0, 4)
playerNP.setH(45)
playerNP.setCollideMask(BitMask32.allOn())
world.attachCharacter(playerNP.node())
playerModel = Actor('models/soldier.egg',{"walk" : "models/soldier-ArmatureAction"})
playerModel.setScale(.25, .25, .25)
playerModel.flattenLight()
playerModel.reparentTo(playerNP)

inputState.watchWithModifiers('forward', 'w')
inputState.watchWithModifiers('left', 'a')
inputState.watchWithModifiers('reverse', 's')
inputState.watchWithModifiers('right', 'd')
inputState.watchWithModifiers('jump', 'space')
inputState.watchWithModifiers('turnLeft', 'q')
inputState.watchWithModifiers('turnRight', 'e')

#Camera
base.disableMouse()
props = WindowProperties()
props.setCursorHidden(True)
base.win.requestProperties(props)
base.cam.lookAt(playerNP.getPos())
heading = base.cam.getH()
pitch = - base.cam.getP()

#player movement
def processInput():
    omega = 0.0
    speed.setX(0)
    speed.setY(0)

    if inputState.isSet('forward'): speed.setY(2.5)
    if inputState.isSet('reverse'): speed.setY(-2.5)
    if inputState.isSet('left'):    speed.setX(-2.5)
    if inputState.isSet('right'):   speed.setX(2.5)
    if inputState.isSet('jump'):   playerNode.doJump()
    if inputState.isSet('turnLeft'):  omega = 120.0
    if inputState.isSet('turnRight'): omega = -120.0

    playerNP.node().setAngularMovement(omega)
    playerNP.node().setLinearMovement(speed, True)

#player animation
def animate():
    if(speed.getX() == 0 and speed.getY() == 0):
        playerModel.pose("walk", 15)
    else:
        if(playerModel.get_current_anim() == None):
            playerModel.loop("walk")


def moveCamera():
    global heading
    global pitch

    md = base.win.getPointer(0)

    x = md.getX()
    y = md.getY()

    if base.win.movePointer(0, 300, 300):
        heading = heading - (x - 300) * 0.2
        pitch = pitch - (y - 300) * 0.2

    base.cam.setHpr(heading, pitch, 0)

    playerNP.setH(heading)
    base.cam.setX(playerNP.getX() + 5 * math.sin(math.pi / 180.0 * playerNP.getH()))
    base.cam.setY(playerNP.getY() - 5 * math.cos(math.pi / 180.0 * playerNP.getH()))
    base.cam.setZ(playerNP.getZ() + 3)


# Update
def update(task):
    dt = globalClock.getDt()
    moveCamera()
    processInput()
    animate()
    world.doPhysics(dt)
    return task.cont


taskMgr.add(update, 'update')
base.run()