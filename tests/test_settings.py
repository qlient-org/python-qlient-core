from qlient.core.settings import Settings


def test_settings():
    settings = Settings()
    assert settings.validate_variables

    assert str(settings) == "<Settings(validate_variables=True)>"


def test_settings_not_validate_variables():
    settings = Settings(validate_variables=False)
    assert not settings.validate_variables
    assert str(settings) == "<Settings(validate_variables=False)>"
