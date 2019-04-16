import asyncio
import collections
from typing import Any, Iterable

from backend.games.connector import Connector


class StubConnector(Connector):

    def __init__(self):
        self.events = collections.defaultdict(collections.deque)
        self.actions = collections.defaultdict(collections.deque)

    async def push_event(self, session_id: str, event: Any):
        self.events[session_id].append(event)

    async def wait_action_from(self, session_id: str) -> Any:
        while True:
            if self.actions[session_id]:
                return self.actions[session_id].popleft()
            else:
                await asyncio.sleep(0.05)

    async def wait_action_from_any_of(self, session_ids: Iterable[str]) -> Any:
        while True:
            for session_id in session_ids:
                if self.actions[session_id]:
                    return self.actions[session_id].popleft()
            else:
                await asyncio.sleep(0.05)
