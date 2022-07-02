# skipcq: PY-D0003
from qlient.core.models import GraphQLRequest, GraphQLResponse


# skipcq: PY-D0003
def test_file_schema_provider_tempfile():
    import tempfile
    from qlient.core.schema.providers import FileSchemaProvider

    my_file = tempfile.NamedTemporaryFile()
    my_file.write(b'{"foo": "bar"}')
    my_file.seek(0)
    my_provider = FileSchemaProvider(my_file)
    assert my_provider.load_schema() == {"foo": "bar"}
    assert my_provider.schema_cache_key == my_file.name
    my_file.close()


# skipcq: PY-D0003
def test_file_schema_provider_tempfile_context():
    import tempfile
    from qlient.core.schema.providers import FileSchemaProvider

    with tempfile.NamedTemporaryFile() as my_file:
        my_file.write(b'{"foo": "bar"}')
        my_file.seek(0)
        my_provider = FileSchemaProvider(my_file)
        assert my_provider.load_schema() == {"foo": "bar"}
        assert my_provider.schema_cache_key == my_file.name


# skipcq: PY-D0003
def test_file_schema_provider_bytes_io():
    import io
    from qlient.core.schema.providers import FileSchemaProvider

    my_file = io.BytesIO(b'{"foo": "bar"}')
    my_file.name = "My Bytes File"
    my_provider = FileSchemaProvider(my_file)
    assert my_provider.load_schema() == {"foo": "bar"}
    assert my_provider.schema_cache_key == "My Bytes File"


# skipcq: PY-D0003
def test_file_schema_provider_string_io():
    import io
    from qlient.core.schema.providers import FileSchemaProvider

    my_file = io.StringIO('{"foo": "bar"}')
    my_file.name = "My String File"
    my_provider = FileSchemaProvider(my_file)
    assert my_provider.load_schema() == {"foo": "bar"}
    assert my_provider.schema_cache_key == "My String File"


# skipcq: PY-D0003
def test_backend_schema_provider():
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
            return GraphQLResponse(request, {"data": {"__schema": {"foo": "bar"}}})

        def execute_mutation(self, *args, **kwargs):
            pass

        def execute_subscription(self, *args, **kwargs):
            pass

        @property
        def schema_identifier(self) -> str:
            return "My Backend Provider"

    my_provider = BackendSchemaProvider(MyBackend())
    assert my_provider.load_schema() == {"foo": "bar"}
    assert my_provider.schema_cache_key == "My Backend Provider"
