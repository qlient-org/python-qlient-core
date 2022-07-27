# skipcq: PY-D0003
import io
import json
import tempfile

import pytest

from conftest import path_to_swapi_schema
from qlient.core.models import GraphQLRequest, GraphQLResponse
from qlient.core.schema.providers import FileSchemaProvider, SchemaProvider
from qlient.core.schema.schema import Schema


@pytest.fixture
def tempfile_schema(raw_swapi_schema):
    my_file = tempfile.NamedTemporaryFile(mode="w+")
    json.dump(raw_swapi_schema, my_file)
    my_file.seek(0)
    yield my_file
    my_file.close()


@pytest.fixture
def bytes_io_schema(raw_swapi_schema):
    my_file = io.BytesIO()
    my_file.write(json.dumps(raw_swapi_schema).encode())
    my_file.seek(0)
    yield my_file
    my_file.close()


@pytest.fixture
def string_io_schema(raw_swapi_schema):
    my_file = io.StringIO()
    json.dump(raw_swapi_schema, my_file)
    my_file.seek(0)
    yield my_file
    my_file.close()


def test_base_schema_provider():
    with pytest.raises(NotImplementedError):
        SchemaProvider.load_schema(...)


# skipcq: PY-D0003
def test_file_schema_provider_path(raw_swapi_schema):
    my_provider = FileSchemaProvider(path_to_swapi_schema)
    assert my_provider.load_schema() == Schema(raw_swapi_schema, my_provider)


# skipcq: PY-D0003
def test_file_schema_provider_str(raw_swapi_schema):
    my_provider = FileSchemaProvider(str(path_to_swapi_schema.resolve()))
    assert my_provider.load_schema() == Schema(raw_swapi_schema, my_provider)


# skipcq: PY-D0003
def test_file_schema_provider_tempfile(tempfile_schema, raw_swapi_schema):
    my_provider = FileSchemaProvider(tempfile_schema)
    assert my_provider.load_schema() == Schema(raw_swapi_schema, my_provider)


# skipcq: PY-D0003
def test_file_schema_provider_bytes_io(bytes_io_schema, raw_swapi_schema):
    my_provider = FileSchemaProvider(bytes_io_schema)
    assert my_provider.load_schema() == Schema(raw_swapi_schema, my_provider)


# skipcq: PY-D0003
def test_file_schema_provider_string_io(string_io_schema, raw_swapi_schema):
    my_provider = FileSchemaProvider(string_io_schema)
    assert my_provider.load_schema() == Schema(raw_swapi_schema, my_provider)


# skipcq: PY-D0003
def test_backend_schema_provider(raw_swapi_schema):
    from qlient.core.schema.providers import BackendSchemaProvider
    from qlient.core.backends import Backend

    class MyBackend(Backend):

        # skipcq: PYL-R0201
        def execute_query(self, request: GraphQLRequest) -> GraphQLResponse:
            assert (
                request.operation_name
                == BackendSchemaProvider.INTROSPECTION_OPERATION_NAME
            )
            assert request.query == BackendSchemaProvider.INTROSPECTION_QUERY
            assert request.variables == {}
            assert request.context is None
            assert request.root is None
            return GraphQLResponse(request, {"data": {"__schema": raw_swapi_schema}})

        # skipcq: PTC-W0049
        def execute_mutation(self, *args, **kwargs):
            pass

        # skipcq: PTC-W0049
        def execute_subscription(self, *args, **kwargs):
            pass

    my_provider = BackendSchemaProvider(MyBackend())
    assert my_provider.load_schema() == Schema(raw_swapi_schema, my_provider)
