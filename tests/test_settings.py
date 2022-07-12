from qlient.core.settings import Settings


def test_settings():
    settings = Settings()
    assert settings.validate_variables
    assert settings.use_schema_description


def test_settings_not_validate_variables():
    settings = Settings(validate_variables=False)
    assert not settings.validate_variables
    assert "validate_variables=False" in str(settings)


def test_settings_not_use_schema_description():
    settings = Settings(use_schema_description=False)
    assert not settings.use_schema_description
    assert "use_schema_description=False" in str(settings)
