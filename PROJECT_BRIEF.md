# Fried Egg Jellyfish (FEJ) — Project Brief
*Created: April 14, 2026*
*Agent: Claude (CLD)*
*Status: Planning / Pre-Build*

---

## Product Identity

**Name:** Fried Egg Jellyfish
**Short Name:** FEJ
**Package Name:** `friedegg`
**Install:** `pip install friedegg`
**Tagline:** "See your automations glow."
**License:** MIT (open source)
**Cost:** Free — $0 to build, $0 to host, $0 for users
**Mascot:** Fried Egg Jellyfish (Cotylorhiza tuberculata)

---

## What FEJ Is

A lightweight, open-source Python monitoring library + local web dashboard
that gives non-technical users real-time visual feedback on automations
built with AI coding tools like Claude Code, Cursor, Copilot, or any agent.

**The gap it fills:** When users build automations through AI coding agents,
the output is raw code with zero visual representation. Unlike n8n or
Make.com where you can see the flow visually, code-built automations are
invisible — you can't see what's happening, what succeeded, or what failed.
FEJ bridges this gap.

---

## What FEJ Is NOT

- NOT a code builder (Claude Code does that)
- NOT a prompt-to-visual tool (Anti-Gravity, Stitch do that)
- NOT an n8n/Make.com replacement (different purpose entirely)
- NOT a hosted SaaS product (runs locally, no cloud dependency)
- NOT limited to Claude Code (works with any automation code)

---

## Why This Metaphor

The Fried Egg Jellyfish (Cotylorhiza tuberculata):
- Has tentacles reaching in all directions → monitors multiple steps simultaneously
- Has symbiotic algae living inside it, providing energy → the library lives inside the code, feeding status back
- Its sting has virtually no effect on humans → lightweight, non-intrusive monitoring
- The golden center is visually stunning → memorable brand, beautiful dashboard
- It's unforgettable → nobody forgets this name

---

## Target Audience

**Primary:** Non-technical users (marketers, business owners, ops managers)
who use AI tools to build automations but can't read or debug code.

**Secondary:** Solo developers and freelancers who build automations for
clients and need a simple way to share "what the automation does" visually.

**Tertiary:** AI automation agencies who want to provide monitoring dashboards
to their clients.

---

## How It Works

### Step-by-step flow:

1. **User builds automation** — Uses Claude Code (or any AI agent) to create
   an automation script (e.g., "Pull leads from HubSpot, check GA activity,
   send daily summary email")

2. **User requests monitoring** — Tells Claude Code: "Add FEJ monitoring to
   this script" (or "Add Fried Egg Jellyfish monitoring")

3. **Claude Code adds hooks** — The AI agent adds `friedegg` library calls
   throughout the script:
   ```python
   from friedegg import monitor

   monitor.start("Daily Lead Report")
   monitor.step("Connect to HubSpot API")
   # ... HubSpot code ...
   monitor.step("Pull new leads")
   # ... pull leads code ...
   monitor.step("Query Google Analytics")
   # ... GA code ...
   monitor.step("Send summary email")
   # ... email code ...
   monitor.done()
   ```

4. **User launches dashboard** — Runs `friedegg dashboard` in terminal
   (or `python -m friedegg dashboard`). Opens a local web UI in their browser.

5. **Automation runs → dashboard lights up** — Each step appears as a node
   in a visual flowchart. Nodes glow gold/green when passing, red when failing.
   Errors show plain-English explanations with suggested fixes.

### Technical flow:
- The `friedegg` library sends status updates via WebSocket to a local server
- The local server (FastAPI or Flask) runs on localhost
- The dashboard (HTML/JS) connects via WebSocket for real-time updates
- All data stays local — nothing leaves the user's machine

---

## Architecture

```
User's Machine
├── Automation Script (Python)
│   ├── import friedegg
│   ├── monitor.start() ───────────┐
│   ├── monitor.step()  ───────────┤  WebSocket
│   ├── monitor.step()  ───────────┤  (localhost)
│   ├── monitor.error() ───────────┤
│   └── monitor.done()  ───────────┘
│                                  │
├── FEJ Local Server (localhost)   │
│   ├── Receives status updates ◄──┘
│   ├── Maintains flow state
│   └── Serves dashboard UI
│                                  
└── Browser Dashboard
    ├── Real-time flowchart
    ├── Step status (pending/running/done/error)
    ├── Error messages in plain English
    └── Suggested fixes
```

---

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Library | Python | Most common language for AI-generated automations |
| Local server | FastAPI or Flask | Lightweight, no heavy dependencies |
| Real-time | WebSocket | True real-time, not polling |
| Dashboard | HTML/CSS/JS (vanilla) | Zero framework dependencies, opens in any browser |
| Distribution | PyPI | `pip install friedegg` — standard Python package |
| Source | GitHub | Open source, community contributions |
| Docs | GitHub Pages | Free hosting, no cost |

---

## MVP Scope (Phase 1)

### Must have:
- [ ] Python library with simple API: `monitor.start()`, `.step()`, `.error()`, `.done()`
- [ ] Local web server launched via `friedegg dashboard` CLI command
- [ ] Real-time visual flowchart in browser showing step progression
- [ ] Status indicators: pending (gray), running (gold/amber), success (green), error (red)
- [ ] Plain-English error display
- [ ] Works with any Python automation script (agent-agnostic)
- [ ] MIT license, open source on GitHub
- [ ] Basic README with usage examples
- [ ] Published on PyPI

### Nice to have (Phase 1):
- [ ] Suggested fixes for common errors (API auth, timeout, etc.)
- [ ] Export flow diagram as image (PNG/SVG)
- [ ] Dark mode dashboard
- [ ] History of past runs

### Future (Phase 2+):
- [ ] Multi-language support (JavaScript/Node.js library)
- [ ] Cloud-hosted dashboard option (optional, freemium)
- [ ] Team sharing — multiple users viewing same dashboard
- [ ] AI-powered error analysis (use Claude API to explain errors)
- [ ] Integration with popular automation platforms (n8n, Make.com webhooks)
- [ ] Mobile-friendly dashboard
- [ ] Notification system (email/Slack when automation fails)

---

## API Design (Draft)

```python
from friedegg import monitor

# Start a new monitored workflow
monitor.start("Workflow Name", description="Optional description")

# Mark a step (auto-tracks timing)
monitor.step("Step Name")

# Log an error with context
monitor.error("Error description", details="Full error traceback")

# Mark workflow complete
monitor.done()

# Optional: add metadata to steps
monitor.step("Pull leads", metadata={"source": "HubSpot", "count": 47})

# Optional: manual status control
monitor.step("Process data", status="running")
monitor.step("Process data", status="done")
```

---

## Distribution & Hosting

| What | Where | Cost |
|------|-------|------|
| Python package | PyPI (`pip install friedegg`) | Free |
| Source code | GitHub (public repo) | Free |
| Documentation | GitHub Pages | Free |
| Dashboard | Runs locally (localhost) | Free |
| **Total** | | **$0** |

---

## Competitive Landscape

| Tool | What it does | FEJ's difference |
|------|-------------|-----------------|
| Claude Task Viewer | Dashboard for Claude Code sessions | Developer-focused, shows task status not automation flow |
| Claude Code Workflow Studio | VS Code extension for visual workflow design | Lives in VS Code, for developers, design-time not runtime |
| Nimbalyst | Desktop workspace for Claude Code | Session management + file editing, not automation monitoring |
| n8n / Make.com | Visual workflow builders | Build tools, not monitoring layers. FEJ monitors what they can't see |
| Prometheus / Grafana | Infrastructure monitoring | Enterprise, complex setup, not for non-technical users |

**FEJ's unique position:** The only tool specifically designed for non-technical
users to visually monitor code-built automations in real time.

---

## Permissions & Legal

- **Anthropic/Claude Code:** No permission needed. FEJ is just a Python package.
  Claude Code generates code that includes it, like any library.
- **Third-party APIs:** Not FEJ's concern. The user's automation connects to APIs,
  not FEJ. FEJ only reports step status.
- **Open source license:** MIT — permissive, community-friendly, allows commercial use.
- **Name conflicts:** "Fried Egg Jellyfish" has zero conflicts in the software space.
  `friedegg` is available on PyPI.
- **Existing "Monitor Lizard":** Rejected due to conflicts (monitor-lizard.com exists,
  GitHub repo exists). Documented for reference.
- **Existing "Komodo":** Rejected due to heavy conflicts (komo.do server management,
  Komodo Systems, Komodo IDE, KDE KomoDo).

---

## Strategic Value for AVI Lane

1. **Reputation builder** — Open source contributions build credibility in the
   AI automation space
2. **Portfolio piece** — Demonstrates deep understanding of the automation
   ecosystem gap between visual builders and code-based tools
3. **Community growth** — GitHub stars, contributors, and users = network
4. **Lead generation** — Users who find FEJ useful may need AVI Lane's
   consulting services for more complex automation work
5. **Skill demonstration** — Shows ability to identify market gaps, build
   products, and ship to production

---

## Project Structure

```
C:\Kenneth_AI\Businesses\AVI_Lane\03_Automations\FEJ\
├── PROJECT_BRIEF.md        ← This file
├── ROADMAP.md              ← Phased build plan
├── docs\                   ← Documentation drafts
├── src\                    ← Source code
│   └── friedegg\           ← Python package
├── design\                 ← Logo, dashboard mockups, brand assets
└── research\               ← Competitive analysis, user research
```

---

## Origin Story

FEJ was born from watching a YouTube video by Mikuel (AI agency owner) about
the n8n vs Claude Code debate. The video highlighted that the automation space
is evolving from visual workflow builders (Phase 2) to agentic workflows
(Phase 3). Kenneth identified a specific gap: when users build automations
through Claude Code, they lose the visual monitoring layer that n8n/Make.com
provide. FEJ fills that exact gap — it's the monitoring layer for the
agentic automation era.

Video: "The Future of AI Automation: N10 vs. Cloud Code" (April 14, 2026)

---

## Next Steps

1. Finalize API design and test edge cases
2. Create logo concept (fried egg jellyfish illustration)
3. Build MVP Python library (core monitoring functions)
4. Build local dashboard (HTML/JS with WebSocket)
5. Test with a real automation (e.g., HubSpot lead pull)
6. Publish to GitHub (public repo)
7. Publish to PyPI
8. Write documentation (GitHub Pages)
9. Share with community (Reddit, Twitter/X, dev forums)

---

*This project brief captures all decisions made during the initial
brainstorming session on April 14, 2026.*
