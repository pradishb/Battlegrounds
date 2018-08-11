from direct.directbase.DirectStart import base
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode
from panda3d.core import Point3, LineSegs, Geom, Vec3, BitMask32, CollisionRay, GeomNode, CollisionNode, NodePath


class Bullet:
    def __init__(self, world, gunPos, shootPos):
        self.world = world
        # print(gunPos)

        v = shootPos - gunPos
        v.normalize()
        v *= 10.0

        # Create bullet
        shape = BulletBoxShape(Vec3(0.01, 0.01, 0.01))
        body = BulletRigidBodyNode('Bullet')
        self.bodyNP = base.render.attachNewNode(body)
        self.bodyNP.node().addShape(shape)
        self.bodyNP.node().setMass(2.0)
        self.bodyNP.node().setLinearVelocity(v)
        self.bodyNP.setPos(gunPos)
        self.bodyNP.setCollideMask(BitMask32.allOn())

        bulletmodel = base.loader.loadModel("smiley")
        bulletmodel.setScale(0.01)
        bulletmodel.reparentTo(self.bodyNP)

        # Enable CCD
        self.bodyNP.node().setCcdMotionThreshold(1e-7)
        self.bodyNP.node().setCcdSweptSphereRadius(0.50)

        self.world.attachRigidBody(self.bodyNP.node())

        # Remove the bullet again after 1 second
        base.taskMgr.doMethodLater(1, self.removeBullet, 'removeBullet')
        
    def removeBullet(self, task):
        self.world.removeRigidBody(self.bodyNP.node())
        self.bodyNP.detachNode()
        return task.done

