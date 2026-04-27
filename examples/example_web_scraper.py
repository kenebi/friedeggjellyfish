"""
Example: Competitor Price Monitor

Simulates a web scraping automation that checks competitor product pricing
across multiple sites. One site returns an unexpected page structure,
raising an error — the workflow catches it and continues to completion.

Demonstrates: monitor.start(), .step(), .error(), .done()

Before running:
  1. In a separate terminal, run: friedeggjellyfish dashboard
  2. The browser opens at http://127.0.0.1:8765
  3. Run this file: python examples/example_web_scraper.py
"""

import time
from friedeggjellyfish import monitor

monitor.start(
    "Competitor Price Monitor",
    description="Scrape and compare product pricing across competitor sites",
)

monitor.step("Initialize scraper", description="Loading selectors and rate-limit config")
time.sleep(0.4)

monitor.step("Scrape site A", description="Fetching 24 product listings")
time.sleep(1.0)

monitor.step("Scrape site B", description="Fetching 18 product listings")
time.sleep(0.5)
try:
    raise RuntimeError("Unexpected page structure — price selector returned 0 matches")
except RuntimeError as e:
    monitor.error(str(e))
time.sleep(0.3)

monitor.step("Parse and compare prices", description="Building price delta table")
time.sleep(0.9)

monitor.step("Save results to CSV", description="Writing report to output/prices.csv")
time.sleep(0.4)

monitor.done()

print("Done. Check the dashboard for the error state.")
time.sleep(0.5)
