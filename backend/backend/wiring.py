import os

from pymongo import MongoClient
from pymongo.database import Database
import redis
import rq

import backend.dev_settings
import backend.k8s_secrets_settings
import backend.k8s_settings
from backend.storage.card import CardDAO
from backend.storage.card_impl import MongoCardDAO


class Wiring(object):

    def __init__(self, env=None):
        if env is None:
            env = os.environ.get("APP_ENV", "dev")
        self.settings = {
            "dev": backend.dev_settings,
            "k8s": backend.k8s_settings,
            "k8s_secrets": backend.k8s_secrets_settings,
        }[env]

        mongo_auth = ""
        if self.settings.MONGO_USER:
            with open(self.settings.MONGO_PASSWORD_PATH, "rt") as f:
                mongo_password = f.read()
            mongo_auth = f"{self.settings.MONGO_USER}:{mongo_password}@"
        mongo_uri = f"mongodb://{mongo_auth}{self.settings.MONGO_HOST}:{self.settings.MONGO_PORT}/"
        self.mongo_client: MongoClient = MongoClient(mongo_uri, serverSelectionTimeoutMS=1000)
        self.mongo_database: Database = self.mongo_client[self.settings.MONGO_DATABASE]
        self.card_dao: CardDAO = MongoCardDAO(self.mongo_database)

        self.redis: redis.Redis = redis.StrictRedis(
            host=self.settings.REDIS_HOST,
            port=self.settings.REDIS_PORT,
            db=self.settings.REDIS_DB)
        self.task_queue: rq.Queue = rq.Queue(
            name=self.settings.TASK_QUEUE_NAME,
            connection=self.redis)
