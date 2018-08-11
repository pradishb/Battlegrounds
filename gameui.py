from direct.gui.OnscreenText import OnscreenText
from direct.directbase.DirectStart import base


class GameUI:
    font = base.loader.loadFont('./fonts/neuropol.ttf')
    font.setPixelsPerUnit(60)

    @staticmethod
    def showInGameUI():
        textObject = OnscreenText(text="Health = 100", pos=(-.5, .5), font=GameUI.font, scale=0.1, fg=(0, 0, 0, 255))
        textObject.setColor(255, 255, 255, 255)