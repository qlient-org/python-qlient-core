import pytest

from qlient.core.models import Directive, PreparedDirective


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
def test_directive_with_variables():
    my_directive = Directive("my_directive", foo="5")
    assert "foo" in my_directive.variables
    assert my_directive.variables["foo"] == "5"
    assert "my_directive" == my_directive.name


# skipcq: PY-D0003
def test_prepared_directive(swapi_schema):
    my_directive = Directive("include")
    prepared_directive = my_directive.prepare(swapi_schema)
    assert isinstance(prepared_directive, PreparedDirective)


# skipcq: PY-D0003
def test_prepared_directive_with_variables(swapi_schema):
    my_directive = Directive("include", **{"if": True})
    prepared_directive = my_directive.prepare(swapi_schema)
    assert isinstance(prepared_directive, PreparedDirective)
    assert prepared_directive.name == "include"
    assert "if" in prepared_directive.var_name_to_var_ref


# skipcq: PY-D0003
def test_prepared_directive_gql(swapi_schema):
    my_directive = Directive("include")
    prepared_directive = my_directive.prepare(swapi_schema)
    assert prepared_directive.__gql__() == "@include"
    assert prepared_directive.__gql__() == str(prepared_directive)


# skipcq: PY-D0003
def test_prepared_directive_with_variables_gql(swapi_schema):
    my_directive = Directive("include", **{"if": True})
    prepared_directive = my_directive.prepare(swapi_schema)
    assert (
        prepared_directive.__gql__()
        == f"@include(if: $include_{id(prepared_directive)}_if)"
    )


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


def test_prepare_input(swapi_schema):
    directive = PreparedDirective()
    directive.prepare_name("include")
    directive.prepare_type_checking(swapi_schema)
    directive.prepare_input({"if": True})

    var_ref = f"include_{id(directive)}_if"
    assert var_ref in directive.var_ref_to_var_value
    assert var_ref == directive.var_name_to_var_ref["if"]
    assert directive.var_ref_to_var_value[directive.var_name_to_var_ref["if"]]


def test_prepare_input_missing_name():
    with pytest.raises(ValueError):
        PreparedDirective().prepare_input({})


def test_prepare_input_missing_schema():
    directive = PreparedDirective()
    directive.prepare_name("include")

    with pytest.raises(ValueError):
        directive.prepare_input({})


def test_prepare_input_unknown_variable(swapi_schema):
    directive = PreparedDirective()
    directive.prepare_name("include")
    directive.prepare_type_checking(swapi_schema)

    with pytest.raises(ValueError):
        directive.prepare_input({"iDontExist": None})
