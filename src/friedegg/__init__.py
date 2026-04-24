"""
Fried Egg Jellyfish (FEJ) — Real-time visual monitoring for code-built automations.

Basic usage:

    from friedegg import monitor

    monitor.start("My workflow")
    monitor.step("Connect to API")
    monitor.step("Pull data")
    monitor.done()

Run the dashboard in a separate terminal:

    friedegg dashboard
"""

from friedegg._client import monitor

__version__ = "0.1.0"
__all__ = ["monitor"]
