import pytest


@pytest.fixture
def swapi_schema():
    from qlient.core.schema.schema import Schema
    from qlient.core.schema.providers import StaticSchemaProvider
    from _schema import raw_schema

    return Schema.load(
        provider=StaticSchemaProvider(raw_schema["data"]["__schema"], "Test"),
        settings=None,
        cache=None,
    )
