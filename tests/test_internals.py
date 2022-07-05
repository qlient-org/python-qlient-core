import pytest

from qlient.core._internal import await_if_coro


@pytest.mark.asyncio
async def test_await_if_coro_with_coro():
    async def _():
        return None

    assert await await_if_coro(_()) is None


@pytest.mark.asyncio
async def test_await_if_coro_with_result():
    def _():
        return None

    assert await await_if_coro(_()) is None
