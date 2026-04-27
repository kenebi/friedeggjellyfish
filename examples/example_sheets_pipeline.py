"""
Example: Google Sheets Data Pipeline

Simulates an automation that reads raw contact data from a Google Sheet,
validates and enriches it, then writes clean results to an output tab.
One step triggers a warning due to rows with missing fields.

Demonstrates: monitor.start(), .step(), .warn(), .done()

Before running:
  1. In a separate terminal, run: friedeggjellyfish dashboard
  2. The browser opens at http://127.0.0.1:8765
  3. Run this file: python examples/example_sheets_pipeline.py
"""

import time
from friedeggjellyfish import monitor

monitor.start(
    "Sheets Data Pipeline",
    description="Validate and enrich contact data from Google Sheets",
)

monitor.step("Connect to Google Sheets API", description="Authenticating with service account")
time.sleep(0.6)

monitor.step("Read raw data", description="Loading 312 rows from 'Contacts' tab")
time.sleep(0.9)

monitor.step("Validate rows", description="Checking for required fields")
time.sleep(0.5)
monitor.warn("14 rows skipped — missing 'email' field")
time.sleep(0.3)

monitor.step("Enrich with company data", description="Matching domains to Clearbit profiles")
time.sleep(1.3)

monitor.step("Write to output sheet", description="Writing 298 clean rows to 'Enriched' tab")
time.sleep(0.7)

monitor.step("Send summary email", description="Notifying team of pipeline results")
time.sleep(0.5)

monitor.done()

print("Done. Check the dashboard.")
time.sleep(0.5)
