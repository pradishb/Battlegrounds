class Animation:
    current = "idle"

    @staticmethod
    def animate(player, xSpeed, ySpeed):
        if xSpeed == 0 and ySpeed == 0 and Animation.current != "pistol idle":
            Animation.current = "pistol idle"
            player.playerModel.loop("idle", partName="legs")
            player.playerModel.loop("idle", partName="hips")
            player.playerModel.pose("pistol", 0, partName="upperBody")
        elif xSpeed > 0 or ySpeed > 0 and Animation.current != "pistol walk":
            Animation.current = "pistol walk"
            player.playerModel.loop("walk", partName="legs")
            player.playerModel.loop("idle", partName="hips")
            player.playerModel.pose("pistol", 0, partName="upperBody")

        # if (xSpeed == 0 and ySpeed == 0):
        #     if (player.playerModel.get_current_anim() != "idle"):
        #         player.playerModel.loop("idle")
        # else:
        #     if (player.playerModel.get_current_anim() != "walk"):
        #         player.playerModel.loop("walk")
