# skipcq: PY-D0003
import io
import json
import tempfile

import pytest

from qlient.core.models import GraphQLRequest, GraphQLResponse
from qlient.core.schema.providers import FileSchemaProvider
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
    my_file.write(json.dumps(raw_swapi_schema))
    my_file.seek(0)
    yield my_file
    my_file.close()


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

        def execute_mutation(self, *args, **kwargs):
            pass

        def execute_subscription(self, *args, **kwargs):
            pass

    my_provider = BackendSchemaProvider(MyBackend())
    assert my_provider.load_schema() == Schema(raw_swapi_schema, my_provider)
