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

    def test_warn_before_start_raises(self):
        with pytest.raises(RuntimeError, match="monitor.start()"):
            self.fresh().warn("oops")

    def test_state_resets_after_done(self):
        m = self.fresh()
        m.start("W", ws_url=_DEAD_URL)
        m.done()
        assert m._run_id is None
        assert m._last_step_name is None
        assert m._step_start is None
        assert m._sender is None

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


class TestStepDescription:
    def fresh(self) -> _Monitor:
        return _Monitor()

    def _capture(self, m):
        """Replace m._sender.send with a capture list."""
        sent = []
        m._sender.send = lambda e: sent.append(e)
        return sent

    def test_step_description_in_metadata(self):
        m = self.fresh()
        m.start("W", ws_url=_DEAD_URL)
        time.sleep(0.15)
        sent = self._capture(m)

        m.step("S1", description="Fetching data")

        step_ev = next((e for e in sent if e.event_type == "step"), None)
        assert step_ev is not None
        assert step_ev.metadata.get("description") == "Fetching data"
        m.done()

    def test_step_description_merged_with_metadata(self):
        m = self.fresh()
        m.start("W", ws_url=_DEAD_URL)
        time.sleep(0.15)
        sent = self._capture(m)

        m.step("S1", description="desc", metadata={"extra": 42})

        step_ev = next((e for e in sent if e.event_type == "step"), None)
        assert step_ev.metadata["description"] == "desc"
        assert step_ev.metadata["extra"] == 42
        m.done()

    def test_step_no_description_is_empty_metadata(self):
        m = self.fresh()
        m.start("W", ws_url=_DEAD_URL)
        time.sleep(0.15)
        sent = self._capture(m)

        m.step("S1")

        step_ev = next((e for e in sent if e.event_type == "step"), None)
        assert "description" not in step_ev.metadata
        m.done()

    def test_step_default_status_is_running(self):
        m = self.fresh()
        m.start("W", ws_url=_DEAD_URL)
        time.sleep(0.15)
        sent = self._capture(m)

        m.step("S1")

        step_ev = next((e for e in sent if e.event_type == "step"), None)
        assert step_ev.status == "running"
        m.done()


class TestWarn:
    def fresh(self) -> _Monitor:
        return _Monitor()

    def _capture(self, m):
        sent = []
        m._sender.send = lambda e: sent.append(e)
        return sent

    def test_warn_emits_warn_event(self):
        m = self.fresh()
        m.start("W", ws_url=_DEAD_URL)
        time.sleep(0.15)
        sent = self._capture(m)

        m.warn("low disk space", details="only 2GB free")

        warn_ev = next((e for e in sent if e.event_type == "warn"), None)
        assert warn_ev is not None
        assert warn_ev.status == "warn"
        assert warn_ev.error_message == "low disk space"
        assert warn_ev.error_traceback == "only 2GB free"
        m.done()

    def test_warn_attaches_to_current_step(self):
        m = self.fresh()
        m.start("W", ws_url=_DEAD_URL)
        time.sleep(0.15)
        m.step("S1")
        sent = self._capture(m)

        m.warn("soft issue")

        warn_ev = next(e for e in sent if e.event_type == "warn")
        assert warn_ev.step_name == "S1"
        m.done()

    def test_warn_does_not_terminate_workflow(self):
        m = self.fresh()
        m.start("W", ws_url=_DEAD_URL)
        time.sleep(0.15)
        m.step("S1")
        m.warn("soft issue")
        m.step("S2")   # must not raise
        m.done()       # must not raise

    def test_warn_followed_by_done_does_not_raise(self):
        m = self.fresh()
        m.start("W", ws_url=_DEAD_URL)
        time.sleep(0.15)
        m.warn("direct warn without prior step")
        m.done()


class TestAtexit:
    def fresh(self) -> _Monitor:
        return _Monitor()

    def _capture(self, m):
        sent = []
        m._sender.send = lambda e: sent.append(e)
        return sent

    def test_atexit_does_nothing_after_done(self):
        m = self.fresh()
        m.start("W", ws_url=_DEAD_URL)
        m.done()
        assert m._run_id is None
        # Atexit guard: run_id is None so finalize is a no-op.
        m._atexit_finalize()  # must not raise

    def test_atexit_sends_error_step_and_workflow_done(self):
        m = self.fresh()
        m.start("W", ws_url=_DEAD_URL)
        time.sleep(0.15)
        m.step("S1")
        sent = self._capture(m)

        m._atexit_finalize()

        types = [e.event_type for e in sent]
        assert "step" in types
        assert "workflow_done" in types

        step_ev = next(e for e in sent if e.event_type == "step")
        assert step_ev.status == "error"
        assert step_ev.step_name == "S1"
        assert "crashed" in step_ev.error_message.lower()

    def test_atexit_clears_run_id_to_prevent_double_fire(self):
        m = self.fresh()
        m.start("W", ws_url=_DEAD_URL)
        time.sleep(0.15)
        self._capture(m)

        m._atexit_finalize()
        assert m._run_id is None

        # Second call must be a no-op.
        m._atexit_finalize()  # must not raise

    def test_atexit_without_any_step_sends_only_workflow_done(self):
        m = self.fresh()
        m.start("W", ws_url=_DEAD_URL)
        time.sleep(0.15)
        sent = self._capture(m)

        m._atexit_finalize()

        types = [e.event_type for e in sent]
        assert "workflow_done" in types
        # No step event because no step was started.
        assert "step" not in types
