import os

import aioredis
from pymongo import MongoClient
from pymongo.database import Database
import redis
import rq

import backend.dev_settings
from backend.actions_manager import ActionsManager
from backend.game_server import GameServer
from backend.game_server_client import GameServerClient
from backend.storage.card import CardDAO
from backend.storage.card_impl import MongoCardDAO
from backend.storage.room import RoomDAO, RoomManager
from backend.storage.room_impl import MongoRoomDAO, RedisLockingRoomManager, RoomClientConverter
from backend.storage.session import SessionDAO, SessionManager
from backend.storage.session_impl import MongoSessionDAO, RedisSessionManager, SessionClientConverter


class Wiring(object):

    def __init__(self, env=None):
        if env is None:
            env = os.environ.get("APP_ENV", "dev")
        self.settings = {
            "dev": backend.dev_settings,
        }[env]

        self.mongo_client: MongoClient = MongoClient(
            host=self.settings.MONGO_HOST,
            port=self.settings.MONGO_PORT)
        self.mongo_database: Database = self.mongo_client[self.settings.MONGO_DATABASE]
        self.card_dao: CardDAO = MongoCardDAO(self.mongo_database)

        self.redis: redis.Redis = redis.StrictRedis(
            host=self.settings.REDIS_HOST,
            port=self.settings.REDIS_PORT,
            db=self.settings.REDIS_DB)
        self.task_queue: rq.Queue = rq.Queue(
            name=self.settings.TASK_QUEUE_NAME,
            connection=self.redis)

        self.game_server_client: GameServerClient = GameServerClient(
            redis=self.redis,
            settings=self.settings)

        self.room_dao: RoomDAO = MongoRoomDAO(self.mongo_database)
        self.room_manager: RoomManager = RedisLockingRoomManager(
            room_dao=self.room_dao,
            redis=self.redis)
        self.room_client_converter: RoomClientConverter = RoomClientConverter()

        self.session_dao: SessionDAO = MongoSessionDAO(self.mongo_database)
        self.session_manager: SessionManager = RedisSessionManager(
            session_dao=self.session_dao,
            redis=self.redis,
            settings=self.settings)
        self.session_client_converter: SessionClientConverter = SessionClientConverter()

        self.actions_manager: ActionsManager = ActionsManager(self.redis)

        self.async_redis: aioredis.Redis = None
        self.game_server: GameServer = None

    async def init_async(self, loop):
        self.async_redis = await aioredis.create_redis_pool(
            f"redis://{self.settings.REDIS_HOST}:{self.settings.REDIS_PORT}",
            db=self.settings.REDIS_DB,
            minsize=100, maxsize=10000,  # TODO decide what's wrong with it (probably just rewrite fucking Pool)
            loop=loop)
        self.actions_manager = ActionsManager(self.async_redis)
        self.game_server = GameServer(
            async_redis=self.async_redis,
            settings=self.settings,
            session_manager=self.session_manager,
            actions_manager=self.actions_manager)
