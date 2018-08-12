from direct.gui.OnscreenText import OnscreenText
from direct.directbase.DirectStart import base


class GameUI:
    font = base.loader.loadFont('./fonts/neuropol.ttf')
    font.setPixelsPerUnit(60)
    health = OnscreenText(text="Health = 100", pos=(-.5, .5), font=font, scale=0.1, fg=(0, 0, 0, 255))
    health.setColor(255, 255, 255, 255)
    display = OnscreenText(text="No Connection", pos=(0, 0), font=font, scale=0.25, fg=(0, 0, 0, 255))
    display.setColor(255, 255, 255, 255)

    @staticmethod
    def createDisplayUI(text):
        display = OnscreenText(text=text, pos=(0, 0), font=GameUI.font, scale=0.25, fg=(0, 0, 0, 255))
        display.setColor(255, 255, 255, 255)
        return display

    @staticmethod
    def updateHealth(value):
        GameUI.health.setText("Health : " + str(value))