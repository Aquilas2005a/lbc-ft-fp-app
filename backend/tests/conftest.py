import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings


def _build_test_database_url() -> str:
    configured_url = os.getenv("TEST_DATABASE_URL")
    if configured_url:
        return configured_url

    project_url = make_url(Settings().resolved_database_url)
    return project_url.set(database="lbc_test").render_as_string(hide_password=False)


TEST_DATABASE_URL = _build_test_database_url()
TEST_DATABASE_NAME = make_url(TEST_DATABASE_URL).database

if TEST_DATABASE_NAME != "lbc_test":
    raise RuntimeError("TEST_DATABASE_URL must target the lbc_test database.")

os.environ["DATABASE_URL"] = TEST_DATABASE_URL
get_settings.cache_clear()

from app.db.session import get_db
from app.main import app


def _ensure_test_database() -> None:
    test_url = make_url(TEST_DATABASE_URL)
    admin_engine = create_engine(
        test_url.set(database="postgres"),
        isolation_level="AUTOCOMMIT",
    )

    try:
        with admin_engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
                {"database_name": TEST_DATABASE_NAME},
            ).scalar()
            if not exists:
                connection.exec_driver_sql(f'CREATE DATABASE "{TEST_DATABASE_NAME}"')
    finally:
        admin_engine.dispose()


_ensure_test_database()
test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db: Session = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def migrated_test_database():
    with test_engine.begin() as connection:
        connection.execute(text("DROP SCHEMA public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))

    alembic_config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    command.upgrade(alembic_config, "head")
    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()
    test_engine.dispose()
