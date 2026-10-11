"""FloodLens Kenya API.

Routes
- GET  /health                      no auth; mode and pinned versions
- POST /messages                    any role; agent routes to an MCP tool
- GET  /review-queue                officer only; scores and reasons, never text or photos
- POST /alerts/{alert_id}/approve   officer only; the human gate

Run: uvicorn services.reports.app:app --port 8080
"""
import logging

import anyio
from fastapi import Depends, FastAPI, HTTPException, Response

from agents import agent
from services.reports import pins, store
from services.reports.auth import current_user, require_officer
from services.reports.logging_setup import configure
from services.reports.schemas import ApproveOut, MessageIn, MessageOut
from services.reports.settings import config, is_stub, mode

configure()
log = logging.getLogger("floodlens.api")

_problems = pins.verify_pins()
if _problems:
    raise RuntimeError(f"pin check failed, refusing to start: {_problems}")

app = FastAPI(title="FloodLens Kenya", version="1.0.0")


def _envelope(out: dict) -> dict:
    p = pins.load_pins()
    stub = is_stub()
    return {**out, "mode": "stub" if stub else "live", "prompt_version": p["prompt_version"],
            "model_id": pins.active_model_id(stub)}


def handle_message(payload: dict, stub: bool = True, role: str = "reporter") -> dict:
    """Synchronous entry point used by tests and scripts (same path as POST /messages)."""
    msg = MessageIn(**payload).model_dump()
    out = agent.handle(msg, role=role)
    env = _envelope(out)
    if stub:
        env["mode"] = "stub"
    return MessageOut(**env).model_dump()


@app.get("/health")
def health(response: Response) -> dict:
    p = pins.load_pins()
    response.headers["X-Prompt-Version"] = p["prompt_version"]
    return {"status": "ok", "service": config()["project"], "mode": mode(),
            "prompt_version": p["prompt_version"], "model_id": pins.active_model_id(is_stub())}


@app.post("/messages", response_model=MessageOut)
async def post_message(body: MessageIn, user: dict = Depends(current_user)) -> dict:
    out = await agent.handle_async(body.model_dump(), role=user["role"])
    if out["status"] == "forbidden":
        raise HTTPException(status_code=403, detail=out["result"]["error"])
    log.info("message routed=%s tool=%s role=%s", out["route"], out["tool"], user["role"])
    return _envelope(out)


@app.get("/review-queue")
def review_queue(user: dict = Depends(current_user), limit: int = 20) -> dict:
    require_officer(user)
    rows = store.queue(limit)
    return {"count": len(rows), "items": rows}


@app.post("/alerts/{alert_id}/approve", response_model=ApproveOut)
async def approve(alert_id: str, user: dict = Depends(current_user)) -> dict:
    require_officer(user)
    alert = await anyio.to_thread.run_sync(store.approve, alert_id, user["user"])
    if alert is None:
        raise HTTPException(status_code=404, detail="alert not found")
    log.info("alert=%s approved_by=%s", alert_id, user["user"])
    return {"alert_id": alert_id, "status": alert["status"], "approved_by": alert["approved_by"]}
