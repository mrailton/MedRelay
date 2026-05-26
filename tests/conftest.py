import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["APP_ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key"

from medrelay.config import get_settings

get_settings.cache_clear()

from medrelay.db.base import Base
from medrelay.db import models  # noqa: F401
from medrelay.main import app
from medrelay.db.session import get_db
from tests.factories import create_user, create_event, make_incident


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


@pytest.fixture
def auth_client(client, controller_user):
    client.post(
        "/login",
        data={"email": controller_user.email, "password": "password", "csrf_token": "test"},
        follow_redirects=False,
    )
    return client
