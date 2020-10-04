import random

from bot.database.models import User


def xp_formula(player_db: User, modifier: float) -> int:
    if player_db.level > 4:
        xp = player_db.xp + abs(
            int(
                (
                        (
                                (
                                        1
                                        * random.randint(1, 10)
                                        * abs(player_db.level - (player_db.level * 0.4))
                                )
                                / (5 * 1)
                        )
                        * (
                                (
                                        pow(
                                            (
                                                    (2 * abs(player_db.level - (player_db.level * 0.4)))
                                                    + 10
                                            ),
                                            2.5,
                                        )
                                        / pow(
                                    (
                                            abs(player_db.level - (player_db.level * 0.4))
                                            + player_db.level
                                            + 10
                                    ),
                                    2.5,
                                )
                                )
                                + 1
                        )
                        * modifier
                )
            )
        )
    else:
        xp = player_db.xp + abs(random.randint(1, 5))
    return xp
