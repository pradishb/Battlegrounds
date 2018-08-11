from direct.directbase.DirectStart import base
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode
from panda3d.core import Point3, LineSegs, Geom, Vec3, BitMask32, CollisionRay, GeomNode, CollisionNode


class Bullet:
    prim = LineSegs()

    bullets = []

    def __init__(self, world):
        self.world = world

    def removeBullet(self, task):
        if len(Bullet.bullets) < 1: return

        bulletNP = Bullet.bullets.pop(0)
        self.world.removeRigidBody(bulletNP.node())

        return task.done

    def update(self):
        # pMouse = (0, 0)
        # pFrom = Point3()
        # pTo = Point3()
        # myLens = base.camLens.__copy__
        # base.camLens.extrude(pMouse, pFrom, pTo)
        #
        # pFrom = base.render.getRelativePoint(base.cam, pFrom)
        # pTo = base.render.getRelativePoint(base.cam, pTo)

        pickerNode = CollisionNode('mouseRay')
        pickerNP = base.camera.attachNewNode(pickerNode)
        pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        pickerRay = CollisionRay()
        pickerNode.addSolid(pickerRay)
        myTraverser.addCollider(pickerNP, myHandler)
        pickerRay.setFromLens(base.camNode, 0, 0)

        # Bullet.prim.drawTo(pFrom)
        # Bullet.prim.drawTo(pTo)
        # node = Bullet.prim.create()
        # np = base.render.attachNewNode(node)
        #
        # # Calculate initial velocity
        # v = pTo - pFrom
        # v.normalize()
        # v *= 100.0
        #
        # # Create bullet
        # shape = BulletBoxShape(Vec3(0.5, 0.5, 0.5))
        # body = BulletRigidBodyNode('Bullet')
        # bodyNP = base.render.attachNewNode(body)
        # bodyNP.node().addShape(shape)
        # bodyNP.node().setMass(2.0)
        # bodyNP.node().setLinearVelocity(v)
        # bodyNP.setPos(pFrom)
        # bodyNP.setCollideMask(BitMask32.allOn())
        #
        # bulletmodel = base.loader.loadModel("models/m1911.egg")
        # bulletmodel.setScale(0.05)
        # bulletmodel.reparentTo(bodyNP)
        #
        # # Enable CCD
        # bodyNP.node().setCcdMotionThreshold(1e-7)
        # bodyNP.node().setCcdSweptSphereRadius(0.50)
        #
        # self.world.attachRigidBody(bodyNP.node())
        #
        # # Remove the bullet again after 1 second
        # Bullet.bullets.append(bodyNP)
        # base.taskMgr.doMethodLater(1, self.removeBullet, 'removeBullet')
