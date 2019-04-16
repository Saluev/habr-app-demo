import redis


class Queue(object):

    def __init__(self, redis: redis.Redis, key: str):
        self.redis = redis
        self.key = key

    def push(self, value: str):
        self.redis.rpush(self.key, value)

    def pop(self, timeout=0) -> str:
        result = self.redis.blpop(self.key, timeout=timeout)
        if result is None:
            raise QueueTimeout()
        return result


class QueueTimeout(Exception):
    pass
