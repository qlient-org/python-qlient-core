import pytest

from qlient.core.models import Field, Directive, Fields, PreparedDirective


# skipcq: PY-D0003
def test_directive():
    actual = Directive("my_directive")
    assert actual.name == "my_directive"


# skipcq: PY-D0003
def test_directive_hash():
    assert isinstance(hash(Directive("foo")), int)


# skipcq: PY-D0003
def test_directive_comparison():
    assert Directive("foo") == Directive("foo")


# skipcq: PY-D0003
def test_directive_comparison_with_different_type():
    with pytest.raises(TypeError):
        assert Directive("foo") == 0


# skipcq: PY-D0003
def test_prepared_directive(swapi_schema):
    my_directive = Directive("include")
    prepared_directive = my_directive.prepare(swapi_schema)
    assert isinstance(prepared_directive, PreparedDirective)


# skipcq: PY-D0003
def test_prepared_directive_gql(swapi_schema):
    my_directive = Directive("include")
    prepared_directive = my_directive.prepare(swapi_schema)
    assert prepared_directive.__gql__() == "@include"
    assert prepared_directive.__gql__() == str(prepared_directive)


def test_prepared_directive_prepare_name():
    PreparedDirective().prepare_name("foo")
    assert True


@pytest.mark.parametrize("invalid_name", ["", None])
def test_prepared_directive_prepare_name_invalid_name(invalid_name):
    with pytest.raises(ValueError):
        PreparedDirective().prepare_name(invalid_name)


def test_prepare_type_checking(swapi_schema):
    directive = PreparedDirective()
    directive.prepare_name("include")
    directive.prepare_type_checking(swapi_schema)
    assert directive.schema_directive.name == "include"


def test_prepare_type_checking_with_unknown_name(swapi_schema):
    directive = PreparedDirective()
    directive.prepare_name("directiveThatDoesNotExist")

    with pytest.raises(ValueError):
        directive.prepare_type_checking(swapi_schema)


def test_prepare_type_checking_with_no_name(swapi_schema):
    directive = PreparedDirective()
    with pytest.raises(ValueError):
        directive.prepare_type_checking(swapi_schema)


def test_prepared_directive__hash__(swapi_schema):
    directive = PreparedDirective()
    directive.prepare_name("include")
    assert isinstance(hash(directive), int)


def test_prepared_directive__eq__():
    directive_a = PreparedDirective()
    directive_a.prepare_name("include")

    directive_b = PreparedDirective()
    directive_b.prepare_name("include")

    assert directive_a == directive_b


def test_prepared_directive__eq__wrong_type():
    directive_a = PreparedDirective()
    directive_a.prepare_name("include")

    with pytest.raises(TypeError):
        directive_a == 1  # noqa


# skipcq: PY-D0003
def test_simple_field():
    actual = Field("a")
    assert actual.name == "a"


# skipcq: PY-D0003
def test_field_add_other_field():
    a = Field("a")
    b = Field("b")
    expected = Fields(a, b)
    actual = a + b
    assert actual == expected


# skipcq: PY-D0003
def test_field_add_list():
    a = Field("a")
    actual = a + ["b", "c"]

    assert "a" in actual
    assert "b" in actual
    assert "c" in actual


# skipcq: PY-D0003
def test_field_add_set():
    a = Field("a")
    actual = a + {"b", "c", "c"}

    assert "a" in actual
    assert "b" in actual
    assert "c" in actual


# skipcq: PY-D0003
def test_field_add_tuple():
    a = Field("a")
    actual = a + ("b", "c")

    assert "a" in actual
    assert "b" in actual
    assert "c" in actual


# skipcq: PY-D0003
def test_field_add_dict():
    a = Field("a")
    actual = a + {"b": "c"}
    assert actual == Fields("a", b="c")


def test_field_add_unknown():
    with pytest.raises(TypeError):
        Field("a") + object()


# skipcq: PY-D0003
def test_field_and_other_field():
    a = Field("a")
    b = Field("b")
    expected = Fields(a, b)
    actual = a & b
    assert actual == expected


def test_field_eq_unknown():
    with pytest.raises(TypeError):
        assert Field("a") == object()


# skipcq: PY-D0003
def test_fields_simple_single():
    a = Fields("a")
    assert a.selected_fields == [Field("a")]


# skipcq: PY-D0003
def test_fields_simple_multiple():
    a = Fields("a", "b", "c")
    assert Field("a") in a.selected_fields
    assert Field("b") in a.selected_fields
    assert Field("c") in a.selected_fields


# skipcq: PY-D0003
def test_fields_simple_multiple_duplicates():
    a = Fields("a", "b", "c", "c", "c")
    assert len(a.selected_fields) == 3


# skipcq: PY-D0003
def test_fields_simple_list():
    a = Fields(["a", "b", "c"])
    assert Field("a") in a.selected_fields
    assert Field("b") in a.selected_fields
    assert Field("c") in a.selected_fields


# skipcq: PY-D0003
def test_fields_simple_list_duplicates():
    fields = ["a", "b", "c", "c", "c"]
    a = Fields(fields)
    assert len(a.selected_fields) == 3


# skipcq: PY-D0003
def test_fields_complex_simple():
    a = Fields("a", "b", c="d")
    assert Field("a") in a.selected_fields
    assert Field("b") in a.selected_fields
    assert Field("c", _sub_fields=Fields("d")) in a.selected_fields


# skipcq: PY-D0003
def test_fields_complex_simple_list():
    a = Fields("a", "b", c=["a", "b"])
    assert Field("a") in a.selected_fields
    assert Field("b") in a.selected_fields
    assert Field("c", _sub_fields=Fields("a", "b")) in a.selected_fields


# skipcq: PY-D0003
def test_fields_complex_nested_fields():
    a = Fields(a=Fields("a"), b=Fields("b"))
    assert Field("a", _sub_fields="a") in a.selected_fields
    assert Field("b", _sub_fields="b") in a.selected_fields


# skipcq: PY-D0003
def test_fields_simple_eq_operator():
    a = Fields("a")
    b = Fields("a")
    assert a == b


# skipcq: PY-D0003
def test_fields_simple_eq_operator_not():
    a = Fields("a")
    b = Fields("b")
    assert a != b


# skipcq: PY-D0003
def test_fields_complex_eq_operator():
    a = Fields("a", b="c")
    b = Fields("a", b="c")
    assert a == b


# skipcq: PY-D0003
def test_fields_complex_eq_operator_not():
    a = Fields("a", b="c")
    b = Fields("a", b="d")
    assert a != b


# skipcq: PY-D0003
def test_fields_simple_add_operator_simple():
    a = Fields("a")
    expected = Fields("a", "b")
    actual = a + "b"
    assert expected == actual


# skipcq: PY-D0003
def test_fields_simple_and_operator_simple():
    a = Fields("a")
    expected = Fields("a", "b")
    actual = a & "b"
    assert expected == actual


# skipcq: PY-D0003
def test_fields_simple_add_operator_list():
    a = Fields("a")
    expected = Fields("a", "b", "c")
    actual = a + ["b", "c"]
    assert expected == actual


# skipcq: PY-D0003
def test_fields_simple_add_operator_dict():
    a = Fields("a")
    expected = Fields("a", b="c")
    actual = a + {"b": "c"}
    assert expected == actual


# skipcq: PY-D0003
def test_fields_simple_add_operator_fields():
    a = Fields("a")
    b = Fields("a", "b", c="d")
    expected = Fields("a", "b", c="d")
    actual = a + b
    assert expected == actual


# skipcq: PY-D0003
def test_fields_complex_add_operator_simple():
    a = Fields("a", b="b")
    actual = a + "c"
    assert Field("a") in actual.selected_fields
    assert Field("b", _sub_fields="b") in actual.selected_fields
    assert Field("c") in actual.selected_fields


# skipcq: PY-D0003
def test_fields_complex_add_operator_list():
    a = Fields("a", b="b")
    actual = a + ["a", "c", "z"]
    assert Field("a") in actual.selected_fields
    assert Field("b", _sub_fields="b") in actual.selected_fields
    assert Field("c") in actual.selected_fields
    assert Field("z") in actual.selected_fields


# skipcq: PY-D0003
def test_fields_complex_add_operator_dict():
    a = Fields("a", b="b")
    actual = a + {"b": ["c", "e"]}
    assert Field("a") in actual.selected_fields
    assert Field("b", _sub_fields=["c", "e"]) in actual.selected_fields


# skipcq: PY-D0003
def test_fields_complex_add_operator_fields():
    a = Fields("a", b="b")
    b = Fields("a", "c")
    actual = a + b
    assert Field("a") in actual.selected_fields
    assert Field("c") in actual.selected_fields
    assert Field("b", _sub_fields="b") in actual.selected_fields


def test_graphql_request(graphql_request):
    assert graphql_request.query == "query testOperation { testOperation { foo bar } }"
    assert graphql_request.variables == {"limit": 1}
    assert graphql_request.operation_name == "testOperation"


def test_graphql_subscription_request(graphql_subscription_request):
    assert graphql_subscription_request.subscription_id == "1"
    assert graphql_subscription_request.options == {"auth": "test"}
    assert (
        graphql_subscription_request.query
        == "query testOperation { testOperation { foo bar } }"
    )
    assert graphql_subscription_request.variables == {"limit": 1}
    assert graphql_subscription_request.operation_name == "testOperation"


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
