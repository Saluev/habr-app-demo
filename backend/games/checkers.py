import logging
from typing import Iterable

from backend.games.connector import Connector
from backend.games.game import Game


MARKS = "xo"


class Checkers(Game):

    async def play(self, participants: Iterable[str], connector: Connector):
        participants = list(participants)
        if len(participants) != 2:
            raise ValueError(f"checkers: {len(participants)} participants is not supported!")

        logger = logging.getLogger("checkers")
        logger.debug("Starting game of checkers.")

        marks = list(MARKS)
        field = [["", "", ""], ["", "", ""], ["", "", ""]]
        winner = unknown

        async def broadcast_state():
            for p, can_make_turn in zip(participants, (True, False)):
                await connector.push_event(p, {
                    "kind": "state",
                    "can_make_turn": can_make_turn and winner is unknown,
                    "field": field,
                    "winner": {unknown: None, nobody: "nobody"}.get(winner, winner),
                })

        await broadcast_state()

        while winner is unknown:
            turn = await _get_turn(connector, field, participants[0])
            field[turn["i"]][turn["j"]] = marks[0]
            participants.reverse()
            marks.reverse()
            winner = _get_winner(field)
            if winner is not unknown and winner is not nobody:
                winner = dict(zip(marks, participants))[winner]
            await broadcast_state()

        logger.debug("Finishing game of checkers.")


unknown = object()
nobody = object()


async def _get_turn(connector, field, player) -> dict:
    while True:
        action = await connector.wait_action_from(player)
        try:
            kind = action["kind"]
            i, j = action["i"], action["j"]
            if kind == "turn" and field[i][j] == "":
                return action
        except (KeyError, TypeError, IndexError):
            pass
        logging.getLogger("checkers").debug("Ignoring action %r", action)


def _get_winner(field):
    for mark in MARKS:
        if any(tuple(row) == (mark,) * 3 for f in (field, zip(*field)) for row in f):
            return mark
        if any(f[0][0] == f[1][1] == f[2][2] == mark for f in (field, field[::-1])):
            return mark
    if all(mark != "" for row in field for mark in row):
        return nobody
    return unknown
