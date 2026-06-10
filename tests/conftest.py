import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.db import get_db

async def mock_get_db():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()

    mock_session.execute.return_value = MagicMock(
        scalars=MagicMock(
            return_value=MagicMock(
                first=MagicMock(return_value=None),
                all=MagicMock(return_value=[])
            )
        )
    )
    async def fake_refresh(obj):
        obj.id = 1
        obj.status = "pending"
    mock_session.refresh.side_effect = fake_refresh
    yield mock_session

@pytest.fixture
async def client():
    app.dependency_overrides[get_db] = mock_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()