from qlient.core import Client, GraphQLResponse


def test_client(strawberry_backend):
    client = Client(strawberry_backend)

    result = client.query.getBooks(_fields=["title", "author"])
    assert isinstance(result, GraphQLResponse)
