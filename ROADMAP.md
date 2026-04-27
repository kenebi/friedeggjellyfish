# friedeggjellyfish — Roadmap

## Shipped — v0.1.0 (April 2026)

- Python library with four-method API: `monitor.start()`, `.step()`, `.warn()`, `.error()`, `.done()`
- Local FastAPI WebSocket server (`friedeggjellyfish dashboard`)
- Real-time browser dashboard with step-by-step flowchart
- Status states: pending, running, completed, warning, error
- Auto-timing per step, in-memory run history, dark mode
- Silent-fail when dashboard isn't running (your script keeps going)
- Plain-English error/warning display with copy-to-clipboard
- Published on PyPI: `pip install friedeggjellyfish`
- 41 passing tests

## Next — v0.2 (planned)

- Smooth step-transition animation polish
- GitHub Actions CI on every push
- Documentation site (GitHub Pages)
- More usage examples (Gmail, HubSpot, Google Sheets, scraping)
- Error pattern library — common error → suggested fix mapping

## Later

- Persisted run history across dashboard restarts
- Export run as PNG / SVG / JSON
- Multiple concurrent workflow tracking
- JavaScript / Node.js client
- Desktop or webhook notifications on error
- Optional hosted dashboard

---

Contributions welcome. Open an issue or PR on [GitHub](https://github.com/kenebi/friedeggjellyfish).
