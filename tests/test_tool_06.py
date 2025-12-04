# tests/test_tool_06.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_tool6_page_loads():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/tool/6")
    assert response.status_code == 200
    assert "无水印" in response.text

@pytest.mark.asyncio
async def test_download_api_rejects_empty():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/download", data={"url": ""})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
