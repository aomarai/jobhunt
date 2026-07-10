import os
import pytest
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.database import Base, get_session

if hasattr(settings.test_database_url, "unicode_string"):
    TEST_DATABASE_URL = settings.test_database_url.unicode_string()
else:
    TEST_DATABASE_URL = str(settings.test_database_url)

def pytest_configure(config):
    """Runs once before tests start to ensure the test database exists."""
    url = make_url(TEST_DATABASE_URL)
    db_name = url.database
    
    # 1. Point dynamically to the default 'postgres' database on that same container
    postgres_url = url._replace(database="postgres")
    bootstrap_engine = create_engine(postgres_url)
    
    # 2. Bypass transaction block requirements using AUTOCOMMIT
    with bootstrap_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        # Query postgres catalog to see if 'job_test' already exists
        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :db_name"), 
            {"db_name": db_name}
        )
        if not result.scalar():
            # If missing, spin it up right on your psql container
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
            
    bootstrap_engine.dispose()

engine = create_engine(TEST_DATABASE_URL)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_session():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def api_login(client):
    """Creates a user, logs user into the API and returns the auth token."""
    email = f"{uuid.uuid4()}@example.com"
    password = str(uuid.uuid4())
    client.post(
        "/auth/register",
        json={"email":email, "password":password}
    )
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password}
    )
    return response.json()["access_token"]


@pytest.fixture
def create_company(client, api_login):
    """Returns a factory function to create a company with custom details."""
    auth_token = api_login
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    def _create_company(name="Default Corp", website="https://example.com", notes="Test notes"):
        response = client.post(
            "/companies",
            json={
                "name": name,
                "website": website,
                "notes": notes
            },
            headers=headers
        )
        return response.json()
        
    return _create_company


@pytest.fixture
def create_application(client, api_login):
    """Returns a factory function to create a job application with custom details."""
    auth_token = api_login
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    def _create_application(
        company_id: str,
        job_id: str,
        job_title: str,
        job_url: str,
        status: str,
        notes: str
    ):
        response = client.post(
            "/applications",
            json={
                "company_id": company_id,
                "job_id": job_id,
                "job_title": job_title,
                "job_url": job_url,
                "status": status,
                "notes": notes
            },
            headers = headers
        )
        return response.json()
    return _create_application