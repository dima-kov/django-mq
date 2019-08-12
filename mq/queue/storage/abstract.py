class AbstractStorageConnector:

    def get(self, key):
        raise NotImplementedError

    def get_int(self, key) -> int:
        raise NotImplementedError

    def incr(self, key):
        raise NotImplementedError

    def decr(self, key):
        raise NotImplementedError

    def set(self, key, value):
        raise NotImplementedError

    def push_list(self, key, *values):
        raise NotImplementedError

    def push_list_start(self, key, *values):
        raise NotImplementedError

    def rpoplpush(self, src, dst):
        raise NotImplementedError

    def list_range(self, key, number=-1):
        raise NotImplementedError

    def delete_key(self, key):
        raise NotImplementedError

    def delete_list_value(self, key, value):
        raise NotImplementedError

    def expire(self, key, ttl):
        raise NotImplementedError

    def list_len(self, key):
        raise NotImplementedError

    def bit_count(self, name, start=None, end=None):
        raise NotImplementedError

    def bit_set(self, name, offset, value):
        raise NotImplementedError

    def bit_get(self, name, offset):
        raise NotImplementedError

    def bitop_and(self, dest, key, *keys):
        raise NotImplementedError

    def bitop_not(self, dest, key):
        raise NotImplementedError

    def ltrim(self, dest, number):
        raise NotImplementedError
