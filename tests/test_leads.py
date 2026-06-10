import pytest

@pytest.mark.anyio
async def test_leads(client):
    response = await client.post('/leads/4')
    assert response.status_code == 200