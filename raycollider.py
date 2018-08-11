import direct.directbase.DirectStart
from pandac.PandaModules import *


class RayCollider():
    def __init__(self):
        # setup collision stuff

        self.picker = CollisionTraverser()
        self.queue = CollisionHandlerQueue()

        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = base.cam.attachNewNode(self.pickerNode)

        self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())

        self.pickerRay = CollisionRay()

        self.pickerNode.addSolid(self.pickerRay)

        self.picker.addCollider(self.pickerNP, self.queue)

        # this holds the object that has been picked
        self.pickedObj = None

        base.accept('mouse1', self.printMe)

    # this function is meant to flag an object as being somthing we can pick
    def makePickable(self, newObj):
        newObj.setTag('pickable', 'true')

    # this function finds the closest object to the camera that has been hit by our ray
    def getObjectHit(self, mpos):  # mpos is the position of the mouse on the screen
        self.pickedObj = None  # be sure to reset this
        self.pickerRay.setFromLens(base.camNode, 0, 0)
        self.picker.traverse(render)
        if self.queue.getNumEntries() > 0:
            self.queue.sortEntries()
            self.pickedObj = self.queue.getEntry(0).getIntoNodePath()

            axis = loader.loadModel('zup-axis.egg')
            axis.reparentTo(render)
            point = self.queue.getEntry(0).getSurfacePoint(render)
            normal = self.queue.getEntry(0).getSurfaceNormal(render)
            axis.setPos(point)
            axis.lookAt(point + normal)
            axis.setScale(0.05)

            parent = self.pickedObj.getParent()
            self.pickedObj = None

            while parent != render:
                if parent.getTag('pickable') == 'true':
                    self.pickedObj = parent
                    return self.queue.getEntry(0).getSurfacePoint(render)
                else:
                    parent = parent.getParent()
        return None

    def getPickedObj(self):
        return self.pickedObj

    def printMe(self):
        print(self.getObjectHit(base.mouseWatcherNode.getMouse()))
        print(self.pickedObj)