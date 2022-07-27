import pytest

from qlient.core import Settings, GraphQLRequest
from qlient.core.proxies import QueryServiceProxy


def test_query_operation_proxy(swapi_schema, fake_backend):
    proxy = QueryServiceProxy(fake_backend, Settings(), swapi_schema, [])

    assert isinstance(str(proxy.allFilms), str)
    assert isinstance(repr(proxy.allFilms), str)

    request = proxy.allFilms.create_request()
    assert isinstance(request, GraphQLRequest)

    assert (
        request.query
        == "query allFilms { allFilms { pageInfo { hasNextPage hasPreviousPage startCursor endCursor } edges { cursor } totalCount films { title episodeID openingCrawl director producers releaseDate created edited id } } }"
    )
    assert request.variables == {}
    assert request.operation_name == "allFilms"
    assert request.context is None
    assert request.root is None


def test_query_proxy_with_illegal_input(swapi_schema, fake_backend):
    proxy = QueryServiceProxy(fake_backend, Settings(), swapi_schema, [])

    with pytest.raises(KeyError):
        proxy.allFilms.create_request(foo="bar")


def test_query_service_proxy(swapi_schema, fake_backend):
    proxy = QueryServiceProxy(fake_backend, Settings(), swapi_schema, [])

    assert isinstance(str(proxy), str)
    assert isinstance(repr(proxy), str)

    assert "allFilms" in proxy
    assert proxy["allFilms"] == proxy.allFilms

    with pytest.raises(AttributeError):
        _ = proxy["iDoNotExists"]
