import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings
from app.db import models  # noqa: F401
from app.db.base import Base
from app.db.session import engine as module_engine
from app.main import app
from app.repositories.session import get_db
from tests.factories import create_user

os.environ["APP_ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key"

get_settings.cache_clear()


@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def client(db_engine, db_session):
    Session = sessionmaker(bind=db_engine)

    def override_get_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    return create_user(db_session, role="ADMIN")


@pytest.fixture
def controller_user(db_session):
    return create_user(db_session, role="CONTROLLER")


@pytest.fixture(autouse=True)
def _dispose_module_engine():
    yield
    module_engine.dispose()


@pytest.fixture
def auth_client(client, controller_user):
    client.post(
        "/login",
        data={"email": controller_user.email, "password": "password", "csrf_token": "test"},
        follow_redirects=False,
    )
    return client
