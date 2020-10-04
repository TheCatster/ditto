import asyncio

import discord
from discord.ext import commands

from bot.database.models import User
from bot.utils import create_embed
from bot.utils.helpers import get_create_user

# report_guild_id = 492701249192460298
report_channel_id = 701158767370305536


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.has_guild_permissions(manage_guild=True)
    @commands.command()
    async def leaderboard(self, ctx):
        """*Adds XP to the user*

        **Usage**: `{prefix}leaderboard`
        **Example**: `{prefix}leaderboard`
        """

        await get_create_user(ctx.message.author.id)
        embed = await create_embed(description=f"Here are the top 10 members!")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Levels(bot))
