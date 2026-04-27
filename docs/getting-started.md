# Getting Started

## Prerequisites

- Python 3.10 or higher
- A terminal you can split into two panes (or two terminal windows)

---

## 1. Install

```
pip install friedeggjellyfish
```

---

## 2. Add monitoring to your script

Import `monitor` and wrap your automation steps:

```python
from friedeggjellyfish import monitor

monitor.start("My Automation")        # name shown in the dashboard

monitor.step("Connect to API")        # call once per step, as it begins
monitor.step("Pull data")
monitor.step("Process records")
monitor.step("Send report")

monitor.done()                        # always call this at the end
```

That's the entire API for a basic run. Each `step()` call auto-times itself and closes the previous step.

---

## 3. Launch the dashboard

In a **separate terminal**, run:

```
friedeggjellyfish dashboard
```

Your browser opens automatically at `http://127.0.0.1:8765`. Leave this terminal running.

---

## 4. Run your script

In your original terminal, run your script as normal:

```
python my_automation.py
```

Switch to the browser. Each step appears on the dashboard as it runs.

---

## What you'll see

- A jellyfish node lights up for each step
- The current step name appears at the top of the workflow card
- Duration is shown under each node after it completes
- The pill in the top-right transitions from **Running** → **Done** when the workflow finishes

---

## Adding warnings and errors

```python
# Non-fatal warning — workflow continues
monitor.warn("GA4 returned partial data", details="Date range 2026-01-01 excluded")

# Error — informational only, your script controls flow
try:
    sync_database()
except Exception as e:
    monitor.error("Database sync failed", details=str(e))
```

The dashboard marks the affected step in orange (warn) or red (error), and shows the message in the Run History panel.

---

## Silent fail

If the dashboard isn't running when your script starts, `friedeggjellyfish` logs a single warning and your automation continues normally. Nothing breaks — monitoring is always optional.

---

## Next steps

- [API Reference](api-reference.md) — full method signatures and CLI flags
- [Examples](examples.md) — complete scripts you can run right now
