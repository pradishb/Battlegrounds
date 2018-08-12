class Animation:
    def __init__(self, player):
        self.current = "idle"
        self.player = player
        taskMgr.add(self.animate, 'animate')

    def animate(self, task):
        if self.player.health == 0 and self.current != "death":
            self.current = "death"
            self.player.playerModel.play("death")
        elif self.player.xSpeed == 0 and self.player.ySpeed == 0 and self.current != "pistol idle" and self.current != "death":
            self.current = "pistol idle"
            self.player.playerModel.loop("idle", partName="legs")
            self.player.playerModel.loop("idle", partName="hips")
            self.player.playerModel.pose("pistol", 0, partName="upperBody")
        elif (self.player.xSpeed != 0 or self.player.ySpeed != 0) and self.current != "pistol walk" and self.current != "death":
            self.current = "pistol walk"
            self.player.playerModel.loop("walk", partName="legs")
            self.player.playerModel.loop("idle", partName="hips")
            self.player.playerModel.pose("pistol", 0, partName="upperBody")
        return task.cont


