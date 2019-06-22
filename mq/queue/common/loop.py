import asyncio


class AsyncLoop(object):

    def __init__(self, loop=None):
        self.loop = loop or self.get_loop()

    def run_multiple(self, tasks):
        return self.run_in_loop(asyncio.wait(tasks))

    def run_in_loop(self, task):
        return self.loop.run_until_complete(task)

    @staticmethod
    def get_loop():
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop
