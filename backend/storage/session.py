import abc
from typing import Any, Iterable, Tuple


class Session(object):
    def __init__(self, id: str = None, current_room_id: str = None):
        self.id = id
        self.current_room_id = current_room_id


class SessionDAO(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create(self, session: Session) -> Session:
        pass

    @abc.abstractmethod
    def update(self, session: Session) -> Session:
        pass

    @abc.abstractmethod
    def get_all(self) -> Iterable[Session]:
        pass

    @abc.abstractmethod
    def get_by_id(self, session_id: str) -> Session:
        pass

    @abc.abstractmethod
    def set_room_id(self, session_id: str, room_id: str):
        pass


class SessionManager(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_session(self) -> Session:
        pass

    @abc.abstractmethod
    def is_session_expired(self, session_id: str) -> bool:
        pass

    @abc.abstractmethod
    def refresh_session_expiration(self, session_id: str):
        pass

    @abc.abstractmethod
    def enqueue_participant(self, session_id: str):
        pass

    @abc.abstractmethod
    def get_next_enqueued_participant(self) -> str:
        pass

    @abc.abstractmethod
    def push_event(self, session_id: str, event: Any):
        pass

    @abc.abstractmethod
    def yield_events(self, session_id: str) -> Iterable[Any]:
        pass


class SessionNotFound(Exception):
    pass
