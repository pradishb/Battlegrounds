import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import Texture, TextureStage, DirectionalLight, AmbientLight, TexGenAttrib, VBase4


class Sky():
    def __init__(self):
        self.sphere = loader.loadModel("models/InvertedSphere.egg")
        # Load a sphere with a radius of 1 unit and the faces directed inward.

        self.sphere.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldPosition)
        self.sphere.setTexProjector(TextureStage.getDefault(), render, self.sphere)
        self.sphere.setTexPos(TextureStage.getDefault(), 0, 0, 0)
        self.sphere.setTexScale(TextureStage.getDefault(), .5)
        # Create some 3D texture coordinates on the sphere. For more info on this, check the Panda3D manual.

        tex = loader.loadCubeMap("models/Daylight Box_#.bmp")
        self.sphere.setTexture(tex)
        # Load the cube map and apply it to the sphere.

        self.sphere.setLightOff()
        # Tell the sphere to ignore the lighting.
        self.sphere.setP(-90)
        self.sphere.setScale(1000)

        # Increase the scale of the sphere so it will be larger than the scene.

        self.sphere.reparentTo(render)
        # Reparent the sphere to render so you can see it.

