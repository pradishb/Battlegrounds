from direct.directbase.DirectStart import base
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode
from panda3d.core import Point3, LineSegs, Geom, Vec3, BitMask32, CollisionRay, GeomNode, CollisionNode, NodePath, LPoint3f
from raycollider import RayCollider
from direct.interval.IntervalGlobal import Sequence


class Bullet:
    def __init__(self, world, gunPos):
        self.gunPos = gunPos
        self.world = world

    def initialize(self):
        self.shootPos = RayCollider.getBulletHitPos()

    def initializeWithPos(self, x, y, z):
        self.shootPos = LPoint3f(x, y, z)

    def shoot(self):
        BulletModel(self.gunPos, self.shootPos)


class BulletModel:
    def __init__(self, x, y):
        self.np = loader.loadModel("smiley")
        self.np.setCollideMask(BitMask32(0x10))
        self.np.setScale(0.05)
        self.np.reparentTo(base.render)

        vec = y - x
        vec.normalize()
        vec = vec * 100
        vec = vec + x
        pandaPosInterval1 = self.np.posInterval(1, vec, startPos=x)

        # Create and play the sequence that coordinates the intervals.
        pandaPace = Sequence(pandaPosInterval1, name="pandaPace")
        pandaPace.start()
        base.taskMgr.doMethodLater(1, self.removeBullet, 'removeBullet')

    def removeBullet(self, task):
        self.np.detachNode()
        return task.done
