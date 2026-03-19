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
    A["POST /agent<br><i>Natural language request</i>"] --> B["Planner"]
    B --> B1["Mock (regex)"]
    B --> B2["OpenAI (gpt-4o-mini)"]
    B1 --> C["Step DAG<br><i>steps + depends_on edges</i>"]
    B2 --> C
    C --> D["Orchestrator<br><i>Wave-based async execution</i>"]
    D --> G{"Guardrail<br>pre-check"}
    G -->|deps OK| E1["cancel_order<br><i>20% failure</i>"]
    G -->|deps OK| E2["send_email<br><i>1s async</i>"]
    G -->|dep failed| SK["SKIPPED"]
    E1 -->|success| F["AgentResponse<br><i>steps + overall_status</i>"]
    E1 -->|failure| SK
    E2 --> F
    SK --> F

    classDef planner fill:#EEEDFE,stroke:#534AB7,stroke-width:1px,color:#3C3489
    classDef orchestrator fill:#E6F1FB,stroke:#185FA5,stroke-width:1px,color:#0C447C
    classDef tool fill:#EAF3DE,stroke:#3B6D11,stroke-width:1px,color:#27500A
    classDef guardrail fill:#FAECE7,stroke:#993C1D,stroke-width:1px,color:#712B13
    classDef neutral fill:#F1EFE8,stroke:#5F5E5A,stroke-width:1px,color:#444441

    class B,B1,B2 planner
    class D orchestrator
    class E1,E2 tool
    class G,SK guardrail
    class A,C,F neutral
```

## Mock tools

Mock tools (cancel_order, send_email) will simulate success/failure based on input (e.g., order ID 9921 cancels successfully, but 9922 fails).

## Planner and The plan

- What does the user want - Planner that can parse the NL input and create  a structured plan.
- A plan is a DAG of steps but how to represent it?
  - Each step will implicitly have:
    - what tool to call
    - with what args
    - what must finish first
  - Datamodel and Dataclasses to represent the plan and steps should suffice.

## How Do I Run the plan?

- Orchestrator that can take the plan and execute it respecting dependencies.
- Naive: run steps in order, one by one, waiting for each to finish before starting the next.
- Better: topological sort, then run each "wave" concurrently.

## Guardrails - What if something fails?.

- Failure is not just about retrying. It's about propagation as well.
- We need check dependency status before running a step. If any dependency failed, we should skip the step and mark it as SKIPPED in the final response.


