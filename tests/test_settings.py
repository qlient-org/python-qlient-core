from qlient.core.settings import Settings


def test_settings():
    settings = Settings()
    assert settings.validate_variables


def test_settings_not_validate_variables():
    assert not Settings(validate_variables=False).validate_variables
