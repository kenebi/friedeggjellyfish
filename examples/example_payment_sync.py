"""
Example: Payment Sync with Error

Simulates a multi-step automation that syncs Stripe payment records
to a database. One step raises a real exception to demonstrate how
FEJ captures errors and marks the workflow "DONE WITH ERRORS".

Demonstrates: monitor.start(), .step(), .error(), .done()

Before running:
  1. In a separate terminal, run: friedeggjellyfish dashboard
  2. The browser opens at http://127.0.0.1:8765
  3. Run this file: python examples/example_payment_sync.py
"""

import time
from friedeggjellyfish import monitor

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
    monitor.error(str(e))
time.sleep(0.3)

monitor.step("Write to database", description="Upserting valid records")
time.sleep(0.9)

monitor.step("Send summary report", description="Email digest to finance@example.com")
time.sleep(0.5)

monitor.done()

print("Done. Check the dashboard for the error state.")
time.sleep(0.5)
