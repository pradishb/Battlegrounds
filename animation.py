class Animation:
    def __init__(self, player):
        self.current = "idle"
        self.player = player

    def animate(self, xSpeed, ySpeed):
        if self.player.health == 0 and self.current != "death":
            self.current = "death"
            self.player.playerModel.play("death")
        elif xSpeed == 0 and ySpeed == 0 and self.current != "pistol idle" and self.current != "death":
            self.current = "pistol idle"
            self.player.playerModel.loop("idle", partName="legs")
            self.player.playerModel.loop("idle", partName="hips")
            self.player.playerModel.pose("pistol", 0, partName="upperBody")
        elif (xSpeed != 0 or ySpeed != 0) and self.current != "pistol walk" and self.current != "death":
            self.current = "pistol walk"
            self.player.playerModel.loop("walk", partName="legs")
            self.player.playerModel.loop("idle", partName="hips")
            self.player.playerModel.pose("pistol", 0, partName="upperBody")


