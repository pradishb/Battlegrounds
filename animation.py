class Animation:
    def __init__(self, player):
        self.current = "idle"
        self.player = player
        taskMgr.add(self.animate, 'animate')

    def animate(self, task):
        if self.player.health == 0 and self.current != "death":
            self.current = "death"
            self.player.playerModel.play("death")
        elif self.current == "shooting" or self.current == "shooting idle" or self.current == "shooting walk":
            if self.player.playerModel.get_current_frame(partName="upperBody") == 23:
                self.current = None
            if self.player.xSpeed == 0 and self.player.ySpeed == 0 and self.current != "shooting idle":
                self.current = "shooting idle"
                self.player.playerModel.loop("idle", partName="legs")
            elif (self.player.xSpeed != 0 or self.player.ySpeed != 0) and self.current != "shooting walk":
                self.current = "shooting walk"
                self.player.playerModel.loop("walk", partName="legs")
        elif self.current == "shoot" and self.current != "shooting":
            self.player.playerModel.play("pistol", partName="upperBody")
            self.current = "shooting"
        elif self.current != "death" and self.current != "shooting":
            if self.player.xSpeed == 0 and self.player.ySpeed == 0 and self.current != "pistol idle":
                self.current = "pistol idle"
                self.player.playerModel.loop("idle", partName="legs")
                self.player.playerModel.pose("pistol", 23, partName="upperBody")
            elif (self.player.xSpeed != 0 or self.player.ySpeed != 0) and self.current != "pistol walk":
                self.current = "pistol walk"
                self.player.playerModel.loop("walk", partName="legs")
                self.player.playerModel.pose("pistol", 23, partName="upperBody")
        return task.cont
