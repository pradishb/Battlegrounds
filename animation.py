class Animation:
    def __init__(self, player):
        self.current = "idle"
        self.player = player

    def animate(self, xSpeed, ySpeed):
        if xSpeed == 0 and ySpeed == 0 and self.current != "pistol idle":
            self.current = "pistol idle"
            self.player.playerModel.loop("idle", partName="legs")
            self.player.playerModel.loop("idle", partName="hips")
            self.player.playerModel.pose("pistol", 0, partName="upperBody")
        elif xSpeed != 0 or ySpeed != 0 and self.current != "pistol walk":
            self.current = "pistol walk"
            self.player.playerModel.loop("walk", partName="legs")
            self.player.playerModel.loop("idle", partName="hips")
            self.player.playerModel.pose("pistol", 0, partName="upperBody")

        # if (xSpeed == 0 and ySpeed == 0):
        #     if (self.player.playerModel.get_current_anim() != "idle"):
        #         self.player.playerModel.loop("idle")
        # else:
        #     if (self.player.playerModel.get_current_anim() != "walk"):
        #         self.player.playerModel.loop("walk")
