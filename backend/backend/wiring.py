import os

from elasticsearch_ltr import LTRClient
from celery import Celery
from elasticsearch import Elasticsearch
from pymongo import MongoClient
from pymongo.database import Database
import redis

import backend.dev_settings
from backend.search.indexer import Indexer
from backend.search.searcher import Searcher
from backend.search.searcher_impl import ElasticsearchSearcher
from backend.storage.card import CardDAO
from backend.storage.card_impl import MongoCardDAO
from backend.tasks.manager import TaskManager


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
        self.celery_app = Celery("habr-app-demo-worker",
            broker=f"redis://{self.settings.REDIS_HOST}:{self.settings.REDIS_PORT}")
        self.task_manager = TaskManager(self.celery_app)

        self.elasticsearch_client = Elasticsearch(hosts=self.settings.ELASTICSEARCH_HOSTS)
        LTRClient.infect_client(self.elasticsearch_client)
        self.indexer = Indexer(self.elasticsearch_client, self.card_dao, self.settings.CARDS_INDEX_ALIAS)
        self.searcher: Searcher = ElasticsearchSearcher(self.elasticsearch_client, self.settings.CARDS_INDEX_ALIAS)
