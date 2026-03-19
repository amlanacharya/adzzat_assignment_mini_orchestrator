# Mini Agent Orchestrator
A lightweight, event-driven order processing agent that receives natural language
requests, decomposes them into an executable plan, and runs async tools with
dependency-aware orchestration.
## Problem
Given: "Cancel my order 9921 and email me the confirmation at user@example.com."
The system should:

Parse the NL input into structured steps -Planner
Execute mock tools asynchronously -Tool Executor/Tools
Respect dependencies between steps -Orchestrator
Handle failures gracefully i.e don't send email if cancellation failed-Failure Handlinganmd Guardrails

## Initial Design Sketch

```mermaid
flowchart TD
    A[User Request (NL)] --> B[Planner]
    B --> C[Step DAG: {cancel_order 9921}, {send_email depends_on: cancel}]
    C --> D[Orchestrator]
    D --> E[Tool Results + Overall Status]

    B:::planner
    D:::orchestrator

    classDef planner fill:#f9f,stroke:#333,stroke-width:2px;
    classDef orchestrator fill:#bbf,stroke:#333,stroke-width:2px;
```

## Mock tools

Mock tools (cancel_order, send_email) will simulate success/failure based on input (e.g., order ID 9921 cancels successfully, but 9922 fails).
