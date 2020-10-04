import asyncio
from datetime import datetime

import discord
from discord.ext import commands

from bot.database.models import User
from bot.utils import create_embed

# report_guild_id = 492701249192460298
from bot.utils.helpers import get_create_user

report_channel_id = 701158767370305536


class Users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")
        await asyncio.sleep(5)
        await self.update_bans()

    async def update_bans(self):
        banned_users = await User.query.where(User.host_banned).gino.all()
        self.bot.host_banned_users = list()
        for user in banned_users:
            self.bot.host_banned_users.append(user.user_id)

    @commands.command()
    async def report(self, ctx, user_id: int, *, message: str = None):
        """*Report users for invalid raid listings*

        `message` is optional as a report reason
        **Usage**: `{prefix}report <user-id> [message]`
        **Example**: `{prefix}report 385437114969358338 invalid listing`
        """
        user = await get_create_user(user_id)
        user_reports = user.report_count
        author = await get_create_user(ctx.author.id)
        author_reports = author.reports_created_count
        channel = self.bot.get_channel(report_channel_id)
        embed = await create_embed(title="User Report")
        embed = await self.add_author_embed(embed, user_id)
        embed.set_footer(text=f"Reported: <{user_id}> by <{ctx.author.id}>")
        if message:
            embed.add_field(name="Report", value=message, inline=False)
        embed.add_field(name="Previous reports", value=user_reports)
        embed.add_field(name="Author report count", value=author_reports)
        await user.update(report_count=user_reports + 1).apply()
        await author.update(reports_created_count=author_reports + 1).apply()
        await channel.send(embed=embed)
        embed = await create_embed(
            description=f"Report sent! Sorry for the inconvenience."
        )
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def raid_ban(self, ctx, user_id: int):
        user = await get_create_user(user_id)
        await user.update(host_banned=True).apply()
        embed = await create_embed(title="User banned")
        embed = await self.add_author_embed(embed, user_id)
        embed.set_footer(text=f"Banned: <{user_id}> by <{ctx.author.id}>")
        await ctx.send(embed=embed)
        await self.update_bans()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def raid_unban(self, ctx, user_id: int):
        user = await get_create_user(user_id)
        await user.update(host_banned=False).apply()
        embed = await create_embed(title="User unbanned")
        embed = await self.add_author_embed(embed, user_id)
        embed.set_footer(text=f"Unbanned: <{user_id}> by <{ctx.author.id}>")
        await ctx.send(embed=embed)
        await self.update_bans()

    async def add_author_embed(self, embed, user_id):
        reported_user = self.bot.get_user(user_id)
        if reported_user is None:
            embed.description = f"<@{user_id}> not found."
        else:
            embed.set_author(name=reported_user, icon_url=reported_user.avatar_url)
        return embed


def setup(bot):
    bot.add_cog(Users(bot))
