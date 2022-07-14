from qlient.core import Client, Settings, GraphQLResponse
from qlient.core.proxies import (
    QueryServiceProxy,
    MutationServiceProxy,
    SubscriptionServiceProxy,
)


# skipcq: PY-D0003
def test_client(strawberry_backend):
    client = Client(strawberry_backend)

    assert isinstance(client.settings, Settings)
    assert client.backend == strawberry_backend
    assert client.schema is not None

    assert client.plugins == []

    assert isinstance(client.query, QueryServiceProxy)
    assert isinstance(client.mutation, MutationServiceProxy)
    assert isinstance(client.subscription, SubscriptionServiceProxy)

    assert str(client) == "Client(backend=StrawberryBackend)"


# skipcq: PY-D0003
def test_client_with_plugins(strawberry_backend, my_plugin):
    client = Client(strawberry_backend, plugins=[my_plugin])
    assert my_plugin in client.plugins


def test_client_query(strawberry_backend):
    client = Client(strawberry_backend)
    result = client.query.getBooks(["title", "author"])
    assert isinstance(result, GraphQLResponse)
    assert isinstance(result.data["getBooks"], list)


def test_client_mutation(strawberry_backend):
    client = Client(strawberry_backend)
    result = client.mutation.addBook(
        ["title", "author"], title="1984", author="George Orwell"
    )
    assert isinstance(result, GraphQLResponse)
    assert isinstance(result.data["addBook"], dict)
    assert result.data["addBook"] == {"title": "1984", "author": "George Orwell"}
