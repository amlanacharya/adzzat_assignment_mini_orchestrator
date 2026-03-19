from httpx import ASGITransport, AsyncClient

import pytest

from app import app


@pytest.mark.asyncio
async def test_agent_endpoint_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/agent",
            json={
                "request": "Cancel order #9921 and email user@example.com confirmation.",
                "use_mock_planner": True,
            },
        )

    data = resp.json()

    assert resp.status_code == 200
    assert data["overall_status"] in ("success", "partial_failure")
    assert len(data["steps"]) == 2


@pytest.mark.asyncio
async def test_agent_endpoint_bad_request():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/agent",
            json={
                "request": "What is the meaning of life?",
                "use_mock_planner": True,
            },
        )

    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")

    data = resp.json()

    assert resp.status_code == 200
    assert data["status"] == "ok"
    assert "cancel_order" in data["tools"]
    assert "send_email" in data["tools"]
