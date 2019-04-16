import json
from typing import Any, Iterable, Tuple

import bson
from pymongo.collection import Collection
from pymongo.database import Database
import redis

from backend.storage.client_converter import ClientConverter
from backend.storage.session import Session, SessionDAO, SessionManager, SessionNotFound
from backend.storage.mongo_dao import MongoDAO
from backend.utility.redis import Queue


SESSION_EXPIRATION_KEY_TEMPLATE = "{session_id}:expire"
SESSION_EVENTS_QUEUE_KEY_TEMPLATE = "{session_id}:events"
PARTICIPANTS_QUEUE_KEY = "participants"


class MongoSessionDAO(MongoDAO, SessionDAO):

    def __init__(self, mongo_database: Database):
        self.mongo_database = mongo_database

    @property
    def collection(self) -> Collection:
        return self.mongo_database["sessions"]

    object_class = Session

    not_found_exception = SessionNotFound

    def to_bson_middleware(self, document: dict):
        document = super().to_bson_middleware(document)
        if "current_room_id" in document:
            document["current_room_id"] = bson.ObjectId(document["current_room_id"])
        return document

    def from_bson_middleware(self, document: dict):
        document = super().from_bson_middleware(document)
        if "current_room_id" in document:
            document["current_room_id"] = str(document["current_room_id"])
        return document

    def set_room_id(self, session_id: str, room_id: str):
        obj_id = bson.ObjectId(session_id)
        self.collection.update_one({"_id": obj_id}, {"$set": {"current_room_id": bson.ObjectId(room_id)}})


class RedisSessionManager(SessionManager):

    def __init__(self, session_dao: SessionDAO, redis: redis.Redis, settings):
        self.dao = session_dao
        self.redis = redis
        self.session_expiration_msec = settings.SESSION_EXPIRATION_MSEC
        self.participants_queue = Queue(self.redis, PARTICIPANTS_QUEUE_KEY)

    def create_session(self) -> Session:
        return self.dao.create(Session())

    def is_session_expired(self, session_id: str) -> bool:
        return self.redis.exists(self._get_session_expiration_key(session_id))

    def refresh_session_expiration(self, session_id: str):
        self.redis.pexpire(self._get_session_expiration_key(session_id), self.session_expiration_msec)

    def enqueue_participant(self, session_id: str):
        return self.participants_queue.push(session_id)

    def get_next_enqueued_participant(self, timeout=0) -> str:
        return self.participants_queue.pop(timeout=timeout)

    def push_event(self, session_id: str, event: Any):
        key = self._get_session_events_key(session_id)
        return self.redis.rpush(key, json.dumps(event))

    def yield_events(self, session_id: str) -> Iterable[Any]:
        key = self._get_session_events_key(session_id)
        while True:
            _, data_json = self.redis.blpop(key)
            yield json.loads(data_json)

    @staticmethod
    def _get_session_expiration_key(session_id: str) -> str:
        return SESSION_EXPIRATION_KEY_TEMPLATE.format(session_id=session_id)

    @staticmethod
    def _get_session_events_key(session_id: str) -> str:
        return SESSION_EVENTS_QUEUE_KEY_TEMPLATE.format(session_id=session_id)


class SessionClientConverter(ClientConverter):
    pass
