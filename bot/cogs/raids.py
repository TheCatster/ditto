import random

import discord
from discord.ext import commands

from bot.utils import create_embed, get_guild_prefix
from bot.database.models import Raid
from bot.utils.helpers import chunk, get_create_user, update_xp
from disputils import BotEmbedPaginator


class Raids(commands.Cog):
    """:video_game:"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Shows all available raids.", usage="raids")
    async def raids(self, ctx):
        raids = self.bot.raid_data

        raid_list = []

        try:
            for chunked in chunk(raids, 5):
                raid_list.append([
                                     f"\n\n**-** {'Gmax' if raid.gmax else ''} {'Shiny' if raid.shiny else ''} {raid.pokemon.capitalize()}"
                                     for raid in chunked])
        except Exception as e:
            print(e)
            await ctx.send("An error has occurred.")
            return

        if len(raids) > 0:
            description = []

            for page in raid_list:
                de_string = ""
                for item in page:
                    de_string += item
                description.append(de_string)

            embeds = [
                discord.Embed(
                    description=f"**Current Raids:**" + page,
                    color=discord.Colour.purple(),
                )
                for page in description
            ]

            paginator = BotEmbedPaginator(ctx, embeds)
            await paginator.run()
        else:
            await ctx.send("No raids running.")

    @commands.command(
        description="Shows the current queue for each gym, shows all if you don't include a gym name.",
        usage="queue [gym]",
    )
    async def queue(self, ctx, *, pokemon: str):
        raid = None
        for raid_id, raid in self.bot.raid_data.items():
            if raid.pokemon == pokemon.lower() and raid.guild_id == ctx.guild.id:
                raid = raid
                break

        if not raid:
            return

        users = [user for raid_id, user in self.bot.queue_data.items() if self.bot.queue_data[raid.id]]

        if len(users) > 0:
            description = []
            raid_pokemon = ""
            if raid.gmax:
                raid_pokemon += "Gmax "
            if raid.shiny:
                raid_pokemon += "Shiny "
            raid_pokemon += raid.pokemon.capitalize()

            try:
                user_list = [
                    [
                        f"**-** {self.bot.get_user(user.user_id).mention}\n"
                        for user in chunked
                    ]
                    for chunked in chunk(users, 5)
                ]
            except Exception as e:
                print(e)
                await ctx.send("An error has occurred.")
                return

            for page in user_list:
                de_string = ""
                for item in page:
                    de_string += item
                description.append(de_string)

            embeds = [
                discord.Embed(
                    title="Raid Queue",
                    description=f"**Current Pokemon:** "
                                f"{raid_pokemon}\n\n"
                                f"Current Queue:\n" + page,
                    color=discord.Colour.purple(),
                )
                for page in description
            ]

            try:
                for embed in embeds:
                    embed.set_thumbnail(url=self.bot.pokemon_images[pokemon.lower()])

            except Exception as e:
                print(e)
                await ctx.send(
                    "An image for this pokemon cannot be found... contact the dev regarding this issue."
                )
                return

            paginator = BotEmbedPaginator(ctx, embeds)
            await paginator.run()
        else:
            await ctx.send(
                "There is no raid running with that Pokemon, or you did not specify a "
                "Pokemon, try using this command again."
            )

    # TODO: Rewrite to GINO
    @commands.command(description='Adds you to the queue for the raid you entered.', usage='join <raid>')
    async def join(self, ctx, *, raid_pokemon: str):
        raid = None
        for raid_id, raid in self.bot.raid_data.items():
            if raid.pokemon == raid_pokemon.lower() and raid.guild_id == ctx.guild.id:
                raid = raid
                break

        if raid:
            host_id = raid.host_id
            queue = [user for raid_id, user in self.bot.queue_data.items() if self.bot.queue_data[f"{raid.id}+{ctx.message.author.id}"]]
            if len(queue) == 0:
                await ctx.send('No raid is running for this pokemon.')
                self.bot.raid_data.pop(raid.id, None)
                await raid.delete()
                return
            if ctx.message.author not in queue:
                self.bot.queue_data[f"{raid.id}+{ctx.message.author.id}"].raid_id = raid.id
                self.bot.queue_data[f"{raid.id}+{ctx.message.author.id}"].user_id = ctx.message.author.id
                self.bot.queue_data[f"{raid.id}+{ctx.message.author.id}"].guild_id = ctx.guild.id
                if len(queue) >= 3:
                    host = await get_create_user(host_id)

                    await update_xp(
                        user=host, modifier=0
                    )

                await ctx.send(f'Added to queue for the {raid.pokemon.capitalize()} raid!')
            else:
                await ctx.send('You are already in the queue for this raid.')
                return
        else:
            await ctx.send('No raid is running for this pokemon.')
            return

    """
        This is still being rewritten.
    @commands.command(description='Removes you from the queue for the raid you entered.', usage='leave <raid>')
    async def leave(self, ctx, *, raid_pokemon: str):
        async with aiosqlite.connect('cogs/db/pokemon.db') as conn:
            try:
                async with conn.execute('SELECT pokemon_name FROM Raids WHERE guild_id = ?', (ctx.guild.id,)) as c:
                    raids = list(dict.fromkeys([raid[0].lower() for raid in await c.fetchall()]))
                    raid = raid_pokemon.lower()

                    if raid in raids:
                        async with conn.execute('SELECT raid_id FROM Raids WHERE pokemon_name = ? COLLATE NOCASE',
                                                (raid,)) as c:
                            raid_id = await c.fetchone()
                            raid_id = raid_id[0]
                        async with conn.execute('SELECT user_id FROM Queue WHERE user_id = ? AND raid_id = ?',
                                                (ctx.message.author.id, raid_id)) as c:
                            queue = [user[0] for user in await c.fetchall()]
                            if ctx.message.author.id in queue:
                                await conn.execute('DELETE FROM Queue WHERE raid_id = ? AND guild_id = ? and user_id '
                                                   '= ?',
                                                   (raid_id, ctx.guild.id, ctx.message.author.id))
                                await conn.commit()
                                await logger_info(ctx)
                                await ctx.send(f'Removed from the queue for the {raid.capitalize()} raid!')
                            else:
                                await ctx.send('You are not in the queue for this raid.')
                                return
                    else:
                        await ctx.send('No such raid.')
                        return
            except Exception as e:
                print(e)
                await logger_error(ctx, e)
                return

    @commands.command(description='Create a raid if no other currently exists.',
                      usage='host <shiny: y/n> <gmax: y/n> <pokemon_name>')
    async def host(self, ctx, shiny: str, gmax: str, pokemon_name: str):
        async with aiosqlite.connect('cogs/db/pokemon.db') as conn:

            try:
                async with conn.execute('SELECT pokemon_name FROM Raids, Queue WHERE Queue.raid_id = Raids.raid_id '
                                        'AND Raids.guild_id = ? '
                                        ' AND Raids.guild_id = Queue.guild_id', (ctx.guild.id,)) as c:
                    raids = list(dict.fromkeys([raid[0].lower() for raid in await c.fetchall()]))
                    raid = pokemon_name.lower()
            except Exception as e:
                print(e)
                await logger_error(ctx, e)
                return

            if raid in raids:
                await ctx.send('There is already a raid running with this Pokemon in your server. Consider joining '
                               'that one!')
                return

            pokemon_name = pokemon_name.lower()
            gmax = gmax.lower()
            shiny = shiny.lower()

            with open('cogs/pokemon/data/pokemon.json', 'r') as f:
                pokemon = json.load(f).keys()
                if pokemon_name not in pokemon:
                    await ctx.send('This is not a valid Pokemon name, or it has been misspelled. '
                                   'Try running this command again.')
                    return

            if shiny != 'y' and shiny != 'n':
                await ctx.send('Your option for shiny is invalid, try running this command again.')
                return

            if gmax != 'y' and gmax != 'n':
                await ctx.send('Your option for gmax is invalid, try running this command again.')
                return

            try:
                await conn.execute('INSERT INTO Raids(guild_id, pokemon_name, shiny, gmax, host_id) '
                                   'VALUES(?, ?, ?, ?, ?)',
                                   (ctx.guild.id, pokemon_name.capitalize(), shiny, gmax, ctx.message.author.id))
                async with conn.execute('SELECT raid_id FROM Raids WHERE pokemon_name = ? and guild_id = ?',
                                        (pokemon_name.capitalize(), ctx.guild.id)) as c:
                    raid_id = await c.fetchone()
                    raid_id = raid_id[0]
                await conn.execute('INSERT INTO Queue(raid_id, user_id, guild_id) VALUES(?, ?, ?)',
                                   (raid_id, ctx.message.author.id, ctx.guild.id))
                await conn.commit()
                await logger_info(ctx)
            except Exception as e:
                print(e)

            await ctx.send(
                'Raid started, you have been automatically added to the queue, and you can check on the current '
                'raid using the queue command.'
                ' Invite your friends to join!')

            await ctx.send('**TIP:** In order to get XP, get 3 or more people to be in the queue!')

    @commands.command(description='Close a raid if you are the host or an admin.',
                      usage='close <pokemon_name>')
    async def close(self, ctx, pokemon_name: str):
        async with aiosqlite.connect('cogs/db/pokemon.db') as conn:
            try:
                async with conn.execute('SELECT pokemon_name FROM Raids, Queue WHERE Queue.raid_id = Raids.raid_id '
                                        'AND Raids.guild_id = ? '
                                        ' AND Raids.guild_id = Queue.guild_id', (ctx.guild.id,)) as c:
                    raids = list(dict.fromkeys([raid[0].lower() for raid in await c.fetchall()]))
                    raid = pokemon_name.lower()
            except Exception as e:
                print(e)
                await logger_error(ctx, e)
                return

            if raid not in raids:
                await ctx.send('This raid cannot be found. Please type in a valid Pokemon name.')
                return

            pokemon_name = pokemon_name.lower()

            async with conn.execute('SELECT raid_id FROM Raids WHERE pokemon_name = ? AND guild_id = ?',
                                    (pokemon_name.capitalize(), ctx.guild.id)) as c:
                raid_id = await c.fetchone()
                raid_id = raid_id[0]

            async with conn.execute('SELECT host_id FROM Raids WHERE raid_id = ? AND guild_id = ?',
                                    (raid_id, ctx.guild.id)) as c:
                raid_host = await c.fetchone()

                raid_host = raid_host[0]
                if raid_host != ctx.message.author.id or not ctx.message.author.guild_permissions.administrator:
                    await ctx.send('You did not host this raid, and are not an admin. Please get someone else to '
                                   'close it.')
                    return

            try:
                await conn.execute('DELETE FROM Raids WHERE pokemon_name = ? AND guild_id = ?',
                                   (pokemon_name.capitalize(), ctx.guild.id))
                await conn.execute('DELETE FROM Queue WHERE raid_id = ? AND guild_id = ?',
                                   (raid_id, ctx.guild.id))
                await logger_info(ctx)
                await conn.commit()
            except Exception as e:
                print(e)
                await logger_error(ctx, e)
                return

            await ctx.send('Raid has been closed, and queue has been purged!')
"""


def setup(bot):
    bot.add_cog(Raids(bot))
