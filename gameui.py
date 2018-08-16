from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode


class GameUI:
    font = base.loader.loadFont('./fonts/neuropol.ttf')
    font.setPixelsPerUnit(60)

    @staticmethod
    def createDisplayUI(text):
        display = OnscreenText(text=text, pos=(0, 0), font=GameUI.font, scale=0.25, fg=(1, 1, 1, 1))
        return display

    @staticmethod
    def createWhiteBgUI(text):
        display = OnscreenText(text=text, pos=(-1.32, 0.9), font=GameUI.font, scale=0.1, fg=(0, 0, 0, 1),
                                     bg=(1, 1, 1, 1), align=TextNode.ALeft)
        return display