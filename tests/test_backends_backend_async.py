import pytest

from qlient.core import GraphQLResponse


@pytest.mark.asyncio
async def test_backend_execute_query(async_strawberry_backend, monkeypatch):
    async def mock(request):
        return GraphQLResponse(request, {"data": {"foo": "bar"}})

    monkeypatch.setattr(async_strawberry_backend, "execute_query", mock)

    response = await async_strawberry_backend.execute_query(None)
    assert response.data == {"foo": "bar"}


@pytest.mark.asyncio
async def test_backend_execute_mutation(async_strawberry_backend, monkeypatch):
    async def mock(request):
        return GraphQLResponse(request, {"data": {"foo": "bar"}})

    monkeypatch.setattr(async_strawberry_backend, "execute_mutation", mock)

    response = await async_strawberry_backend.execute_mutation(None)
    assert response.data == {"foo": "bar"}


@pytest.mark.asyncio
async def test_backend_execute_subscription_iterator(
    async_strawberry_backend, monkeypatch
):
    messages = [{"foo": "bar"}] * 10

    async def mock(request):
        class AIterator:
            def __init__(self, data):
                self.data = iter(data)

            def __aiter__(self):
                return self

            async def __anext__(self):
                try:
                    return next(self.data)
                except StopIteration:
                    raise StopAsyncIteration

        return GraphQLResponse(request, AIterator(messages))

    monkeypatch.setattr(async_strawberry_backend, "execute_subscription", mock)

    response = await async_strawberry_backend.execute_subscription(None)

    assert isinstance(response, GraphQLResponse)

    async for message in response:
        assert message in messages


@pytest.mark.asyncio
async def test_backend_execute_subscription_generator(
    async_strawberry_backend, monkeypatch
):
    messages = [{"foo": "bar"}] * 10

    async def mock(request):
        async def generator():
            for message in messages:
                yield message

        return GraphQLResponse(request, generator())

    monkeypatch.setattr(async_strawberry_backend, "execute_subscription", mock)

    response = await async_strawberry_backend.execute_subscription(None)

    assert isinstance(response, GraphQLResponse)

    async for message in response:
        assert message in messages
