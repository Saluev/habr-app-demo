import json
from typing import Iterable


class ActionsManager(object):

    def __init__(self, redis):
        self.redis = redis

    def push_action(self, session_id, action):
        key = self._get_session_actions_key(session_id)
        self.redis.rpush(key, json.dumps(action))

    async def pop_action(self, session_id: str):
        key = self._get_session_actions_key(session_id)
        _, action_json = await self.redis.blpop(key)
        return json.loads(action_json)

    async def pop_first_action(self, session_ids: Iterable[str]):
        keys = map(self._get_session_actions_key, session_ids)
        key, action_json = await self.redis.blpop(*keys)
        session_id = self._parse_session_actions_key(key.decode("ascii"))
        return session_id, json.loads(action_json)

    @staticmethod
    def _get_session_actions_key(session_id: str) -> str:
        return f"{session_id}:actions"

    @staticmethod
    def _parse_session_actions_key(key: str) -> str:
        return key.split(":", 1)[0]
