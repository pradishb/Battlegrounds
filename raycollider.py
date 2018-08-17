import direct.directbase.DirectStart
from panda3d.bullet import BulletBoxShape, BulletGhostNode
from pandac.PandaModules import *


class LineSeg:
    def __init__(self, x=(0, 0, 0), y=(0, 0, 0)):
        line = LineSegs()
        line.setColor(0, 1, 0, 1)
        line.drawTo(x)
        line.drawTo(y)
        self.node = line.create()
        self.np = base.render.attachNewNode(self.node)

    def update(self, x, y):
        line = LineSegs()
        line.setColor(0, 1, 0, 1)
        line.drawTo(x)
        line.drawTo(y)
        self.node = line.create()
        self.np.detachNode()
        self.np = base.render.attachNewNode(self.node)


class RayCollider():
    # setup eyepos
    eyepos = LineSegs()
    eyepos.setColor(0, 1, 0, 1)
    eyepos.drawTo(0, 0, 0)
    eyepos.setThickness(30)
    node = eyepos.create()
    eyeNP = base.render.attachNewNode(node)

    playerHitId = None

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
            RayCollider.eyeNP.setPos(point)
            RayCollider.playerHitId = None
            if RayCollider.queue.getEntry(0).getIntoNodePath().getParent().getName() == "__Actor_modelRoot":
                body_part = RayCollider.queue.getEntry(0).getIntoNodePath().getParent().getParent().getParent().getName()
                if body_part != "mixamorig:RightHand":
                    RayCollider.playerHitId = body_part
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

