import json
import pytest
from app import plan_with_mock, _parse_plan

def test_mock_planner_cancel_and_email():
    plan = plan_with_mock(
    "Cancel my order #9921 and email me the confirmation at amlan@example.com."
    )
    assert len(plan.steps) == 2
    assert plan.steps[0].tool == "cancel_order"
    assert plan.steps[0].args["order_id"] == "9921"
    assert plan.steps[1].tool == "send_email"
    assert plan.steps[1].depends_on == ["step_1"]

def test_mock_planner_cancel_only():
    plan = plan_with_mock("Cancel order #5001")
    assert len(plan.steps) == 1
    assert plan.steps[0].tool == "cancel_order"

def test_mock_planner_unknown_request():
    with pytest.raises(ValueError, match="could not parse"):
        plan_with_mock("What is the weather today?")

def test_parse_plan_valid_json():
    raw = json.dumps([
    {"id": "s1", "tool": "cancel_order", "args": {"order_id": "1"}, "depends_on": []},
    {"id": "s2", "tool": "send_email", "args": {"email": "a@b.com", "message": "done"}, "depends_on": ["s1"]},
    ])
    plan = _parse_plan(raw)
    assert len(plan.steps) == 2
    assert plan.steps[1].depends_on == ["s1"]