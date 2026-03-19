import pytest
from unittest.mock import patch
from app import cancel_order, send_email

@pytest.mark.asyncio
async def test_cancel_order_success():
    with patch("app.random.random", return_value=0.5):
        result = await cancel_order("9921")
    assert result["cancelled"] is True
    assert result["order_id"] == "9921"
@pytest.mark.asyncio
async def test_cancel_order_failure():
    with patch("app.random.random", return_value=0.1):
        with pytest.raises(RuntimeError, match="Order service unavailable"):
            await cancel_order("9921")
@pytest.mark.asyncio
async def test_send_email():
    result = await send_email("amlan@example.com", "Your order was cancelled.")
    assert result["sent"] is True
    assert result["email"] == "amlan@example.com"