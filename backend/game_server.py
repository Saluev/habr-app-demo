import asyncio
import json
import logging
from typing import Any, Iterable

import aioredis

from backend.actions_manager import ActionsManager
from backend.games.checkers import Checkers
from backend.games.connector import Connector
from backend.games.minesweeper import Minesweeper
from backend.storage.room import Room
from backend.storage.session import SessionManager


class GameServer(object):

    def __init__(self, async_redis: aioredis.Redis, settings, session_manager: SessionManager, actions_manager: ActionsManager):
        self.async_redis = async_redis
        self.game_queue_name = settings.GAME_QUEUE_NAME
        self.action_timeout = settings.MAX_GAME_LENGTH_SEC
        self.session_manager = session_manager
        self.actions_manager = actions_manager

    async def serve_room(self, room: Room):
        logging.info("Started serving room %s of kind %r", room.id, room.kind)
        try:
            game = self._get_game_instance_by_kind(room.kind)
            connector = ConnectorWithTimeout(RedisConnector(self, room), self.action_timeout)
            await game.play(room.participants, connector)
        except TimeoutExceeded:
            for participant in room.participants:
                self.session_manager.push_event(participant, {"kind": "error", "error": "timeout"})
            # TODO cleanup
        except Exception:
            logging.exception("Exception while serving room %s of kind %r", room.id, room.kind)

    async def serve_games(self):
        logging.info("Game server started")
        while True:
            _, room_json = await self.async_redis.blpop(self.game_queue_name)
            room = Room(**json.loads(room_json))
            asyncio.create_task(self.serve_room(room))

    @staticmethod
    def _get_game_instance_by_kind(kind: str):
        return {
            "checkers": Checkers,
            "minesweeper": Minesweeper,
        }[kind]()

    def _push_event_to_all_in_room(self, room, event, data):
        for participant in room.participants:
            self.session_manager.push_event(participant, event, data)


class RedisConnector(Connector):

    def __init__(self, game_server: GameServer, room: Room):
        self.game_server = game_server
        self.room = room

    async def push_event(self, session_id: str, event: Any):
        return self.game_server.session_manager.push_event(session_id, event)

    async def wait_action_from(self, session_id: str):
        return await self.game_server.actions_manager.pop_action(session_id)

    async def wait_action_from_any_of(self, session_ids: Iterable[str]):
        return await self.game_server.actions_manager.pop_first_action(session_ids)


class TimeoutExceeded(Exception):
    pass


class ConnectorWithTimeout(Connector):

    def __init__(self, connector, timeout):
        self.connector = connector
        self.timeout = timeout

    async def push_event(self, session_id: str, event: Any):
        return await self.connector.push_event(session_id, event)

    async def wait_action_from(self, session_id: str):
        return await self._do_with_timeout(self.connector.wait_action_from(session_id))

    async def wait_action_from_any_of(self, session_ids: Iterable[str]):
        return await self._do_with_timeout(self.connector.wait_action_from_any_of(session_ids))

    async def _do_with_timeout(self, task):
        done, pending = await asyncio.wait([
            task,
            self.raise_timeout_exceeded(),
        ], return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        return await done.pop()

    async def raise_timeout_exceeded(self):
        await asyncio.sleep(self.timeout)
        logging.debug("Timeout while waiting for actions")
        raise TimeoutExceeded

