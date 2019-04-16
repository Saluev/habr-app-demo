import json

import redis

from backend.storage.room import Room
from backend.utility.redis import Queue


class GameServerClient(object):
    def __init__(self, redis: redis.Redis, settings):
        self.queue = Queue(redis, settings.GAME_QUEUE_NAME)

    def schedule_game(self, room: Room):
        if not room.is_complete():
            raise ValueError("can't schedule game in incomplete room")
        self.queue.push(json.dumps(self.to_json(room)))

    @staticmethod
    def to_json(room: Room):
        return {k: v for k, v in room.__dict__.items() if v is not None}
