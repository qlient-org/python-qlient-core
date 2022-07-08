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
