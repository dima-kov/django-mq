import asyncio

import uvloop


class AsyncLoop(object):

    def run_multiple(self, tasks):
        return self.run_in_loop(asyncio.wait(tasks))

    def run_in_loop(self, task):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(task)
