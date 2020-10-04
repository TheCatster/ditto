from .config import Config
from .embeds import create_embed, wait_for_choice

config = Config()


def get_guild_prefix(_bot, guild_id):
    prefix = config.prefix
    try:
        guild_data = _bot.guild_data[guild_id]
        _prefix = guild_data.prefix
        if _prefix is not None:
            prefix = _prefix
    except KeyError:
        pass
    return prefix
