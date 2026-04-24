# FEJ — Project Context for Claude Code (CDE)
*Last updated: April 24, 2026*
*Primary agent: Claude Code (CDE)*
*Project path: `C:\Kenneth_AI\Businesses\AVI_Lane\03_Automations\FEJ\`*

---

## 🚨 Read First — Start Here

You are Claude Code (CDE) working on the **Fried Egg Jellyfish (FEJ)**
project. This file is your project-scoped context. Before doing anything:

1. Read this entire file
2. Read the active session log: `C:\Kenneth_AI\Session_Logs\AVI_Lane\FEJ_Project.md`
3. Confirm: "Context loaded for FEJ. Ready!"

If the session log shows the previous agent was CLD (Claude Desktop), you
are continuing their work — do not redo completed items.

---

## What FEJ Is

Fried Egg Jellyfish (FEJ) is an **open-source Python monitoring library**
that adds real-time visual flowchart monitoring to AI-generated automation
scripts. It addresses a specific gap: non-technical users who move from
visual automation tools (n8n, Make.com) to agentic coding tools (Claude
Code, etc.) lose the visual workflow view that made the original tools
approachable.

FEJ gives them that view back.

- **Package name on PyPI:** `friedegg`
- **Command on install:** `friedegg dashboard` (launches local WS server + browser UI)
- **User API:** `from friedegg import monitor` — `.start()`, `.step()`, `.error()`, `.done()`
- **License:** MIT
- **Owner:** Kenneth Ebilane (solo maintainer)
- **GitHub username:** `kenebi` (display name "Kenneth Ebilane")
- **Future repo URL:** `https://github.com/kenebi/friedegg`
- **Attribution:** "Built by Kenneth Ebilane / AVI Lane Digital" — but FEJ is
  NOT an AVI Lane sub-brand. See `design/BRAND.md` for brand separation rules.

---

## Current Status (as of April 24, 2026)

**Phase 1.1 complete and validated.** The package builds, installs with
`pip install -e .`, runs via `friedegg dashboard`, and a smoke test
(`examples/smoke_test.py`) successfully rendered a 5-step workflow end-to-end
in the browser on Kenneth's machine.

The architecture is proven:
```
user automation script (imports `monitor`)
    │
    │ WebSocket over ws://127.0.0.1:8765/ws/ingest
    ▼
FastAPI server (src/friedegg/server.py)
    │
    │ broadcasts to all connected browser clients
    ▼ ws://127.0.0.1:8765/ws/dashboard
dashboard UI (src/friedegg/dashboard/)
```

**What works:**
- `pyproject.toml` → installs via `pip install -e .`
- `friedegg` command registered → `friedegg dashboard` launches server + auto-opens browser
- WebSocket ingest path (automation → server)
- WebSocket dashboard broadcast path (server → browser)
- In-memory history replay (new dashboard tabs catch up on in-progress runs)
- Auto-timing between steps (durations measured correctly)
- Silent-fail when dashboard isn't running (automation continues)
- Smoke test renders "Daily Lead Report" with all 5 steps, correct durations, "DONE" pill

**What doesn't (known issues — see "Work Queue" below):**
- Step markers visually stay gold ("running") forever — they never transition to navy ("done")
- Naming collision smell: `src/friedegg/monitor.py` contains a singleton also named `monitor`, which caused the only bug we hit today

---

## Kenneth's Environment

- **OS:** Windows 11
- **Shell:** PowerShell 7+ (`pwsh`) — NEVER use bash/cmd syntax
- **Python:** 3.13.13 (installed fresh today at `C:\Users\ebila\AppData\Local\Programs\Python\Python313\`)
- **Git:** 2.54.0.windows.1 (installed today; default branch set to `main`, VS Code as editor)
- **Git identity:** `user.name = Kenneth Ebilane`, `user.email = ebilanekenneth@gmail.com`
- **Venv:** `FEJ\.venv\` (project root, not inside `src/`)
- **Virtualenv activation:** `.\.venv\Scripts\Activate.ps1`
- **Editor:** VS Code
- **Min Python support for users:** 3.10+ (see `pyproject.toml`)

### Dependencies already installed in `.venv`

From `pip list` today:

```
fastapi           0.136.1
uvicorn           0.46.0  (with [standard] extras: httptools, watchfiles, websockets)
websockets        16.0
pydantic          2.13.3
```

Plus the package itself is editable-installed: `pip install -e .`

---

## 🎯 Immediate Work Queue (pick up here)

These are the tasks Kenneth and CLD agreed on. Do them in this order
unless Kenneth directs otherwise. Each is small enough to verify with
a run between iterations — your iteration-loop strengths apply here.

### 1. Initialize git + `.gitignore`

- `git init` in FEJ root (will create `main` branch — already configured in global git config)
- Create `.gitignore` — must exclude: `.venv/`, `__pycache__/`, `*.egg-info/`,
  `dist/`, `build/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`,
  `*.pyc`, `.DS_Store`, `.vscode/`, `.idea/`
- First commit: "Initial commit — Phase 1.1 complete"

### 2. Create `LICENSE` (MIT)

Standard MIT with "Copyright (c) 2026 Kenneth Ebilane".

### 3. Write `README.md`

Quick-start (install + 5-line usage example), API reference for the four
`monitor.*` methods, link to the dashboard screenshot, credit/attribution.
Reference the logo at `design/AVILANE_FEJ_LOGO_20260423_CLD_v1.svg`.

### 4. Fix the "step done transition" bug

**The bug:** step markers pulse gold forever even after the workflow
completes. Auto-timing works (durations captured correctly), but no
"done" state ever fires for individual steps.

**The fix (recommended approach):** In `src/friedegg/monitor.py`, when
`_Monitor.step()` is called and `self._last_step_name` exists, emit a
second event flipping the previous step to `status="done"` BEFORE
emitting the new step's event. This matches FEJ's "auto-timing"
philosophy — the user shouldn't have to manually close out steps.

Also: `workflow_done` should walk any still-"running" step and mark
it "done" so the final step's marker transitions correctly.

Add this to the smoke test afterward to prove it: watch the browser
and confirm each marker turns navy before the next one starts pulsing.

### 5. Refactor `monitor.py` → `_client.py`

**Why:** the module and the singleton inside it are both named `monitor`,
which caused today's import bug. Rename the file to `_client.py` (the
underscore signals "internal module") and keep the singleton name
`monitor` in `__init__.py`. Users still write `from friedegg import monitor`.

After the rename, verify `examples/smoke_test.py` still works end-to-end.

### 6. Add pytest suite

- `tests/test_monitor.py` — `_Monitor` state transitions, `Event`
  serialization, silent-fail behavior when server is down
- `tests/test_server.py` — `Broadcaster` history behavior, ingest→broadcast
  round-trip with `httpx` WebSocket test client
- Install deps: `pip install -e ".[dev]"` (the `[dev]` extras in
  `pyproject.toml` already include pytest, pytest-asyncio, httpx)
- Target: pytest runs green on every commit going forward

### 7. Report back to Kenneth when #1–6 are done

Don't silently roll into Phase 1.2. Confirm with Kenneth after #6 so he
can see the state and decide priorities.

---

## Phase 1.2 (after 1.1 polish is done)

These are queued but not immediate. Kenneth will confirm timing.

- Replace the CSS-recreated logo in the dashboard header with the actual
  `design/AVILANE_FEJ_LOGO_20260423_CLD_v1.svg`
- Add dark mode toggle
- Add run-history sidebar (list past runs, click to view)
- Add error-state smoke test (verify red error UI renders correctly)
- Polish step-transition animations (smooth navy-fill as step completes)

## Phase 1.3 (publish)

### GitHub — personal account, confirmed by Kenneth

- **Repo: `kenebi/friedegg`** (personal account, NOT an org)
- Full URL: `https://github.com/kenebi/friedegg`
- Public, MIT license
- GitHub Pages for docs site eventually
- Consider: GitHub Actions CI running pytest on push

### PyPI

- TestPyPI first: `https://test.pypi.org/project/friedegg/`
- Then production PyPI
- `python -m build` produces the `dist/` artifacts
- `twine upload` for the push (install twine as part of the dev deps)

---

## Brand & Design References

**Do not reinvent the brand.** All brand decisions are finalized in:

`design/BRAND.md`

Key locked decisions:
- **Palette (canonical, from SVG):** Yolk Gold `#F9AA10`, Navy `#1B3C5A`,
  Teal `#22A3A4`, White `#FDFEFE`
- **One exception:** Error red `#D64545` — used ONLY for error UI states
- **Logo files:** `design/AVILANE_FEJ_LOGO_20260423_CLD_v1.{svg,png}`
- **Typography for dashboard:** system font stack (no web fonts in Phase 1)
- **Typography for README/docs:** decide in Phase 2 — DO NOT default to
  AVI Lane's Inter + DM Sans (FEJ is a separate brand)

If you need to produce any new visual asset (favicon, social card, etc.),
**stop and ask Kenneth first** — visual decisions go to CLD, not CDE.
See "Cross-Agent Routing" below.

---

## Kenneth_AI Multi-Agent System (you're part of it)

This project is part of Kenneth's larger workspace (`C:\Kenneth_AI\`)
with a 4-agent system. You (CDE) are one of four agents. The master
context is `C:\Kenneth_AI\CLAUDE.md` but you do NOT need to read it —
this file gives you everything relevant for FEJ.

### Vendor Pairs

| Vendor | Chat Agent | Code Agent |
|--------|-----------|-----------|
| Anthropic | Claude Desktop (CLD) | **Claude Code (CDE) — you** |
| Google | Gemini (GMN) | Gemini CLI (GCL) |

Your primary handoff partner is **CLD**. When Kenneth's using the
Google pair instead, the equivalent code agent is GCL.

### Cross-Agent Routing — when to hand back to CLD

You're great at code iteration, git, tests, and publishing. You're
NOT the best fit for these things — flag and suggest a redirect to CLD:

- **Brand or visual decisions** (colors, logo variants, social cards)
- **Long-form writing** (beyond README — blog posts, marketing copy,
  launch announcements)
- **Cross-business strategy** (how FEJ ties into AVI Lane's commercial
  services, EbiLearn, or Gavins)
- **Planning or roadmap restructuring** (if Kenneth wants to re-sequence
  phases, re-scope the project, etc.)
- **Research** (competitive analysis, naming new features, etc.)

**How to redirect:** name CLD explicitly, one-sentence reason, ask
*"Want to switch, or should I continue here anyway?"* — then accept
Kenneth's answer without re-negotiating. Full protocol in master CLAUDE.md.

### When to stay (do not redirect)

- Writing, testing, running, debugging, or publishing code
- Git operations
- Installing dependencies
- Multi-file refactors within this project
- Small README or docstring edits
- Anything Kenneth explicitly asked you to handle

---

## File Naming Inside This Project

**Inside the `friedegg` package repo**, use standard open-source
conventions (`README.md`, `LICENSE`, `pyproject.toml`,
`src/friedegg/module.py`, `tests/test_module.py`, etc.). Do NOT apply
Kenneth's `BUSINESS_TASK_TYPE_DATE_AGENT_VER` convention to files
that end up in the public git repo — it would look bizarre on GitHub.

**Outside the repo**, if you produce a document Kenneth asked for that
is NOT shipping with the package (e.g. internal notes, a SOP for him
to read, a proposal draft), use the full naming convention with `CDE`:

```
AVILANE_AUTO_SOP_20260425_CDE_v1.md
AVILANE_AUTO_DOCS_20260425_CDE_v1.md
```

These go into the appropriate Tasks folder, NOT into the FEJ repo.

---

## Session Logs & Handoff

**Session log path (workspace-level, not project-level):**

- Current state: `C:\Kenneth_AI\Session_Logs\AVI_Lane\FEJ_Project.md`
- Append-only history: `C:\Kenneth_AI\Session_Logs\AVI_Lane\FEJ_Project_History.md`

**When Kenneth says "save summary":**

1. Overwrite `FEJ_Project.md` with the current latest state
2. Append the same content to `FEJ_Project_History.md` under a new
   date header (never overwrite the history file)
3. Include `*Agent: Claude Code (CDE)*` in the session log header
4. List next steps specific enough for CLD to pick up from if Kenneth
   switches agents

**Proactively remind Kenneth to save a summary** when sessions get deep
or when you're about to wrap — don't let work go unsummarized.

---

## Shell Conventions (non-negotiable)

Kenneth is on PowerShell 7+. When giving commands:

- Use `Invoke-RestMethod` for HTTP, NOT `curl` (curl is aliased to
  `Invoke-WebRequest` in PS and breaks on JSON escaping)
- Windows backslash paths: `C:\Kenneth_AI\...`
- Env vars: `$env:VAR`, not `%VAR%` or `export`
- Scripts: `.\script.ps1`, not `./script.sh`
- `python` not `python3`

Full conventions in master CLAUDE.md's "Shell & Environment Conventions"
section. You generally won't need HTTP commands for FEJ work, but the
Python/pip/git commands should use `.\` and `\` paths.

---

## Things Kenneth Values (from his stated preferences)

- **Directness.** Push back when something is wrong rather than agreeing.
- **Don't over-explain.** He has an IT background and digital marketing
  experience. Match his level.
- **Proactive next-step suggestions.** Don't wait to be asked.
- **Save summaries before wrapping.** Remind him.
- **Action-oriented.** Keep responses practical.
- **He dislikes AI-tells in writing.** Avoid overused em-dashes in any
  prose you produce for README or docs.

---

## Quick Reference — Project Layout

```
FEJ\
├── CLAUDE.md                      ← This file
├── PROJECT_BRIEF.md               ← Original vision (April 14, pre-code)
├── ROADMAP.md                     ← Phased build plan
├── pyproject.toml                 ← Package config
├── .venv\                         ← Virtual environment (gitignored)
├── src\friedegg\
│   ├── __init__.py                ← Exports `monitor` singleton
│   ├── monitor.py                 ← Client API (rename → _client.py in task #5)
│   ├── server.py                  ← FastAPI WebSocket server
│   ├── cli.py                     ← `friedegg dashboard` command
│   └── dashboard\                 ← HTML/CSS/JS UI
├── examples\
│   └── smoke_test.py              ← 5-step dummy automation
├── design\
│   ├── BRAND.md                   ← Brand palette + dashboard state mapping
│   ├── AVILANE_FEJ_LOGO_20260423_CLD_v1.svg
│   └── AVILANE_FEJ_LOGO_20260423_CLD_v1.png
└── docs\                          ← Empty — Phase 1.2+
```

Future additions from Work Queue:
```
├── .gitignore          ← task #1
├── .git\               ← task #1
├── LICENSE             ← task #2
├── README.md           ← task #3
└── tests\              ← task #6
    ├── test_monitor.py
    └── test_server.py
```

---

*You are CDE. You handle this project's code. CLD handles the rest of
Kenneth's workspace. When in doubt about scope, ask.*
