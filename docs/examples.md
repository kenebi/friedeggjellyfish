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

!!! note "More examples coming in v0.2.0"
    Gmail inbox cleanup, Google Sheets pipeline, and web scraping examples are planned for the next release.
