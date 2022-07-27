from qlient.core.schema.models import Type
from qlient.core.schema.schema import Schema


# skipcq: PY-D0003
def test_schema(swapi_schema):

    assert isinstance(swapi_schema, Schema)
    assert isinstance(swapi_schema.query_type, Type)
    assert swapi_schema.query_type.name == "Root"
    assert swapi_schema.mutation_type is None
    assert swapi_schema.subscription_type is None

    # check if __getattr__ works
    assert swapi_schema.Root == swapi_schema.query_type

    assert (
        str(swapi_schema)
        == "<Schema(query_type=<Type(name=`Root`)>, mutation_type=None, subscription_type=None)>"
    )
