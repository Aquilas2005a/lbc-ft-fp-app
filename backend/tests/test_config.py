from app.core.config import Settings


def test_settings_encode_special_characters_in_generated_database_url() -> None:
    settings = Settings(
        _env_file=None,
        postgres_db="lbc_db",
        postgres_user="lbc_user",
        postgres_password="password@local",
        postgres_host="localhost",
        postgres_port=5433,
        database_url=None,
    )

    assert settings.resolved_database_url == (
        "postgresql+psycopg://lbc_user:password%40local@localhost:5433/lbc_db"
    )


def test_settings_split_csv_cors_origins() -> None:
    settings = Settings(
        _env_file=None,
        cors_origins="http://localhost:5173, http://127.0.0.1:5173",
    )

    assert settings.cors_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
