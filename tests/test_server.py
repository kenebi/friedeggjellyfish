import asyncio

import pytest
from starlette.testclient import TestClient

from friedeggjellyfish.server import app, Broadcaster, broadcaster

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
    broadcaster._runs.clear()
    yield
    broadcaster._history.clear()
    broadcaster._dashboards.clear()
    broadcaster._runs.clear()


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
        from friedeggjellyfish.server import _HISTORY_MAXLEN
        bc = Broadcaster()
        for i in range(_HISTORY_MAXLEN + 10):
            asyncio.run(bc.publish({"run_id": str(i)}))
        assert len(bc._history) == _HISTORY_MAXLEN


class TestBroadcasterAggregateState:
    def _bc_with_start(self, run_id="r1"):
        bc = Broadcaster()
        asyncio.run(bc.publish({
            "run_id": run_id,
            "event_type": "workflow_start",
            "workflow_name": "W",
        }))
        return bc

    def test_workflow_start_initializes_run_state(self):
        bc = self._bc_with_start()
        assert "r1" in bc._runs
        assert bc._runs["r1"].has_errors is False
        assert bc._runs["r1"].has_warnings is False

    def test_error_event_sets_has_errors(self):
        bc = self._bc_with_start()
        asyncio.run(bc.publish({"run_id": "r1", "event_type": "error"}))
        assert bc._runs["r1"].has_errors is True
        assert bc._runs["r1"].has_warnings is False

    def test_warn_event_sets_has_warnings(self):
        bc = self._bc_with_start()
        asyncio.run(bc.publish({"run_id": "r1", "event_type": "warn"}))
        assert bc._runs["r1"].has_warnings is True
        assert bc._runs["r1"].has_errors is False

    def test_clean_run_gets_done_final_status(self):
        bc = self._bc_with_start()
        asyncio.run(bc.publish({"run_id": "r1", "event_type": "workflow_done"}))
        assert bc._runs["r1"].final_status == "done"

    def test_run_with_warnings_gets_done_with_warnings(self):
        bc = self._bc_with_start()
        asyncio.run(bc.publish({"run_id": "r1", "event_type": "warn"}))
        asyncio.run(bc.publish({"run_id": "r1", "event_type": "workflow_done"}))
        assert bc._runs["r1"].final_status == "done_with_warnings"

    def test_run_with_errors_gets_done_with_errors(self):
        bc = self._bc_with_start()
        asyncio.run(bc.publish({"run_id": "r1", "event_type": "error"}))
        asyncio.run(bc.publish({"run_id": "r1", "event_type": "workflow_done"}))
        assert bc._runs["r1"].final_status == "done_with_errors"

    def test_errors_take_priority_over_warnings(self):
        bc = self._bc_with_start()
        asyncio.run(bc.publish({"run_id": "r1", "event_type": "warn"}))
        asyncio.run(bc.publish({"run_id": "r1", "event_type": "error"}))
        asyncio.run(bc.publish({"run_id": "r1", "event_type": "workflow_done"}))
        assert bc._runs["r1"].final_status == "done_with_errors"

    def test_workflow_done_injects_final_status_into_history(self):
        bc = self._bc_with_start()
        asyncio.run(bc.publish({"run_id": "r1", "event_type": "error"}))
        asyncio.run(bc.publish({"run_id": "r1", "event_type": "workflow_done"}))
        last = list(bc._history)[-1]
        assert last.get("final_status") == "done_with_errors"

    def test_workflow_done_does_not_mutate_original_event_dict(self):
        bc = self._bc_with_start()
        original = {"run_id": "r1", "event_type": "workflow_done"}
        asyncio.run(bc.publish(original))
        # Original dict must not have been mutated.
        assert "final_status" not in original


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

    def test_workflow_done_broadcasts_with_final_status(self):
        done_event = {
            **_WORKFLOW_EVENT,
            "event_type": "workflow_done",
            "status": "done",
        }
        with TestClient(app) as client:
            with client.websocket_connect("/ws/dashboard") as dash:
                with client.websocket_connect("/ws/ingest") as ingest:
                    ingest.send_json(_WORKFLOW_EVENT)  # workflow_start
                    _ = dash.receive_json()
                    ingest.send_json(done_event)
                    received = dash.receive_json()
        assert received.get("final_status") == "done"
