import json
import time

import pytest

from friedegg._client import _Monitor, Event

_DEAD_URL = "ws://127.0.0.1:19999/ws/ingest"  # nothing listening here


class TestEvent:
    def test_serializes_to_valid_json(self):
        e = Event(
            event_type="step",
            run_id="r1",
            workflow_name="W",
            step_name="S",
            status="running",
        )
        data = json.loads(e.to_json())
        assert data["event_type"] == "step"
        assert data["step_name"] == "S"
        assert data["status"] == "running"

    def test_timestamp_ends_with_z(self):
        e = Event(event_type="workflow_start", run_id="r1", workflow_name="W")
        assert json.loads(e.to_json())["timestamp"].endswith("Z")

    def test_default_metadata_is_empty_dict(self):
        e = Event(event_type="step", run_id="r1", workflow_name="W")
        assert json.loads(e.to_json())["metadata"] == {}


class TestMonitor:
    def fresh(self) -> _Monitor:
        return _Monitor()

    def test_start_returns_uuid_string(self):
        m = self.fresh()
        run_id = m.start("W", ws_url=_DEAD_URL)
        assert isinstance(run_id, str)
        assert len(run_id) == 36  # UUID4 with hyphens
        m.done()

    def test_step_before_start_raises(self):
        with pytest.raises(RuntimeError, match="monitor.start()"):
            self.fresh().step("S")

    def test_done_before_start_raises(self):
        with pytest.raises(RuntimeError, match="monitor.start()"):
            self.fresh().done()

    def test_error_before_start_raises(self):
        with pytest.raises(RuntimeError, match="monitor.start()"):
            self.fresh().error("oops")

    def test_state_resets_after_done(self):
        m = self.fresh()
        m.start("W", ws_url=_DEAD_URL)
        m.done()
        assert m._run_id is None
        assert m._last_step_name is None
        assert m._step_start is None

    def test_can_start_new_workflow_after_done(self):
        m = self.fresh()
        id1 = m.start("W1", ws_url=_DEAD_URL)
        m.done()
        id2 = m.start("W2", ws_url=_DEAD_URL)
        m.done()
        assert id1 != id2

    def test_silent_fail_when_server_unreachable(self):
        m = self.fresh()
        m.start("W", ws_url=_DEAD_URL)
        time.sleep(0.15)  # let sender thread attempt and fail
        m.step("Step 1")
        m.step("Step 2")
        m.done()  # must not raise
