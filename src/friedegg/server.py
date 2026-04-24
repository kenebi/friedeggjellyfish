"""
friedegg.server — Local FastAPI server for the FEJ dashboard.

Two WebSocket endpoints:
  /ws/ingest    — receives events from user automation scripts (monitor.py)
  /ws/dashboard — pushes events to dashboard browsers

Plus a static route at / that serves the dashboard HTML/CSS/JS.

Run with:
    uvicorn friedegg.server:app --host 127.0.0.1 --port 8765

Or via the CLI:
    friedegg dashboard
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections import deque
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

_LOGGER = logging.getLogger("friedegg.server")

# Dashboard static files live next to this module.
_DASHBOARD_DIR = Path(__file__).parent / "dashboard"

# Keep the last N events in memory so a newly-opened dashboard tab
# can "catch up" on a workflow that's already running.
_HISTORY_MAXLEN = 500


# ---------------------------------------------------------------------------
# In-memory broadcaster
# ---------------------------------------------------------------------------

class Broadcaster:
    """
    Tracks connected dashboard clients and relays events from ingest to them.

    Thread-safety note: FastAPI's WebSocket handlers run in a single asyncio
    event loop, so regular Python lists are fine here — no locks needed.
    """

    def __init__(self) -> None:
        self._dashboards: set[WebSocket] = set()
        self._history: deque[dict[str, Any]] = deque(maxlen=_HISTORY_MAXLEN)

    async def connect_dashboard(self, ws: WebSocket) -> None:
        await ws.accept()
        self._dashboards.add(ws)
        # Replay history so newly-opened tabs see in-progress workflows.
        for event in self._history:
            try:
                await ws.send_json(event)
            except Exception:
                break

    def disconnect_dashboard(self, ws: WebSocket) -> None:
        self._dashboards.discard(ws)

    async def publish(self, event: dict[str, Any]) -> None:
        self._history.append(event)
        dead: list[WebSocket] = []
        for ws in self._dashboards:
            try:
                await ws.send_json(event)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._dashboards.discard(ws)

    def clear_history_for_new_run(self, run_id: str) -> None:
        """Keep only events belonging to this run_id in history."""
        self._history = deque(
            (e for e in self._history if e.get("run_id") == run_id),
            maxlen=_HISTORY_MAXLEN,
        )


broadcaster = Broadcaster()


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="friedegg dashboard", version="0.1.0")


@app.websocket("/ws/ingest")
async def ws_ingest(ws: WebSocket) -> None:
    """Receive events from a user's automation script."""
    await ws.accept()
    try:
        while True:
            raw = await ws.receive_text()
            try:
                event = json.loads(raw)
            except json.JSONDecodeError:
                _LOGGER.warning("Ingest received invalid JSON: %r", raw[:200])
                continue

            # If this is a new workflow start, reset history to just this run.
            if event.get("event_type") == "workflow_start":
                run_id = event.get("run_id")
                if run_id:
                    broadcaster.clear_history_for_new_run(run_id)

            await broadcaster.publish(event)
    except WebSocketDisconnect:
        return
    except Exception as exc:
        _LOGGER.exception("Ingest error: %s", exc)


@app.websocket("/ws/dashboard")
async def ws_dashboard(ws: WebSocket) -> None:
    """Push events to a connected dashboard browser."""
    await broadcaster.connect_dashboard(ws)
    try:
        while True:
            # We don't expect messages from the dashboard for Phase 1,
            # but we need to keep the connection alive and handle disconnect.
            await ws.receive_text()
    except WebSocketDisconnect:
        broadcaster.disconnect_dashboard(ws)
    except Exception as exc:
        _LOGGER.exception("Dashboard connection error: %s", exc)
        broadcaster.disconnect_dashboard(ws)


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(_DASHBOARD_DIR / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "friedegg"}


# Mount static files last so it doesn't swallow the routes above.
if _DASHBOARD_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(_DASHBOARD_DIR)),
        name="static",
    )
