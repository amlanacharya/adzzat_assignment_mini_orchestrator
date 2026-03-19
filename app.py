from fastapi import FastAPI

app = FastAPI(
    title="Mini Agent Orchestrator",
    description="An Event driven Order Processing Agent",
)


@app.get("/health")
async def health():
    return {"status": "ok"}
