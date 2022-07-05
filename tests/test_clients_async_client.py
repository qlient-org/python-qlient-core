import pytest

from qlient.core import AsyncClient, GraphQLResponse, OutOfAsyncContext


@pytest.mark.asyncio
async def test_async_client(async_strawberry_backend):
    async with AsyncClient(async_strawberry_backend) as client:
        assert client.schema is not None


def test_async_client_out_of_context(async_strawberry_backend):
    client = AsyncClient(async_strawberry_backend)

    with pytest.raises(OutOfAsyncContext):
        assert client.schema


@pytest.mark.asyncio
async def test_async_client_query(async_strawberry_backend):
    async with AsyncClient(async_strawberry_backend) as client:
        result = await client.query.getBooks(_fields=["title", "author"])
        assert isinstance(result, GraphQLResponse)
        assert isinstance(result.data["getBooks"], list)


@pytest.mark.asyncio
async def test_async_client_mutation(async_strawberry_backend):
    async with AsyncClient(async_strawberry_backend) as client:
        result = await client.mutation.addBook(
            _fields=["title", "author"], title="1984", author="George Orwell"
        )
        assert isinstance(result, GraphQLResponse)
        assert isinstance(result.data["addBook"], dict)
        assert result.data["addBook"] == {"title": "1984", "author": "George Orwell"}


@pytest.mark.asyncio
async def test_async_client_subscription(async_strawberry_backend):
    count = 0
    async with AsyncClient(async_strawberry_backend) as client:
        result = await client.subscription.count(target=5)
        assert isinstance(result, GraphQLResponse)
        async for num in result:
            assert count == num.data["count"]
            count += 1
