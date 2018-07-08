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
from direct.gui.OnscreenImage import LineSegs, deg2Rad, NodePath
import math
import sys

def makeArc(angleDegrees = 360, numSteps = 16):
    ls = LineSegs()

    angleRadians = deg2Rad(angleDegrees)

    for i in range(numSteps + 1):
        a = angleRadians * i / numSteps
        y = math.sin(a)
        x = math.cos(a)

        ls.drawTo(x, 0, y)


    node = ls.create()
    return NodePath(node)

#Debug
def toggleDebug():
    if debugNP.isHidden():
        debugNP.show()
    else:
        debugNP.hide()

base.setFrameRateMeter(True)
o = DirectObject()
o.accept('f1', toggleDebug)
o.accept('escape', sys.exit, [0])

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
walk_speed = 1.5

shape = BulletCapsuleShape(.2, .6, ZUp)
playerNode = BulletCharacterControllerNode(shape, 0.4, 'Player')
playerNode.setMaxJumpHeight(2.0)
playerNode.setJumpSpeed(4.0)
playerNP = render.attachNewNode(playerNode)
playerNP.setPos(-2, 0, 4)
playerNP.setCollideMask(BitMask32.allOn())
world.attachCharacter(playerNP.node())
playerModel = Actor('models/soldier.egg', {"idle" : "models/soldier_ani_idle.egg",
                                           "walk": "models/soldier_ani_walk.egg"})
myTexture = loader.loadTexture("models/soldier_texture.png")
playerModel.setTexture(myTexture,1)
playerModel.setH(90)
playerModel.setScale(.06)
playerModel.setZ(-.45)
playerModel.flattenLight()
playerModel.setLightOff()
playerModel.reparentTo(playerNP)

inputState.watchWithModifiers('forward', 'w')
inputState.watchWithModifiers('left', 'a')
inputState.watchWithModifiers('reverse', 's')
inputState.watchWithModifiers('right', 'd')
inputState.watchWithModifiers('jump', 'space')


#Camera
base.disableMouse()
props = WindowProperties()
props.setCursorHidden(True)
base.win.requestProperties(props)
heading = 0
pitch = 40

#Pointer
imageObject = makeArc()
imageObject.setSx(.02)
imageObject.setSy(.02)
imageObject.setSz(.02)
imageObject.reparent_to(aspect2d)

#player movement
def processInput():
    omega = 0.0
    speed.setX(0)
    speed.setY(0)

    if inputState.isSet('forward'): speed.setY(walk_speed)
    if inputState.isSet('reverse'): speed.setY(-walk_speed)
    if inputState.isSet('left'):    speed.setX(-walk_speed)
    if inputState.isSet('right'):   speed.setX(walk_speed)
    if inputState.isSet('jump'):   playerNode.doJump()

    playerNP.node().setLinearMovement(speed, True)

#player animation
def animate():
    if(speed.getX() == 0 and speed.getY() == 0):
        if (playerModel.get_current_anim() != "idle"):
            playerModel.loop("idle")
    else:
        if (playerModel.get_current_anim() != "walk"):
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
        if (pitch < -30.0): pitch = -30.0
        elif (pitch > 45.0): pitch = 45.0

    base.cam.setHpr(heading, pitch, 0)

    playerNP.setH(heading)
    base.cam.setX(playerNP.getX() + 3 * math.sin(math.pi / 180.0 * playerNP.getH()))
    base.cam.setY(playerNP.getY() - 3 * math.cos(math.pi / 180.0 * playerNP.getH()))
    base.cam.setZ(playerNP.getZ() - 0.05 * pitch + .7)


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