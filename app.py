from fastapi import FastAPI
from typing import Any
import asyncio
import random
import json
from enum import Enum
from dataclasses import dataclass, field
import re
import os
import httpx

app = FastAPI(
    title="Mini Agent Orchestrator",
    description="An Event driven Order Processing Agent",
)

class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
@dataclass
class Step:
    id: str
    tool: str
    args: dict[str, Any]
    depends_on: list[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: str | None = None
@dataclass
class Plan:
    steps: list[Step]
    raw_llm_output: str = ""


TOOL_REGISTRY: dict[str, Any] = {}

def register_tool(fn):
    TOOL_REGISTRY[fn.__name__] = fn
    return fn

@register_tool
async def cancel_order(order_id: str) -> dict:
    """Cancel an order. Simulates 20% random failure rate."""
    await asyncio.sleep(0.3)
    if random.random() < 0.2:
        raise RuntimeError(f"Order service unavailable - failed to cancel order {order_id}")
    return {"order_id": order_id, "cancelled": True}

@register_tool
async def send_email(email: str, message: str) -> dict:
    """Send an email. Simulates async email dispatch."""
    await asyncio.sleep(1.0)
    return {"email": email, "sent": True, "message_preview": message[:80]}


def plan_with_mock(user_request: str) -> Plan:
    """Deterministic mock planner. Parses common patterns without an LLM."""
    text = user_request.lower()
 
    order_match = re.search(r"#?(\d{4,})", user_request)
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w]+(?:\.[\w]+)*", user_request)
 
    steps: list[dict] = []
 
    if "cancel" in text and order_match:
        steps.append({
            "id": "step_1",
            "tool": "cancel_order",
            "args": {"order_id": order_match.group(1)},
            "depends_on": [],
        })
 
    if email_match:
        order_id = order_match.group(1) if order_match else "unknown"
        email_step = {
            "id": f"step_{len(steps) + 1}",
            "tool": "send_email",
            "args": {
                "email": email_match.group(0),
                "message": f"Your order #{order_id} has been cancelled successfully.",
            },
            "depends_on": [s["id"] for s in steps],  
        }
        steps.append(email_step)
 
    if not steps:
        raise ValueError(f"Mock planner could not parse request: {user_request}")
 
    raw = json.dumps(steps)
    return _parse_plan(raw)
 
 
def _parse_plan(raw: str) -> Plan:
    """Parse raw JSON string into a Plan with Steps."""
    cleaned = raw.strip().removeprefix("```json").removesuffix("```").strip()
    data = json.loads(cleaned)
    steps = [
        Step(
            id=s["id"],
            tool=s["tool"],
            args=s.get("args", {}),
            depends_on=s.get("depends_on", []),
        )
        for s in data
    ]
    return Plan(steps=steps, raw_llm_output=raw)


PLAN_SYSTEM_PROMPT = """You are a task planner for an order processing system.

Given a user request, output a JSON array of steps. Each step has:
- "id": unique step identifier (e.g. "step_1")
- "tool": one of ["cancel_order", "send_email"]
- "args": dict of arguments for the tool
- "depends_on": list of step ids that must succeed before this step runs

Tool signatures:
- cancel_order(order_id: str) -> cancels an order
- send_email(email: str, message: str) -> sends an email

Rules:
- If sending an email depends on a prior step succeeding, list that step in depends_on.
- Extract order IDs, email addresses, and compose appropriate messages from context.
- Output ONLY the JSON array, no markdown fences, no explanation."""



async def plan_with_openai(user_request: str) -> Plan:
    """Call OpenAI API to parse NL into a step plan."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set. Use mock planner or set the key.")

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "gpt-4o-mini",
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": PLAN_SYSTEM_PROMPT}, #TODO:Revisit for open ai key testing.
                    {"role": "user", "content": user_request},
                ],
            },
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]
    return _parse_plan(raw)


async def execute_plan(plan: Plan) -> list[dict]:
    """Execute plan steps sequentially."""
    for step in plan.steps:
        tool_fn = TOOL_REGISTRY.get(step.tool)
        if not tool_fn:
            step.status = StepStatus.FAILED
            step.error = f"Unknown tool: {step.tool}"
            continue  

        step.status = StepStatus.RUNNING
        try:
            step.result = await tool_fn(**step.args)
            step.status = StepStatus.SUCCESS
        except Exception as exc:
            step.status = StepStatus.FAILED
            step.error = str(exc)

    return [
        {
            "id": s.id,
            "tool": s.tool,
            "args": s.args,
            "status": s.status.value,
            "result": s.result,
            "error": s.error,
        }
        for s in plan.steps
    ]


@app.get("/health")
async def health():
    return {"status": "ok","tools": list(TOOL_REGISTRY.keys())}
