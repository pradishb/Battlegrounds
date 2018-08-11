import direct.directbase.DirectStart
from pandac.PandaModules import *


class RayCollider():
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
    def getObjectHit():  # mpos is the position of the mouse on the screen
        RayCollider.pickerRay.setFromLens(base.camNode, 0, 0)
        RayCollider.picker.traverse(render)
        if RayCollider.queue.getNumEntries() > 0:
            RayCollider.queue.sortEntries()
            RayCollider.pickedObj = RayCollider.queue.getEntry(0).getIntoNodePath()
            # axis = loader.loadModel('zup-axis.egg')
            # axis.reparentTo(render)
            # point = self.queue.getEntry(0).getSurfacePoint(render)
            # normal = self.queue.getEntry(0).getSurfaceNormal(render)
            # axis.setPos(point)
            # axis.lookAt(point + normal)
            # axis.setScale(0.05)
            return RayCollider.queue.getEntry(0).getSurfacePoint(render)
        pFrom = Point3()
        pTo = Point3()
        base.camLens.extrude((0, 0), pFrom, pTo)

        pTo = base.render.getRelativePoint(base.cam, pTo)
        return pTo