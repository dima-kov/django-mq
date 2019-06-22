from mq.storage.connectors.abstract import AbstractStorageConnector


class ConsumerRegistry(object):
    """
       'queue_name:consumers'

    :cid == consumer_id
    :cname == consumer_name
    @todo: add transactions support
    """

    def __init__(self, queue_name, connector: AbstractStorageConnector):
        self.connector = connector
        self.consumers_num = '{}:consumers:num'.format(queue_name)
        self.consumers_register = '{}:consumers:register'.format(queue_name)
        self.consumers_active = '{}:consumers:active'.format(queue_name)
        self.consumers_ready = '{}:consumers:ready'.format(queue_name)

        # Helper keys to store temp values during BITOP
        self.consumers_active_and_registered = '{}:consumers:active_registered'.format(queue_name)
        self.consumers_not_active = '{}:consumers:not_active'.format(queue_name)
        self.consumers_inactive = '{}:consumers:inactive'.format(queue_name)

        self.consumers_ready_and_registered = '{}:consumers:ready_registered'.format(queue_name)
        self.consumers_not_ready = '{}:consumers:not_ready'.format(queue_name)
        self.consumers_unready = '{}:consumers:unready'.format(queue_name)

    def register(self):
        ids = self.batch_register(1)
        return ids.pop()

    def batch_register(self, n):
        unregistered = self._get_unregistered_cids()
        unregistered_len = len(unregistered)

        cids = []
        for i in range(n):
            cid = unregistered.pop(0) if i < unregistered_len else self._new()
            cids.append(cid)
            self._update_register(cid, 1)
        return cids

    def unregister(self, cid: int):
        self._update_register(cid, 0)
        if cid == self._num():
            self.connector.decr(self.consumers_num)

    def count_active(self):
        self.connector.bitop_and(self.consumers_active_and_registered, self.consumers_register,
                                 self.consumers_active)
        return self.connector.bit_count(self.consumers_active_and_registered)

    def count_inactive(self):
        self.connector.bitop_not(self.consumers_not_active, self.consumers_active)
        self.connector.bitop_and(self.consumers_inactive, self.consumers_register, self.consumers_not_active)
        return self.connector.bit_count(self.consumers_inactive)

    def count_ready(self):
        self.connector.bitop_and(self.consumers_ready_and_registered, self.consumers_register,
                                 self.consumers_ready)
        return self.connector.bit_count(self.consumers_ready_and_registered)

    def count_unready(self):
        self.connector.bitop_not(self.consumers_not_ready, self.consumers_ready)
        self.connector.bitop_and(self.consumers_unready, self.consumers_register, self.consumers_not_ready)
        return self.connector.bit_count(self.consumers_unready)

    def update_active(self, cid):
        return self._update_active(cid, 1)

    def update_inactive(self, cid):
        return self._update_active(cid, 0)

    def update_ready(self, cid, ready: bool):
        return self._update(self.consumers_ready, cid, int(ready))

    def as_bits(self):
        return {
            'registered': self._cut_num(self.connector.get(self.consumers_register)),
            'ready': self._cut_num(self.connector.get(self.consumers_ready)),
            'active': self._cut_num(self.connector.get(self.consumers_active)),
        }

    def cleanup(self):
        self.connector.delete_key(self.consumers_num)
        self.connector.delete_key(self.consumers_active)
        self.connector.delete_key(self.consumers_inactive)
        self.connector.delete_key(self.consumers_register)
        self.connector.delete_key(self.consumers_ready)

    def _update_register(self, cid: int, status: int):
        return self._update(self.consumers_register, cid, status)

    def _update_active(self, cid: int, status: int):
        return self._update(self.consumers_active, cid, status)

    def _update(self, key: str, cid: int, status: int):
        return self.connector.bit_set(key, cid, status)

    def _get_unregistered_cids(self):
        bits = self._cut_num(self.connector.get(self.consumers_register))
        return [i for i, status in enumerate(bits) if status == 0]

    def _cut_num(self, sequence: [int]) -> [int]:
        return to_bits(sequence)[:self._num()]

    def _new(self):
        return self.connector.incr(self.consumers_num) - 1

    def _num(self):
        return self.connector.get_int(self.consumers_num)


def to_bits(r) -> [int]:
    bits = []
    if r is None:
        return bits

    for byte in r:
        bits += [(byte >> i) & 1 for i in range(7, -1, -1)]

    return bits
