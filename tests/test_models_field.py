from qlient.core.models import Field, Directive, Fields


# skipcq: PY-D0003
def test_simple_field():
    actual = Field("a")
    assert actual.name == "a"


# skipcq: PY-D0003
def test_simple_field_with_values():
    actual = Field(
        "repo",
        last=5,
        _alias="repo_alias",
        _directive=Directive("include"),
        _sub_fields=["name"],
    )
    assert actual.name == "repo"
    assert actual.alias == "repo_alias"
    assert actual.directive is not None
    assert actual.directive.name == "include"
    assert "last" in actual.variables
    assert actual.variables["last"] == 5
    assert actual.sub_fields is not None
    assert isinstance(actual.sub_fields, Fields)


# skipcq: PY-D0003
def test_field_add_other_field():
    a = Field("a")
    b = Field("b")
    expected = Fields(a, b)
    actual = a + b
    assert actual == expected
