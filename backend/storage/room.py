import abc
from typing import Iterable, List


class Room(object):
    def __init__(self, id: str = None, kind: str = None, participants: List[str] = None):
        self.id = id
        self.kind = kind
        self.participants = participants

    def is_complete(self):
        return len(self.participants) == 2


class RoomDAO(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create(self, room: Room) -> Room:
        pass

    @abc.abstractmethod
    def update(self, room: Room) -> Room:
        pass

    @abc.abstractmethod
    def get_all(self) -> Iterable[Room]:
        pass

    @abc.abstractmethod
    def get_by_id(self, room_id: str) -> Room:
        pass

    @abc.abstractmethod
    def add_participant(self, room_id: str, participant_id: str):
        pass


class RoomManager(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def choose_room_for_participant(self, participant_id: str) -> (str, bool):
        pass


class RoomNotFound(Exception):
    pass
