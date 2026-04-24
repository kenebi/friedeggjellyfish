"""
friedegg._client — Client-side monitoring API.

This module is imported by the user's automation script. It sends status
events to the local FEJ dashboard server over WebSocket. If the dashboard
isn't running, events are silently dropped so the automation still works.

Example:
    from friedegg import monitor

    monitor.start("Daily lead report")
    monitor.step("Connect to HubSpot")
    monitor.step("Pull new leads")
    monitor.done()
"""

from __future__ import annotations

import json
import logging
import queue
import threading
import time
import traceback
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

try:
    from websockets.sync.client import connect
    from websockets.exceptions import WebSocketException
except ImportError:  # pragma: no cover
    connect = None  # type: ignore
    WebSocketException = Exception  # type: ignore

_LOGGER = logging.getLogger("friedegg")

# Default local dashboard endpoint.
DEFAULT_WS_URL = "ws://127.0.0.1:8765/ws/ingest"


# ---------------------------------------------------------------------------
# Event data model
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    """UTC timestamp in ISO-8601 format with trailing Z."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


@dataclass
class Event:
    """Single status event sent to the dashboard."""
    event_type: str                 # "workflow_start" | "step" | "error" | "workflow_done"
    run_id: str                     # UUID for this workflow run
    workflow_name: str
    timestamp: str = field(default_factory=_now_iso)
    step_name: str | None = None
    status: str | None = None       # "pending" | "running" | "done" | "error"
    duration_ms: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    error_traceback: str | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self))


# ---------------------------------------------------------------------------
# Background sender thread
# ---------------------------------------------------------------------------

class _Sender:
    """
    Background thread that drains an event queue and pushes events to the
    dashboard over a persistent WebSocket connection.

    Runs as a daemon thread so it never blocks program exit.
    """

    def __init__(self, ws_url: str = DEFAULT_WS_URL) -> None:
        self.ws_url = ws_url
        self._queue: queue.Queue[Event | None] = queue.Queue()
        self._thread: threading.Thread | None = None
        self._connected = False
        self._warned_once = False

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(
            target=self._run,
            name="friedegg-sender",
            daemon=True,
        )
        self._thread.start()

    def send(self, event: Event) -> None:
        self._queue.put(event)

    def stop(self) -> None:
        """Signal the sender to drain and exit. Non-blocking."""
        self._queue.put(None)

    def _run(self) -> None:
        if connect is None:
            self._warn_disconnected("websockets library not installed")
            return

        try:
            with connect(self.ws_url, open_timeout=2) as ws:
                self._connected = True
                while True:
                    event = self._queue.get()
                    if event is None:  # shutdown sentinel
                        return
                    try:
                        ws.send(event.to_json())
                    except WebSocketException as exc:
                        self._warn_disconnected(f"send failed: {exc}")
                        return
        except (ConnectionRefusedError, OSError, WebSocketException) as exc:
            self._warn_disconnected(f"dashboard not reachable ({exc})")
            # Drain the queue so producers don't block forever.
            self._drain()

    def _drain(self) -> None:
        try:
            while True:
                self._queue.get_nowait()
        except queue.Empty:
            return

    def _warn_disconnected(self, reason: str) -> None:
        if not self._warned_once:
            _LOGGER.warning(
                "FEJ: %s. Automation will continue without monitoring. "
                "Run `friedegg dashboard` in another terminal to enable.",
                reason,
            )
            self._warned_once = True


# ---------------------------------------------------------------------------
# Public monitor API
# ---------------------------------------------------------------------------

class _Monitor:
    """
    The singleton monitor instance exposed as `friedegg.monitor`.

    Tracks a single active workflow run. Auto-timestamps steps and measures
    step durations.
    """

    def __init__(self) -> None:
        self._sender: _Sender | None = None
        self._run_id: str | None = None
        self._workflow_name: str | None = None
        self._step_start: float | None = None
        self._last_step_name: str | None = None

    # -- lifecycle --------------------------------------------------------

    def start(
        self,
        workflow_name: str,
        description: str | None = None,
        ws_url: str = DEFAULT_WS_URL,
    ) -> str:
        """Begin a new monitored workflow. Returns the run_id."""
        self._run_id = str(uuid.uuid4())
        self._workflow_name = workflow_name
        self._step_start = None
        self._last_step_name = None

        self._sender = _Sender(ws_url=ws_url)
        self._sender.start()

        self._sender.send(Event(
            event_type="workflow_start",
            run_id=self._run_id,
            workflow_name=workflow_name,
            metadata={"description": description} if description else {},
        ))
        return self._run_id

    def step(
        self,
        step_name: str,
        status: str = "done",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Mark a step in the workflow.

        If a previous step is still open, it is auto-finalized to "done"
        with its measured duration before the new step is emitted.
        """
        self._ensure_started()

        now = time.monotonic()

        # Auto-close the previous step before opening a new one.
        if self._last_step_name is not None and self._last_step_name != step_name:
            prev_duration_ms: float | None = None
            if self._step_start is not None:
                prev_duration_ms = (now - self._step_start) * 1000
            self._sender.send(Event(  # type: ignore[union-attr]
                event_type="step",
                run_id=self._run_id,  # type: ignore[arg-type]
                workflow_name=self._workflow_name,  # type: ignore[arg-type]
                step_name=self._last_step_name,
                status="done",
                duration_ms=prev_duration_ms,
            ))

        self._sender.send(Event(  # type: ignore[union-attr]
            event_type="step",
            run_id=self._run_id,  # type: ignore[arg-type]
            workflow_name=self._workflow_name,  # type: ignore[arg-type]
            step_name=step_name,
            status=status,
            duration_ms=None,
            metadata=metadata or {},
        ))

        self._step_start = now
        self._last_step_name = step_name

    def error(
        self,
        message: str,
        details: str | None = None,
        step_name: str | None = None,
    ) -> None:
        """Report an error. `details` may be a traceback string."""
        self._ensure_started()

        if details is None:
            details = traceback.format_exc()
            if details.strip() == "NoneType: None":
                details = None

        self._sender.send(Event(  # type: ignore[union-attr]
            event_type="error",
            run_id=self._run_id,  # type: ignore[arg-type]
            workflow_name=self._workflow_name,  # type: ignore[arg-type]
            step_name=step_name or self._last_step_name,
            status="error",
            error_message=message,
            error_traceback=details,
        ))

    def done(self) -> None:
        """Mark the workflow complete."""
        self._ensure_started()

        # Close the last step if it is still open.
        if self._last_step_name is not None:
            now = time.monotonic()
            last_duration_ms: float | None = None
            if self._step_start is not None:
                last_duration_ms = (now - self._step_start) * 1000
            self._sender.send(Event(  # type: ignore[union-attr]
                event_type="step",
                run_id=self._run_id,  # type: ignore[arg-type]
                workflow_name=self._workflow_name,  # type: ignore[arg-type]
                step_name=self._last_step_name,
                status="done",
                duration_ms=last_duration_ms,
            ))

        self._sender.send(Event(  # type: ignore[union-attr]
            event_type="workflow_done",
            run_id=self._run_id,  # type: ignore[arg-type]
            workflow_name=self._workflow_name,  # type: ignore[arg-type]
            status="done",
        ))
        self._sender.stop()  # type: ignore[union-attr]

        # Reset state for the next workflow
        self._run_id = None
        self._workflow_name = None
        self._step_start = None
        self._last_step_name = None

    # -- internals --------------------------------------------------------

    def _ensure_started(self) -> None:
        if self._run_id is None or self._sender is None:
            raise RuntimeError(
                "friedegg: monitor.start() must be called before step/error/done."
            )


# The singleton users interact with:
monitor = _Monitor()
