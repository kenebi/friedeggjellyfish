# Fried Egg Jellyfish (FEJ) — Roadmap
*Created: April 14, 2026*
*Agent: Claude (CLD)*

---

## Phase 1: MVP — Core Library + Local Dashboard
**Goal:** Ship a working, installable tool that people can actually use.
**Timeline:** Target 2-3 sessions

### 1.1 Python Library (`friedegg`)
- [ ] Package structure (`friedegg/` with `__init__.py`, `monitor.py`, `server.py`, `cli.py`)
- [ ] Core API: `monitor.start()`, `.step()`, `.error()`, `.done()`
- [ ] WebSocket client that sends status events to local server
- [ ] Auto-timestamps on each step
- [ ] Error capture with traceback formatting
- [ ] CLI entry point: `friedegg dashboard`
- [ ] `setup.py` / `pyproject.toml` for PyPI packaging

### 1.2 Local Dashboard Server
- [ ] FastAPI or Flask local server
- [ ] WebSocket endpoint to receive status updates
- [ ] Serve static HTML dashboard
- [ ] Store run history in memory (current session only)
- [ ] Auto-open browser when dashboard starts

### 1.3 Dashboard UI
- [ ] Real-time flowchart visualization (HTML/CSS/JS)
- [ ] Node states: pending (gray), running (amber/gold), done (green), error (red)
- [ ] Animated transitions between states
- [ ] Plain-English error display panel
- [ ] Step timing display (how long each step took)
- [ ] Jellyfish-themed design (golden center, tentacle-like flow lines)

### 1.4 Documentation & Release
- [ ] README.md with quick start guide
- [ ] Usage examples (3 common automation scenarios)
- [ ] Publish to GitHub (public repo, MIT license)
- [ ] Publish to PyPI
- [ ] GitHub Pages documentation site

---

## Phase 2: Polish + Community
**Goal:** Make it delightful and easy to contribute to.

- [ ] Dark mode dashboard
- [ ] Export flow diagram as PNG/SVG
- [ ] Run history (persist past runs, view previous automation results)
- [ ] Suggested fixes for common errors (auth failures, timeouts, API rate limits)
- [ ] CONTRIBUTING.md for open source contributors
- [ ] Logo and brand assets finalized
- [ ] Community launch (Reddit r/automation, r/python, Twitter/X, LinkedIn)
- [ ] Demo video / GIF showing FEJ in action

---

## Phase 3: Expand
**Goal:** Grow adoption and add power features.

- [ ] JavaScript/Node.js library (`npm install friedegg`)
- [ ] Multiple concurrent workflow monitoring
- [ ] Dashboard notifications (desktop notifications on errors)
- [ ] Webhook support (send alerts to Slack/email on failure)
- [ ] Optional cloud dashboard (hosted version, freemium model)
- [ ] AI-powered error analysis (Claude API integration for smart error explanations)

---

## Phase 4: Ecosystem
**Goal:** Become the standard monitoring layer for code-built automations.

- [ ] Integration plugins for n8n, Make.com (output FEJ-compatible logs)
- [ ] Team/multi-user dashboard
- [ ] Mobile-friendly responsive dashboard
- [ ] API for third-party integrations
- [ ] CLI commands: `friedegg replay`, `friedegg export`, `friedegg share`

---

*Focus is Phase 1 only. Ship MVP, get feedback, iterate.*
