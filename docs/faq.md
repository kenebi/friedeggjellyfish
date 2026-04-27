# FAQ

## Does this send any data to external services?

No. Everything stays on your machine. The dashboard communicates over a local WebSocket (`ws://127.0.0.1:8765`) — no internet connection required, no telemetry, no accounts.

---

## What if I forget to run the dashboard before my script?

Nothing breaks. `friedeggjellyfish` logs a single warning and your automation continues normally:

```
WARNING: FEJ: dashboard not reachable. Automation will continue without monitoring.
```

This is by design — monitoring should never be a dependency of your automation.

---

## Can I monitor multiple workflows at once?

Not in v0.1.x. The `monitor` object is a singleton that tracks one active run at a time. Multiple concurrent workflows will be supported in a future release.

---

## What Python version do I need?

Python 3.10 or higher.

---

## Can I use this with async code?

The `monitor` API is synchronous (blocking calls are in the microsecond range). You can call it from async code without issues — just call it normally. The background sender thread handles the WebSocket communication without blocking your event loop.

---

## What happens if my script crashes without calling `monitor.done()`?

`friedeggjellyfish` registers an `atexit` handler when `monitor.start()` is called. If your script exits unexpectedly, the handler automatically:

1. Marks the last open step as errored with the message *"Workflow ended without monitor.done() — script may have crashed."*
2. Emits a `workflow_done` event so the dashboard doesn't sit stuck at **Running**

---

## Can I run the dashboard on a different port?

Yes:

```
friedeggjellyfish dashboard --port 9000
```

Then point your script at the new URL:

```python
monitor.start("My workflow", ws_url="ws://127.0.0.1:9000/ws/ingest")
```

---

## Is there a way to persist run history across dashboard restarts?

Not yet. History is in-memory only and resets when the dashboard restarts. Persisted run history is planned for a future release.
