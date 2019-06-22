import time


class NoValueInsideGenerator(IndexError):
    pass


class InfiniteGenerator(object):
    """
       InfiniteGenerator - class for returning one object from list.
       One object is always present in _current_obj with access to it by current() method.
       When you need to use next - method next()
        - list of objects - set in child class with get_all_objects_list()

        It is useful when many instances of one class should use same `current_object` while smth happens
        to change it.

        Example:
            - CaptchaSolver
            It sends request to external resource with API key. Key is being checked on external server whether
            account has enough money. When server returns ZeroBalance: one instance calls `next` method,
            key is changed to another and all other instances uses it.
    """
    allow_empty = False
    _all_objects_list = None
    _current_obj = None
    __generator__ = None

    def __init__(self):
        self.reload_generator()

    def generator(self):
        if len(self._all_objects_list) == 0:
            if not self.allow_empty:
                raise NoValueInsideGenerator('You should populate generator with data. Maybe DB table is empty')
            self._all_objects_list = [None]
        return iter(self._all_objects_list)

    def get_all_objects_list(self):
        """Method to specify list with all available objects in generator
            Will be called every time, when generator ends.
        """
        raise NotImplemented()

    def current(self):
        """Return current object in generator"""
        return self._current_obj

    def next(self):
        return self._next()

    def _next(self):
        """Move generator to next object"""
        try:
            self._current_obj = next(self.__generator__)
        except StopIteration:
            self.reload_generator()
            return self._next()

    def reload_generator(self):
        self._all_objects_list = self.get_all_objects_list()
        self.__generator__ = self.generator()


class ExactlyChangedInfiniteGenerator(InfiniteGenerator):
    """
        Infinite Generator with check whether previous value (provided by client) differs
        from current in generator. If value differ then value in generator has been already
        changed by another client.

        Useful with clients that runs some concurrency code.

        E.g.:

            class Client():
                g = ExactlyChangedInfiniteGenerator()

                async def do():
                    # if some happens -> move generator to next value
                    if something:
                        g.next()

            client1 = Client()
            client2 = Client()
            loop.run_until_complete(asyncio.wait(client1.do(), client2.do()))

            # Both client1 and client2 will send request to generator to switch to next value
            without check for previous value
    """

    def next(self, previous=None):
        """Move generator to next object"""
        if self._current_obj != previous:
            # Means self._current_obj was already changed by some previous next() call
            return
        super(ExactlyChangedInfiniteGenerator, self).next()


class SuspendingInfiniteGenerator(InfiniteGenerator):
    """Infinite Generator that suspends (`time.sleep()`) every `suspend_after`."""

    suspend_after = None
    sleep_len = 5
    current_change = 0

    def __init__(self):
        if self.suspend_after is None:
            raise ValueError('suspend_after attribute should not be None')
        super(SuspendingInfiniteGenerator, self).__init__()

    def next(self, previous=None):
        """Move generator to next object"""
        self.current_change += 1
        if self.current_change > self.suspend_after:
            time.sleep(self.suspend_after * self.sleep_len)

        super(SuspendingInfiniteGenerator, self).next()

    def nullify(self):
        self.current_change = 0


class EmptyInfiniteGenerator(InfiniteGenerator):
    """Infinite generator with allowed empty list"""

    def next(self):
        try:
            return super().next()
        except NoValueInsideGenerator:
            return None


def test():
    class SomeListGen(InfiniteGenerator):

        def get_all_objects_list(self):
            return [1, 2]

    gen = SomeListGen()
    gen.next()
    assert gen.current() == 1
    gen.next()
    assert gen.current() == 2
    gen.next()
    assert gen.current() == 1
    gen.next()
    assert gen.current() == 2


def test_only_exect():
    class SomeOnceChangedGen(ExactlyChangedInfiniteGenerator):
        def get_all_objects_list(self):
            return [1, 2]

    gen2 = SomeOnceChangedGen()
    gen2.next()
    gen3 = gen2
    assert gen2.current() == 1
    assert gen3.current() == 1
    gen2.next(1)
    assert gen2.current() == 2
    assert gen3.current() == 2
    gen3.next(1)
    assert gen2.current() == 2
    assert gen3.current() == 2
    gen2.next(2)
    assert gen2.current() == 1
    assert gen3.current() == 1


def test_only_exect_and_suspending():
    class SomeOnceChangedSuspendingGen(ExactlyChangedInfiniteGenerator, SuspendingInfiniteGenerator):
        suspend_after = 2

        def get_all_objects_list(self):
            return [1, 2]

    gen2 = SomeOnceChangedSuspendingGen()
    gen2.next()
    gen3 = gen2
    assert gen2.current() == 1
    assert gen3.current() == 1
    gen2.next(1)
    assert gen2.current() == 2
    assert gen3.current() == 2
    gen3.next(1)
    assert gen2.current() == 2
    assert gen3.current() == 2
    gen2.next(2)
    assert gen2.current() == 1
    assert gen3.current() == 1
