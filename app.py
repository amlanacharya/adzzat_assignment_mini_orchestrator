from fastapi import FastAPI
from typing import Any
import asyncio
import random


app = FastAPI(
    title="Mini Agent Orchestrator",
    description="An Event driven Order Processing Agent",
)

TOOL_REGISTRY: dict[str, Any] = {}

def register_tool(fn):
    TOOL_REGISTRY[fn.name] = fn
    return fn

@register_tool
async def cancel_order(order_id: str) -> dict:
    """Cancel an order. Simulates 20% random failure rate."""
    await asyncio.sleep(0.3)
    if random.random() < 0.2:
        raise RuntimeError(f"Order service unavailable for order {order_id}")
    return {"order_id": order_id, "cancelled": True}

@register_tool
async def send_email(email: str, message: str) -> dict:
    """Send an email. Simulates async email dispatch."""
    await asyncio.sleep(1.0)
    return {"email": email, "sent": True, "message_preview": message[:80]}


@app.get("/health")
async def health():
    return {"status": "ok","tools": list(TOOL_REGISTRY.keys())}
