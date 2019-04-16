import abc
from typing import Iterable

from backend.games.connector import Connector


class Game(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    async def play(self, participants: Iterable[str], connector: Connector):
        pass
