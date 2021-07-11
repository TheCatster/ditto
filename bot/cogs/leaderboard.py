from discord.ext import commands

from bot.database.models import User
from bot.utils import create_embed


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.command(aliases=["leader", "lead", "board", "top"])
    async def leaderboard(self, ctx):
        """*Shows the top 10 players in all servers.*
        **Example**: `{prefix}`leaderboard"""
        leaders = await User.query.order_by(User.xp.desc()).limit(10).gino.all()

        board = [(f"<@{player.id}>", player.level, player.xp) for player in leaders]
        description = ""

        for user in board:
            description += f"**{board.index(user) + 1}.** {user[0]} | Level: {user[1]} | XP: {user[2]}\n"
        msg = await create_embed(
            title=f"{str(ctx.guild)}" "'s Raid Leaderboard", description=description
        )

        await ctx.send(embed=msg)


def setup(bot):
    bot.add_cog(Levels(bot))
