from direct.directbase.DirectStart import base
from panda3d.core import Point3, LineSegs, Geom


class Bullet:
    prim = LineSegs()

    def update(self):
        pMouse = (0, 0)
        pFrom = Point3()
        pTo = Point3()
        base.camLens.extrude(pMouse, pFrom, pTo)

        pFrom = base.render.getRelativePoint(base.cam, pFrom)
        pTo = base.render.getRelativePoint(base.cam, pTo)
        Bullet.prim.drawTo(pFrom)
        Bullet.prim.drawTo(pTo)
        node = Bullet.prim.create()
        np = base.render.attachNewNode(node)