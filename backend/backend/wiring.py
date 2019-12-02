import os

from pymongo import MongoClient
from pymongo.database import Database
import redis
import rq

import backend.dev_settings
from backend.storage.card import CardDAO
from backend.storage.card_impl import MongoCardDAO


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
