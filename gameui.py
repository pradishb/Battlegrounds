from direct.gui.OnscreenText import OnscreenText
from direct.directbase.DirectStart import base


class GameUI:
    font = base.loader.loadFont('./fonts/neuropol.ttf')
    font.setPixelsPerUnit(60)
    health = OnscreenText(text="Health = 100", pos=(-.5, .5), font=font, scale=0.1, fg=(0, 0, 0, 255))
    health.setColor(255, 255, 255, 255)

    @staticmethod
    def showInGameUI():
        pass

    @staticmethod
    def updateHealth(value):
        GameUI.health.setText("Health : " + str(value))