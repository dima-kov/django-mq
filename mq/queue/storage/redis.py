import redis

from mq import settings
from mq.queue.storage.abstract import AbstractStorageConnector


class RedisStorageConnector(AbstractStorageConnector):
    redis = redis.Redis(host=settings.MQ_REDIS_HOST, port=settings.MQ_REDIS_PORT)

    def decode(self, data):
        """Decoding from byte into string after redis storage"""
        if isinstance(data, bytes):
            return data.decode('ascii')
        if isinstance(data, dict):
            return dict(map(self.decode, data.items()))
        if isinstance(data, tuple):
            return map(self.decode, data)

        return data

    def get(self, key):
        return self.redis.get(key)

    def get_int(self, key) -> int:
        return self.as_int(self.redis.get(key))

    def set(self, key, value):
        return self.redis.set(key, value)

    def incr(self, key):
        return self.redis.incr(key)

    def decr(self, key):
        return self.redis.decr(key)

    def push_list(self, key, *values):
        return self.redis.lpush(key, *values)

    def push_list_start(self, key, *values):
        return self.redis.rpush(key, *values)

    def rpoplpush(self, src, dst):
        return self.redis.rpoplpush(src, dst)

    def list_range(self, key, number=-1):
        return self.redis.lrange(key, 0, number)

    def delete_key(self, key):
        return self.redis.delete(key)

    def delete_list_value(self, key, value):
        return self.redis.lrem(key, 0, value)

    def list_len(self, key):
        return self.redis.llen(key)

    def bit_count(self, key, start=None, end=None):
        return self.redis.bitcount(key, start, end)

    def bit_set(self, name, offset, value):
        return self.redis.setbit(name, offset, value)

    def bit_get(self, name, offset):
        return self.redis.getbit(name, offset)

    def bitop_and(self, dest, key, *keys):
        return self.redis.bitop('and', dest, key, *keys)

    def bitop_not(self, dest, key):
        return self.redis.bitop('not', dest, key)

    def ltrim(self, name, number):
        return self.redis.ltrim(name, number, -1)

    @staticmethod
    def as_int(v):
        return 0 if v is None else int(v)

    def hgetall(self, key: str):
        return self.redis.hgetall(key)

    def hmset(self, key, value: dict):
        return self.redis.hmset(key, value)

    def expire(self, key, ttl=0):
        return self.redis.expire(key, ttl)
