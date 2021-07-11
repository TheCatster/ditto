import discord
from discord.ext import commands

from bot.database.models import Profile
from bot.utils import create_embed, get_guild_prefix
from bot.utils.helpers import get_create_user


async def query_profile(user_id: int):
    """: query profile, create if not exist"""
    profile = await Profile.get(user_id)
    if profile is None:
        profile = await Profile.create(user_id=user_id)
    return profile


async def send_changed_embed(ctx, changed: str, before: str, after: str):
    embed = await create_embed(description=f"*{changed} changed*")
    embed.set_thumbnail(url=ctx.author.avatar_url)
    embed.add_field(name="From", value=before)
    embed.add_field(name="To", value=after)
    await ctx.send(embed=embed)


class Profiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{type(self).__name__} Cog ready.")

    @commands.group(invoke_without_command=True, pass_context=True)
    async def profile(self, ctx, user_check: discord.User = None):
        """*Look up your or your friends profile*

        `[user]` is optional and either a user-id or a user mention
        **Usage**: `{prefix}profile [user]`
        **Example**: `{prefix}profile`

        To setup your own profile use the following commands
        **Usage**: `{prefix}profile <key> <value>`
        **Possible keys**:
            `island, name, fruit, hemisphere, fc, flower, airport, timezone`
        **Examples**:
            `{prefix}profile name Ditto`
            `{prefix}profile fc SW-000-0000`
            `{prefix}profile timezone NYC`
        """
        author = user_check
        if author is None:
            author = ctx.author
        user = await get_create_user(ctx.message.author.id)
        profile = await query_profile(user.id)

        embed = await create_embed()
        if user.level is not None:
            embed.add_field(name=":level_slider: Level", value=user.level)
        if user.xp is not None:
            embed.add_field(name=":bar_chart: XP", value=user.xp)
        if user.times_hosted is not None:
            embed.add_field(name=":metal: Times Hosted", value=user.times_hosted)
        if profile.user_name != "Not Set":
            embed.add_field(name="Character Name", value=profile.user_name)
            embed.add_field(name="\u200c", value="\u200c")
        if profile.timezone:
            embed.add_field(name=":clock130: Timezone", value=profile.timezone)
        if profile.friend_code != "Not Set":
            embed.add_field(name="Friend Code", value=profile.friend_code)

        if embed.fields:
            embed.set_thumbnail(url=author.avatar_url)
            embed.set_footer(text=f"Profile of {author.name}#{author.discriminator}")
        else:
            if user_check:
                embed.description = (
                    f"{user_check.mention} hasn't configured their profile yet!"
                )
            else:
                prefix = get_guild_prefix(self.bot, ctx.guild.id)
                embed.description = (
                    f"**You haven't configured your profile yet!**\n"
                    f"To configure your profile use: \n`{prefix}profile <key> <value>`\n"
                    f"**Possible keys**: \n"
                    f"`name, fc, timezone`\n"
                    f"**Examples**:\n"
                    f"`{prefix}profile name Ditto`\n"
                    f"`{prefix}profile fc SW-000-0000`\n"
                    f"`{prefix}profile timezone NYC`\n"
                )
        await ctx.send(embed=embed)

    @profile.command(aliases=["name", "username"])
    async def character(self, ctx, *, character_name: str):
        profile = await query_profile(ctx.author.id)
        await send_changed_embed(
            ctx,
            changed="Character name",
            before=profile.user_name,
            after=character_name,
        )
        await profile.update(user_name=character_name).apply()

    @profile.command(aliases=["fc", "code"])
    async def friendcode(self, ctx, friend_code: str):
        profile = await query_profile(ctx.author.id)
        friend_code = friend_code.upper()
        if "SW-" not in friend_code:
            friend_code = f"SW-{friend_code}"
        await send_changed_embed(
            ctx,
            changed="Friend code",
            before=profile.friend_code,
            after=friend_code,
        )
        await profile.update(friend_code=friend_code).apply()

    @profile.command()
    async def timezone(self, ctx, *, timezone: str):
        profile = await query_profile(ctx.author.id)
        before = profile.timezone
        if not before:
            before = "Not Set"
        await profile.update(timezone=timezone).apply()
        await send_changed_embed(
            ctx, changed="Timezone", before=before, after=profile.timezone
        )


def setup(bot):
    bot.add_cog(Profiles(bot))
