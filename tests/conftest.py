import pytest


@pytest.fixture
def swapi_schema():
    from qlient.core.schema.schema import Schema
    from _schema import raw_schema

    return Schema.from_raw(raw_schema, None)
