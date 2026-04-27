# API Reference

## monitor

The `monitor` object is the singleton you import and use directly. There is no need to instantiate anything.

```python
from friedeggjellyfish import monitor
```

---

### `monitor.start()`

```python
monitor.start(workflow_name, description=None, ws_url="ws://127.0.0.1:8765/ws/ingest")
```

Begins a new monitored workflow run. Call this once at the top of your script.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `workflow_name` | `str` | required | Name shown in the dashboard header |
| `description` | `str \| None` | `None` | Optional subtitle shown under the name |
| `ws_url` | `str` | `ws://127.0.0.1:8765/ws/ingest` | Dashboard WebSocket URL |

**Returns:** `str` — the run ID (UUID4). You can ignore it.

---

### `monitor.step()`

```python
monitor.step(step_name, description=None, status="running", metadata=None)
```

Marks a step as starting. Call once per step as it begins. The previous step is automatically closed and timed.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `step_name` | `str` | required | Label shown on the dashboard node |
| `description` | `str \| None` | `None` | Optional subtitle shown under the step name |
| `status` | `str` | `"running"` | Initial status. Pass `"done"` to mark a step immediately complete (unusual) |
| `metadata` | `dict \| None` | `None` | Arbitrary key/value pairs attached to the event |

**Auto-timing:** `friedeggjellyfish` measures the wall-clock duration of each step and displays it under the node after the step completes.

---

### `monitor.warn()`

```python
monitor.warn(message, details=None, step_name=None)
```

Reports a non-fatal warning. The workflow continues normally. The affected step turns burnt orange on the dashboard.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | `str` | required | Plain-English description of the warning |
| `details` | `str \| None` | `None` | Extra context (shown in Run History) |
| `step_name` | `str \| None` | `None` | Which step to attach the warning to. Defaults to the last active step |

---

### `monitor.error()`

```python
monitor.error(message, details=None, step_name=None)
```

Reports an error. Informational only — `friedeggjellyfish` does not raise an exception or stop your script. The affected step turns red on the dashboard.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | `str` | required | Plain-English description of what failed |
| `details` | `str \| None` | `None` | Full traceback or extra context. If omitted, the current exception traceback is captured automatically |
| `step_name` | `str \| None` | `None` | Which step failed. Defaults to the last active step |

!!! tip
    Call `monitor.error()` inside your `except` block. The traceback is captured automatically if you leave `details=None`.

---

### `monitor.done()`

```python
monitor.done()
```

Marks the workflow complete. Always call this at the end of your script.

Closes any open step, emits a `workflow_done` event, and resets the monitor state. The dashboard pill transitions to **Done**, **Done with warnings**, or **Done with errors** depending on what was reported during the run.

---

## Dashboard CLI

```
friedeggjellyfish dashboard [OPTIONS]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--host` | `127.0.0.1` | Bind address |
| `--port` | `8765` | Port |
| `--no-browser` | off | Skip auto-opening the browser tab |
| `--log-level` | `warning` | Server log verbosity: `debug`, `info`, `warning`, `error`, `critical` |

---

## Silent fail behaviour

If the dashboard server is not running when `monitor.start()` is called, `friedeggjellyfish` logs a single warning to the Python logger and all subsequent calls (`step`, `warn`, `error`, `done`) become no-ops. **Your automation always continues.**

```
WARNING: FEJ: dashboard not reachable. Automation will continue without monitoring.
Run `friedeggjellyfish dashboard` in another terminal to enable.
```

---

## Crash recovery

If your script exits without calling `monitor.done()` (e.g. due to an unhandled exception), `friedeggjellyfish` registers an `atexit` handler that automatically:

1. Marks the last open step as errored
2. Emits a `workflow_done` event

This prevents the dashboard from sitting stuck at **Running** after a crash.
