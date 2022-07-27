from qlient.core.settings import Settings


def test_settings():
    settings = Settings()
    assert settings.allow_auto_lookup
    assert settings.lookup_recursion_depth
    assert settings.use_schema_description

    assert isinstance(str(settings), str)
