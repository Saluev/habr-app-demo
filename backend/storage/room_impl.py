import logging

import bson
from pymongo.collection import Collection
from pymongo.database import Database
import redis
import redis_lock

from backend.storage.client_converter import ClientConverter
from backend.storage.room import Room, RoomDAO, RoomManager, RoomNotFound
from backend.storage.mongo_dao import MongoDAO


ROOMS_QUEUE_KEY = "rooms"
ROOMS_QUEUE_LOCK = "rooms_lock"


class MongoRoomDAO(MongoDAO, RoomDAO):

    def __init__(self, mongo_database: Database):
        self.mongo_database = mongo_database

    @property
    def collection(self) -> Collection:
        return self.mongo_database["rooms"]

    object_class = Room

    not_found_exception = RoomNotFound

    def to_bson_middleware(self, document: dict):
        document = super().to_bson_middleware(document)
        if "participants" in document:
            document["participants"] = list(map(bson.ObjectId, document["participants"]))
        return document

    def from_bson_middleware(self, document: dict):
        document = super().from_bson_middleware(document)
        if "participants" in document:
            document["participants"] = list(map(str, document["participants"]))
        return document

    def add_participant(self, room_id: str, participant_id: str):
        obj_id = bson.ObjectId(room_id)
        self.collection.update_one({"_id": obj_id}, {"$push": {"participants": bson.ObjectId(participant_id)}})


class RedisLockingRoomManager(RoomManager):

    def __init__(self, room_dao: RoomDAO, redis: redis.Redis):
        self.dao = room_dao
        self.redis = redis

    def choose_room_for_participant(self, participant_id: str) -> (str, bool):
        with redis_lock.Lock(self.redis, ROOMS_QUEUE_LOCK, expire=10):
            room_id = self.redis.lpop(ROOMS_QUEUE_KEY)
            if room_id is None:
                room = Room(kind="minesweeper")
                room = self.dao.create(room)
                room_id = room.id
            else:
                room_id = room_id.decode("ascii")
            logging.debug("Adding participant %s to room %s", participant_id, room_id)
            self.dao.add_participant(room_id, participant_id)
            room = self.dao.get_by_id(room_id)
            if not room.is_complete():
                self.redis.lpush(ROOMS_QUEUE_KEY, room.id)
            return room.id, room.is_complete()


class RoomClientConverter(ClientConverter):
    pass
