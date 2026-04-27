"""
Example: Gmail Inbox Cleanup

Simulates an automation that connects to Gmail, finds old unread emails,
and archives them in batches. All steps complete successfully — this is
a clean run showing the fully-completed (gold) state.

Demonstrates: monitor.start(), .step(), .done()

Before running:
  1. In a separate terminal, run: friedeggjellyfish dashboard
  2. The browser opens at http://127.0.0.1:8765
  3. Run this file: python examples/example_gmail_cleanup.py
"""

import time
from friedeggjellyfish import monitor

monitor.start(
    "Gmail Inbox Cleanup",
    description="Archive unread emails older than 30 days",
)

monitor.step("Authenticate with Gmail API", description="Loading OAuth credentials")
time.sleep(0.5)

monitor.step("Fetch candidate emails", description="Searching for unread messages > 30 days old")
time.sleep(1.1)

monitor.step("Filter by label", description="Excluding starred and important labels")
time.sleep(0.6)

monitor.step("Archive messages", description="Moving 47 emails to archive")
time.sleep(1.4)

monitor.step("Generate report", description="Summarising what was cleaned up")
time.sleep(0.5)

monitor.done()

print("Done. Check the dashboard.")
time.sleep(0.5)
