"""
Smoke test for FEJ — simulates a typical multi-step automation.

Exercises Phase 1.2 features:
  - step() description parameter
  - monitor.warn() (soft warning, workflow continues)
  - All four jellyfish states visible in the timeline

Before running:
  1. In a separate terminal with (.venv) active, run: friedeggjellyfish dashboard
  2. The browser should open at http://127.0.0.1:8765
  3. Then run this file: python examples/smoke_test.py
"""

import time
from friedeggjellyfish import monitor

monitor.start(
    "Daily Lead Report",
    description="Pull leads from CRM and send summary email",
)

monitor.step("Connect to HubSpot API", description="Authenticating with API token")
time.sleep(0.8)

monitor.step("Pull new leads", description="Fetching contacts updated in last 24h")
time.sleep(1.2)

monitor.step("Query Google Analytics", description="Session data for lead scoring")
time.sleep(0.4)
monitor.warn("GA4 property returned partial data — some date ranges excluded")
time.sleep(0.4)

monitor.step("Generate summary", description="Aggregate stats and highlight hot leads")
time.sleep(0.9)

monitor.step("Send email", description="Dispatch report to kenneth@example.com")
time.sleep(0.7)

monitor.done()

print("Smoke test complete. Check the dashboard.")
# Give the background sender a moment to flush before the script exits.
time.sleep(0.5)
