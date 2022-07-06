import pytest

from qlient.core import AsyncClient, GraphQLResponse


@pytest.mark.asyncio
async def test_async_client_non_async_backend(strawberry_backend):
    async with AsyncClient(strawberry_backend) as client:
        assert client.schema is not None


@pytest.mark.asyncio
async def test_async_client_query(strawberry_backend):
    async with AsyncClient(strawberry_backend) as client:
        result = await client.query.getBooks(_fields=["title", "author"])
        assert isinstance(result, GraphQLResponse)
        assert isinstance(result.data["getBooks"], list)


@pytest.mark.asyncio
async def test_async_client_mutation(strawberry_backend):
    async with AsyncClient(strawberry_backend) as client:
        result = await client.mutation.addBook(
            _fields=["title", "author"], title="1984", author="George Orwell"
        )
        assert isinstance(result, GraphQLResponse)
        assert isinstance(result.data["addBook"], dict)
        assert result.data["addBook"] == {"title": "1984", "author": "George Orwell"}
