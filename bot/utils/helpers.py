from typing import Tuple
from bot.database.models import User
from bot.utils.formulas import xp_formula
import ujson


with open("bot/levels.json", "r") as f:
    LEVELS = ujson.load(f)


async def get_create_user(user_id) -> User:
    user = await User.get(user_id)
    if user is None:
        user = await User.create(id=user_id)
        # user = await User.get(user_id)
    return user


def chunk(_list, amount: int):
    """Split an iterable object into smaller chunks

    Args:
        _list (iterable): the object to chunk
        amount (int): the amount of items in the new list

    """
    for name in range(0, len(_list), amount):
        yield _list[name : name + amount]


async def update_xp(user: User, modifier: float) -> Tuple[User, bool]:
    """**Use to give XP after a successful command.**

    USAGE:
    User, leveled_up = await update_xp(
        user=user, modifier=0
    )

    """

    modifier += 0.1

    xp = xp_formula(user, modifier)

    await user.update(xp=xp).apply()

    og_level = user.level

    user_level = 1
    for level, xp in LEVELS.items():
        if user.xp >= xp:
            user_level = int(level)
        else:
            break

    await user.update(level=user_level).apply()

    return (
        user,
        user_level != og_level,
    )
