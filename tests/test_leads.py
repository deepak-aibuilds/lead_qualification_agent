from httpx import AsyncClient
import pytest
from unittest.mock import patch

@pytest.mark.anyio
async def test_post_lead_saves_pending(client: AsyncClient):
    with patch("app.main.qualify_email_agent") as mock_task:
        response = await client.post('/leads', data={
            'name': "Deepak",
            'email': "dipu@gmail.com",
            'company': "AI",
            'budget': '1000',
            'required_service': "lead generation",
        })
    print(response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "pending"
    mock_task.assert_called_once()  