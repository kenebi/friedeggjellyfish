import asyncio

import pytest
from starlette.testclient import TestClient

from friedegg.server import app, Broadcaster, broadcaster

_WORKFLOW_EVENT = {
    "event_type": "workflow_start",
    "run_id": "test-run-1",
    "workflow_name": "Test Workflow",
    "timestamp": "2026-01-01T00:00:00.000Z",
    "step_name": None,
    "status": None,
    "duration_ms": None,
    "metadata": {},
    "error_message": None,
    "error_traceback": None,
}


@pytest.fixture(autouse=True)
def reset_broadcaster():
    broadcaster._history.clear()
    broadcaster._dashboards.clear()
    yield
    broadcaster._history.clear()
    broadcaster._dashboards.clear()


class TestBroadcaster:
    def test_publish_adds_to_history(self):
        bc = Broadcaster()
        asyncio.run(bc.publish({"run_id": "r1", "event_type": "step"}))
        assert len(bc._history) == 1

    def test_clear_keeps_only_matching_run(self):
        bc = Broadcaster()
        asyncio.run(bc.publish({"run_id": "old"}))
        asyncio.run(bc.publish({"run_id": "new"}))
        bc.clear_history_for_new_run("new")
        assert len(bc._history) == 1
        assert list(bc._history)[0]["run_id"] == "new"

    def test_maxlen_not_exceeded(self):
        from friedegg.server import _HISTORY_MAXLEN
        bc = Broadcaster()
        for i in range(_HISTORY_MAXLEN + 10):
            asyncio.run(bc.publish({"run_id": str(i)}))
        assert len(bc._history) == _HISTORY_MAXLEN


class TestHTTP:
    def test_health_returns_ok(self):
        with TestClient(app) as client:
            r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_index_serves_html(self):
        with TestClient(app) as client:
            r = client.get("/")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]


class TestWebSocket:
    def test_ingest_broadcasts_to_dashboard(self):
        with TestClient(app) as client:
            with client.websocket_connect("/ws/dashboard") as dash:
                with client.websocket_connect("/ws/ingest") as ingest:
                    ingest.send_json(_WORKFLOW_EVENT)
                    received = dash.receive_json()
        assert received["run_id"] == "test-run-1"
        assert received["event_type"] == "workflow_start"

    def test_new_dashboard_replays_history(self):
        # Pre-populate history directly to avoid timing races.
        asyncio.run(broadcaster.publish(_WORKFLOW_EVENT))

        with TestClient(app) as client:
            with client.websocket_connect("/ws/dashboard") as dash:
                received = dash.receive_json()

        assert received["run_id"] == "test-run-1"

    def test_workflow_start_clears_previous_run_history(self):
        new_run_event = {**_WORKFLOW_EVENT, "run_id": "new-run"}

        with TestClient(app) as client:
            with client.websocket_connect("/ws/ingest") as ingest:
                ingest.send_json(_WORKFLOW_EVENT)   # old run
                ingest.send_json(new_run_event)     # new run clears old

            with client.websocket_connect("/ws/dashboard") as dash:
                received = dash.receive_json()

        assert received["run_id"] == "new-run"
