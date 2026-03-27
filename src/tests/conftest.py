import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
import uuid

from app.main import app
from app.dependencies import get_db, get_current_user
from app.models.user import User

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def mock_user():
    return User(
        id=uuid.uuid4(),
        supabase_uid=str(uuid.uuid4()),
        name="Test Passenger",
        email="passenger@goalong.com",
        phone="1234567890",
        role="passenger"
    )

@pytest.fixture
def mock_driver():
    return User(
        id=uuid.uuid4(),
        supabase_uid=str(uuid.uuid4()),
        name="Test Driver",
        email="driver@goalong.com",
        phone="0987654321",
        role="driver"
    )

@pytest.fixture
def client(mock_db, mock_user):
    async def override_get_db():
        yield mock_db
        
    async def override_get_current_user():
        return mock_user
        
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    with TestClient(app) as c:
        yield c
        
    app.dependency_overrides.clear()
