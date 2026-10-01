from app.config import Settings


def test_settings_defaults():
    """Verify application configuration has sensible default settings."""
    settings = Settings()
    assert settings.APP_NAME == "Spendable API"
    assert settings.PORT == 8000
    assert "http://localhost:5173" in settings.CORS_ORIGINS


def test_settings_cors_parsing():
    """Verify CORS origins string parsing works as expected."""
    settings = Settings(CORS_ORIGINS="http://example.com,http://localhost:3000")
    assert isinstance(settings.CORS_ORIGINS, list)
    assert "http://example.com" in settings.CORS_ORIGINS
    assert "http://localhost:3000" in settings.CORS_ORIGINS
