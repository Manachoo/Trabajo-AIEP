import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def _resolve_test_database_url() -> str:
    explicit_test_url = os.getenv("TEST_DATABASE_URL")
    if explicit_test_url:
        return explicit_test_url

    base_database_url = os.getenv("DATABASE_URL")
    if base_database_url:
        parsed_url = make_url(base_database_url)
        database_name = parsed_url.database or "food_delivery"
        test_url = parsed_url.set(database=f"{database_name}_test")
        return test_url.render_as_string(hide_password=False)

    return "postgresql+psycopg://food_user:food_password@localhost:5432/food_delivery_test"


TEST_DATABASE_URL = _resolve_test_database_url()
os.environ["DATABASE_URL"] = TEST_DATABASE_URL


@pytest.fixture(scope="session", autouse=True)
def configure_test_database_url():
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    return TEST_DATABASE_URL


@pytest.fixture(scope="session", autouse=True)
def ensure_test_database_exists(configure_test_database_url):
    test_url = make_url(configure_test_database_url)
    if test_url.get_backend_name() != "postgresql":
        return

    admin_url = test_url.set(database="postgres")
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": test_url.database},
            ).scalar()

            if not exists:
                connection.execute(text(f'CREATE DATABASE "{test_url.database}"'))
    finally:
        admin_engine.dispose()


@pytest.fixture(autouse=True)
def reset_database(configure_test_database_url, ensure_test_database_exists):
    from app.infrastructure.database import Base, engine, init_database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    init_database()
    yield


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from main import app

    with TestClient(app) as test_client:
        yield test_client
