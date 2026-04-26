"""
Fried Egg Jellyfish — Real-time visual monitoring for code-built automations.

Basic usage:

    from friedeggjellyfish import monitor

    monitor.start("My workflow")
    monitor.step("Connect to API")
    monitor.step("Pull data")
    monitor.done()

Run the dashboard in a separate terminal:

    friedeggjellyfish dashboard
"""

from friedeggjellyfish._client import monitor

__version__ = "0.1.0"
__all__ = ["monitor"]
