# Examples

All examples are runnable scripts. Start the dashboard first, then run the script.

```
friedeggjellyfish dashboard
```

---

## Daily Lead Report

Simulates a CRM automation that pulls leads, scores them against analytics data, and sends a summary email. Demonstrates `warn()` — the GA4 step returns partial data, which is flagged as a non-fatal warning.

**Source:** [`examples/example_lead_report.py`](https://github.com/kenebi/friedeggjellyfish/blob/main/examples/example_lead_report.py)

```python
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
```

**What to watch for:** The "Query Google Analytics" step turns burnt orange after the warning. The workflow still completes — the final pill reads **Done with warnings**.

---

## Payment Sync with Error

Simulates a Stripe-to-database sync where one record fails validation. Demonstrates `error()` — the exception is caught, reported to the dashboard, and the workflow continues and finishes cleanly.

**Source:** [`examples/example_payment_sync.py`](https://github.com/kenebi/friedeggjellyfish/blob/main/examples/example_payment_sync.py)

```python
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
```

**What to watch for:** The "Validate records" step turns red after the error. The workflow continues — "Write to database" and "Send summary report" still run. The final pill reads **Done with errors**.

---

## Gmail Inbox Cleanup

Simulates an automation that authenticates with Gmail, finds old unread emails, and archives them in batches. Every step completes successfully — this is a clean run showing the fully-completed (gold) state.

**Source:** [`examples/example_gmail_cleanup.py`](https://github.com/kenebi/friedeggjellyfish/blob/main/examples/example_gmail_cleanup.py)

```python
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
```

**What to watch for:** All five steps turn gold as they complete. The final pill reads **Done** with no warnings or errors.

---

## Google Sheets Data Pipeline

Simulates reading raw contact data from a Google Sheet, validating and enriching it, then writing clean results to an output tab. One step flags rows with missing fields as a non-fatal warning.

**Source:** [`examples/example_sheets_pipeline.py`](https://github.com/kenebi/friedeggjellyfish/blob/main/examples/example_sheets_pipeline.py)

```python
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
```

**What to watch for:** The "Validate rows" step turns burnt orange after the warning. The pipeline keeps running and completes. The final pill reads **Done with warnings**.

---

## Competitor Price Monitor

Simulates a web scraping automation that checks competitor pricing across multiple sites. One site returns an unexpected page structure — the error is caught and reported, and the workflow continues to completion.

**Source:** [`examples/example_web_scraper.py`](https://github.com/kenebi/friedeggjellyfish/blob/main/examples/example_web_scraper.py)

```python
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
```

**What to watch for:** The "Scrape site B" step turns red after the error. Price parsing and CSV export still run. The final pill reads **Done with errors**.
