"""
Error-state smoke test for FEJ.

Verifies the red error UI: one step raises a real exception, monitor.error()
captures the traceback automatically, and the workflow completes with
"DONE WITH ERRORS".

Before running:
  1. In a separate terminal with (.venv) active: friedegg dashboard
  2. Then run this file: python examples/error_smoke_test.py
"""

import time
from friedegg import monitor

monitor.start(
    "Payment Sync",
    description="Sync payment records from Stripe to database",
)

monitor.step("Connect to Stripe", description="Authenticating with API key")
time.sleep(0.6)

monitor.step("Fetch transactions", description="Pulling last 24h of charges")
time.sleep(0.8)

monitor.step("Validate records", description="Checking for duplicates and missing fields")
time.sleep(0.5)
try:
    raise ValueError("Record #TXN-4821 is missing required field 'currency'")
except ValueError as e:
    # details= is omitted so monitor.error() auto-captures the traceback.
    monitor.error(str(e))
time.sleep(0.3)

monitor.step("Write to database", description="Upserting valid records")
time.sleep(0.9)

monitor.step("Send summary report", description="Email digest to finance@example.com")
time.sleep(0.5)

monitor.done()

print("Error smoke test complete. Check the dashboard for the red error state.")
time.sleep(0.5)
