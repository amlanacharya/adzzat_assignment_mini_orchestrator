import time
from unittest.mock import patch

import pytest

from app import Plan, Step, execute_plan, plan_with_mock


@pytest.mark.asyncio
async def test_orchestrator_all_success():
    """When cancel succeeds, email should also execute."""
    with patch("app.random.random", return_value=0.5):
        plan = plan_with_mock(
            "Cancel order #9921 and email user@example.com confirmation."
        )
        results = await execute_plan(plan)

    assert results[0]["status"] == "success"
    assert results[1]["status"] == "success"


@pytest.mark.asyncio
async def test_orchestrator_cancel_fails_email_skipped():
    """When cancel fails, email must be skipped."""
    with patch("app.random.random", return_value=0.05):
        plan = plan_with_mock(
            "Cancel order #9921 and email user@example.com confirmation."
        )
        results = await execute_plan(plan)

    assert results[0]["status"] == "failed"
    assert results[1]["status"] == "skipped"
    assert "upstream" in results[1]["error"]


@pytest.mark.asyncio
async def test_orchestrator_unknown_tool():
    plan = Plan(steps=[Step(id="s1", tool="nonexistent", args={})])

    results = await execute_plan(plan)

    assert results[0]["status"] == "failed"
    assert "Unknown tool" in results[0]["error"]


@pytest.mark.asyncio
async def test_independent_steps_run_concurrently():
    """Two independent steps should finish in about 1s, not 2s."""
    plan = Plan(
        steps=[
            Step(
                id="s1",
                tool="send_email",
                args={"email": "a@b.com", "message": "hi"},
            ),
            Step(
                id="s2",
                tool="send_email",
                args={"email": "c@d.com", "message": "bye"},
            ),
        ]
    )

    t0 = time.monotonic()
    results = await execute_plan(plan)
    elapsed = time.monotonic() - t0

    assert all(result["status"] == "success" for result in results)
    assert elapsed < 1.8, f"Steps ran sequentially? elapsed={elapsed:.2f}s"
