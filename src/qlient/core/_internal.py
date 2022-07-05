import inspect


async def await_if_coro(x):
    """Await if it is a coroutine otherwise return x"""
    if inspect.iscoroutine(x):
        return await x
    return x
