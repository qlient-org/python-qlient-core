import pytest

from qlient.core import GraphQLResponse, Backend


def test_backend_no_impl():
    with pytest.raises(TypeError):
        Backend()


def test_backend_execute_query_raise_not_implemented():
    with pytest.raises(NotImplementedError):
        Backend.execute_query(..., ...)


def test_backend_execute_mutation_raise_not_implemented():
    with pytest.raises(NotImplementedError):
        Backend.execute_mutation(..., ...)


def test_backend_execute_subscription_raise_not_implemented():
    with pytest.raises(NotImplementedError):
        Backend.execute_subscription(..., ...)


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
        return GraphQLResponse(request, messages)

    monkeypatch.setattr(strawberry_backend, "execute_subscription", mock)

    response = strawberry_backend.execute_subscription(None)

    assert isinstance(response, GraphQLResponse)

    for message in response:
        assert message in messages


def test_backend_execute_subscription_generator(strawberry_backend, monkeypatch):
    messages = [{"foo": "bar"}] * 10

    def mock(request):
        def generator():
            yield from messages

        return GraphQLResponse(request, generator())

    monkeypatch.setattr(strawberry_backend, "execute_subscription", mock)

    response = strawberry_backend.execute_subscription(None)

    assert isinstance(response, GraphQLResponse)

    for message in response:
        assert message in messages
