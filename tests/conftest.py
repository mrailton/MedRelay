import os
from collections.abc import Generator

# Must happen before any app imports
os.environ["APP_ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import security as _security
from app.config import get_settings
from app.db import models  # noqa: F401
from app.db.base import Base
from app.db.session import engine as module_engine
from app.main import app
from app.repositories.session import get_db
from tests.factories import create_organisation, create_user

# Use plaintext passwords in tests — bcrypt with 12 rounds is 200ms+ per hash
_security.pwd_context = CryptContext(schemes=["plaintext"])

get_settings.cache_clear()


@pytest.fixture(scope="session")
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


@pytest.fixture(autouse=True)
def _clean_db(db_engine):
    yield
    with db_engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        for table in Base.metadata.sorted_tables:
            conn.execute(table.delete())
        conn.commit()


@pytest.fixture
def client(db_engine, db_session):
    Session = sessionmaker(bind=db_engine)

    def override_get_db() -> Generator[Session]:
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
def organisation(db_session):
    return create_organisation(db_session, code="testorg", name="Test Organisation")


@pytest.fixture
def admin_user(db_session, organisation):
    return create_user(db_session, role="ADMIN", organisation=organisation)


@pytest.fixture
def controller_user(db_session, organisation):
    return create_user(db_session, role="CONTROLLER", organisation=organisation)


@pytest.fixture(autouse=True)
def _dispose_module_engine():
    yield
    module_engine.dispose()


@pytest.fixture
def auth_client(client, controller_user, organisation):
    client.post(
        "/login",
        data={"organisation_code": organisation.code, "email": controller_user.email, "password": "password", "csrf_token": "test"},
        follow_redirects=False,
    )
    return client
