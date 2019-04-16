import logging
import random
from typing import Iterable

from backend.games.connector import Connector
from backend.games.game import Game


class Minesweeper(Game):

    async def play(self, participants: Iterable[str], connector: Connector, nmines: int = 99):
        participants = list(participants)

        m, n = 16, 30

        logger = logging.getLogger("minesweeper")
        logger.debug("Starting game of minesweeper %d x %d for %d players.", m, n, len(participants))

        field, stats = _generate_random_field(m, n, nmines)
        mask = [[closed] * n for _ in range(m)]
        can_make_turn = True

        async def broadcast_state():
            await connector.broadcast_event(participants, {
                "kind": "state",
                "can_make_turn": can_make_turn,
                "field": [
                    [
                        {
                            closed: "closed",
                            open: "mine" if field[i][j] is mine else str(stats[i][j]),
                            marked: "marked",
                        }[mask[i][j]]
                        for j in range(n)
                    ]
                    for i in range(m)
                ]
            })

        await broadcast_state()

        while can_make_turn:
            action = await _get_action(connector, mask, participants)
            i, j = action["i"], action["j"]
            kind = action["kind"]
            if kind == "mark":
                mask[i][j] = marked
            elif kind == "unmark":
                mask[i][j] = open
            elif kind == "open":
                mask[i][j] = open
                if field[i][j] is mine:
                    can_make_turn = False
                elif stats[i][j] != 0:
                    pass  # we opened it, everything's fine
                else:
                    # We have to open all adjacent empty cells, and so on.
                    _open_empty_cells(i, j, field, mask, stats)
            await broadcast_state()


def _open_empty_cells(i, j, field, mask, stats):
    m, n = len(field), len(field[0])
    queue = [(i, j)]

    def neighbours(i, j):
        return (
            (i+di, j+dj)
            for (di, dj) in [(-1, 0), (1, 0), (0, -1), (0, 1)]
            if 0 <= i + di < m and 0 <= j + dj < n
        )

    while queue:
        i, j = queue.pop()
        mask[i][j] = open
        queue.extend((ni, nj) for ni, nj in neighbours(i, j) if stats[ni][nj] == 0 and mask[ni][nj] is not open)


def _generate_random_field(m, n, nmines):
    field = [[empty] * n for _ in range(m)]
    for _ in range(nmines):
        while True:
            i, j = random.randint(0, m - 1), random.randint(0, n - 1)
            if field[i][j] == "":
                field[i][j] = mine
                break

    stats = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            stats[i][j] = sum(
                1
                for di in (-1, 0, 1)
                for dj in (-1, 0, 1)
                if 0 <= i + di < m and 0 <= j + dj < n and field[i + di][j + dj] is mine
            )

    return field, stats


async def _get_action(connector, mask, players) -> dict:
    while True:
        action = await connector.wait_action_from_any_of(players)
        try:
            kind = action["kind"]
            i, j = action["i"], action["j"]
            if mask[i][j] is closed and kind in {"open", "mark"}:
                return action
            if mask[i][j] is marked and kind == "unmark":
                return action
        except (KeyError, TypeError, IndexError):
            pass
        logging.getLogger("minesweeper").debug("Ignoring action %r", action)


# Field cells
empty = object()
mine = object()

# Mask cells
closed = object()
open = object()
marked = object()
