"""
Smoke test for FEJ — simulates a typical multi-step automation.

Before running:
  1. In a separate terminal with (.venv) active, run: friedegg dashboard
  2. The browser should open at http://127.0.0.1:8765
  3. Then run this file: python examples/smoke_test.py
"""

import time
from friedegg import monitor

monitor.start(
    "Daily Lead Report",
    description="Pull leads from CRM and send summary email",
)

monitor.step("Connect to HubSpot API", status="running")
time.sleep(0.8)

monitor.step("Pull new leads", status="running", metadata={"source": "HubSpot"})
time.sleep(1.2)

monitor.step("Query Google Analytics", status="running")
time.sleep(0.6)

monitor.step("Generate summary", status="running")
time.sleep(0.9)

monitor.step("Send email", status="running", metadata={"recipient": "kenneth@example.com"})
time.sleep(0.7)

monitor.done()

print("Smoke test complete. Check the dashboard.")
# Give the background sender a moment to flush before the script exits.
time.sleep(0.5)
