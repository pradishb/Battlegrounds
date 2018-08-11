import direct.directbase.DirectStart
from panda3d.bullet import BulletBoxShape, BulletGhostNode
from pandac.PandaModules import *


class LineSeg:
    def __init__(self, x=(0, 0, 0), y=(0, 0, 0)):
        eyepos = LineSegs()
        eyepos.setColor(0, 1, 0, 1)
        eyepos.drawTo(x)
        eyepos.drawTo(y)
        self.node = eyepos.create()
        self.np = base.render.attachNewNode(self.node)

    def update(self, x, y):
        eyepos = LineSegs()
        eyepos.setColor(0, 1, 0, 1)
        eyepos.drawTo(x)
        eyepos.drawTo(y)
        self.node = eyepos.create()
        self.np.detachNode()
        self.np = base.render.attachNewNode(self.node)


class RayCollider():
    # setup eyepos
    eyepos = LineSegs()
    eyepos.setColor(0, 1, 0, 1)
    eyepos.drawTo(0, 0, 0)
    eyepos.setThickness(30)
    node = eyepos.create()
    np = base.render.attachNewNode(node)

    # cameraToPointer = LineSeg()

    # setup collision stuff
    picker = CollisionTraverser()
    queue = CollisionHandlerQueue()

    pickerNode = CollisionNode('mouseRay')
    pickerNP = base.cam.attachNewNode(pickerNode)

    pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())

    pickerRay = CollisionRay()

    pickerNode.addSolid(pickerRay)

    picker.addCollider(pickerNP, queue)

    @staticmethod
    def getBulletHitPos():
        RayCollider.pickerRay.setFromLens(base.camNode, 0, 0)
        RayCollider.picker.traverse(render)
        if RayCollider.queue.getNumEntries() > 0:
            RayCollider.queue.sortEntries()

            point = RayCollider.queue.getEntry(0).getSurfacePoint(render)
            RayCollider.np.setPos(point)
            print(RayCollider.queue.getEntry(0).getIntoNodePath().getParent().getParent().getParent().getName())
            return point
        pFrom = Point3()
        pTo = Point3()
        base.camLens.extrude((0, 0), pFrom, pTo)
        pTo = base.render.getRelativePoint(base.cam, pTo)
        return pTo

    @staticmethod
    def getObjectHit():
        pFrom = Point3()
        pTo = Point3()
        base.camLens.extrude((0, 0), pFrom, pTo)
        pFrom = base.render.getRelativePoint(base.cam, pFrom)
        pTo = base.render.getRelativePoint(base.cam, pTo)

        return pTo

