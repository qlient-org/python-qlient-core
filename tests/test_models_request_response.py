import pytest

from qlient.core.models import GraphQLRequest, GraphQLResponse


@pytest.fixture
def graphql_request() -> GraphQLRequest:
    return GraphQLRequest(
        query="query testOperation { testOperation { foo bar } }",
        variables={"limit": 1},
        operation_name="testOperation",
    )


@pytest.fixture
def graphql_response(graphql_request) -> GraphQLResponse:
    return GraphQLResponse(
        graphql_request,
        {
            "data": {"testOperation": {"foo": "", "bar": ""}},
            "errors": [],
            "extensions": [],
        },
    )


def test_graphql_request(graphql_request):
    assert graphql_request.query == "query testOperation { testOperation { foo bar } }"
    assert graphql_request.variables == {"limit": 1}
    assert graphql_request.operation_name == "testOperation"


# skipcq: PY-D0003
def test_graphql_response(graphql_response):
    assert (
        graphql_response.request.query
        == "query testOperation { testOperation { foo bar } }"
    )
    assert graphql_response.request.variables == {"limit": 1}
    assert graphql_response.request.operation_name == "testOperation"

    assert graphql_response.data == {"testOperation": {"foo": "", "bar": ""}}
    assert graphql_response.errors == []
    assert graphql_response.extensions == []
