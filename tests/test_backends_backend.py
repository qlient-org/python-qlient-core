from qlient.core import GraphQLResponse, GraphQLResponseIterator


def test_backend_execute_query(strawberry_backend, monkeypatch):
    def mock(request):
        return GraphQLResponse(request, {"data": {"foo": "bar"}})

    monkeypatch.setattr(strawberry_backend, "execute_query", mock)

    response = strawberry_backend.execute_query(None)
    assert response.data == {"foo": "bar"}


def test_backend_execute_mutation(strawberry_backend, monkeypatch):
    def mock(request):
        return GraphQLResponse(request, {"data": {"foo": "bar"}})

    monkeypatch.setattr(strawberry_backend, "execute_mutation", mock)

    response = strawberry_backend.execute_mutation(None)
    assert response.data == {"foo": "bar"}


def test_backend_execute_subscription_iterator(strawberry_backend, monkeypatch):
    messages = [{"foo": "bar"}] * 10

    def mock(request):
        return GraphQLResponseIterator(request, messages)

    monkeypatch.setattr(strawberry_backend, "execute_subscription", mock)

    response = strawberry_backend.execute_subscription(None)

    assert isinstance(response, GraphQLResponseIterator)

    for message in response:
        assert message in messages


def test_backend_execute_subscription_generator(strawberry_backend, monkeypatch):
    messages = [{"foo": "bar"}] * 10

    def mock(request):
        def generator():
            yield from messages

        return GraphQLResponseIterator(request, generator())

    monkeypatch.setattr(strawberry_backend, "execute_subscription", mock)

    response = strawberry_backend.execute_subscription(None)

    assert isinstance(response, GraphQLResponseIterator)

    for message in response:
        assert message in messages
