from direct.directbase.DirectStart import base
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
        self.np = loader.loadModel("models/bullet.egg")
        self.np.setCollideMask(BitMask32(0x10))
        self.np.setScale(0.05)
        self.np.lookAt(y)
        self.np.reparentTo(base.render)

        vec = y - x
        vec.normalize()
        vec = vec * 100
        vec = vec + x
        bulletTravelPath = self.np.posInterval(1, vec, startPos=x)

        # Create and play the sequence that coordinates the intervals.
        bulletTravelAnimation = Sequence(bulletTravelPath, name="pandaPace")
        bulletTravelAnimation.start()
        base.taskMgr.doMethodLater(1, self.removeBullet, 'removeBullet')

    def removeBullet(self, task):
        self.np.detachNode()
        return task.done
