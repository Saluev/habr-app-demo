import abc
import asyncio
from typing import Any, Iterable


class Connector(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    async def push_event(self, session_id: str, event: Any):
        pass

    async def broadcast_event(self, session_ids: Iterable[str], event: Any):
        # This method can be overriden in order to use Redis pipelining.
        await asyncio.wait(self.push_event(session_id, event) for session_id in session_ids)

    @abc.abstractmethod
    async def wait_action_from(self, session_id: str) -> Any:
        pass

    @abc.abstractmethod
    async def wait_action_from_any_of(self, session_ids: Iterable[str]) -> Any:
        pass
