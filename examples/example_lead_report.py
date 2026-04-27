"""
Example: Daily Lead Report

Simulates a multi-step automation that pulls leads from a CRM,
scores them against analytics data, and sends a summary email.

Demonstrates: monitor.start(), .step(), .warn(), .done()

Before running:
  1. In a separate terminal, run: friedeggjellyfish dashboard
  2. The browser opens at http://127.0.0.1:8765
  3. Run this file: python examples/example_lead_report.py
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

print("Done. Check the dashboard.")
time.sleep(0.5)
