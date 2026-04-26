# FEJ Phase 1.2 — Implementation Spec

**Document ID:** AVILANE_FEJ_PHASE_1_2_SPEC_20260425_CLD_v1
**Author:** Claude (CLD)
**Date:** 2026-04-25
**Owner:** Kenneth Ebilane
**Status:** Ready for CDE handoff
**Implements:** Phase 1.2 of the FEJ roadmap

---

## Purpose

This document is the single source of truth for FEJ Phase 1.2 implementation. CDE should be able to read this top-to-bottom and start coding without further design questions.

If anything in this spec is unclear or seems wrong, **stop and ask Kenneth before improvising**. Design decisions in this spec are the result of two design sessions and should not be revised unilaterally.

---

## Scope

Phase 1.2 delivers:

1. A new dashboard UI matching the Stitch design output from session 1
2. Three API additions to `friedegg/_client.py`
3. Aggregate state tracking on the dashboard server
4. An `atexit` safety net for crash cases

**Out of scope for 1.2** (defer to 1.3 or later):
- Persistent run history across server restarts (still in-memory only)
- Authentication / multi-user
- Run search/filter UI
- Export run data
- Webhooks or external integrations

---

## Visual design

### Canonical references

The visual design is locked in. Match these references:

- **`design/fej_logo.svg`** — the canonical jellyfish artwork (used at full size for the header, scaled to ~24–32px for per-step markers)
- **`design/fej_logo_animation.css`** — production-ready CSS for all four per-step states. Use as-is.
- **`design/AVILANE_FEJ_STITCH_OUTPUT_20260425_KEN_*.png`** — screenshot reference for layout and styling. Match closely.

### Header

Top of the dashboard. Static — no animation.

```
[fej_logo.svg, ~44px]   Fried Egg Jellyfish
                        [tagline placeholder]
                                                    [connection indicator]
```

- Logo is the static, full-color `fej_logo.svg` (no state classes applied)
- Product name text is **"Fried Egg Jellyfish"** (full name, three words) — NOT "friedegg"
- The Python package, CLI, and import path stay as `friedegg`. Only the displayed brand name uses the full version.
- Tagline placeholder: keep current `"See your automations glow."` for v1. Kenneth will replace before ship.
- Connection indicator stays as it is currently — colored dot + label

### Workflow card layout (active run)

Reference: Stitch frame 02 (in-flight) and frame 03 (completed).

```
┌────────────────────────────────────────────────────────────┐
│ [Workflow name, h2]                              [pill]    │
│ [Current step name, prominent]                             │
│ [Step description, muted]                                  │
│                                                            │
│   [breathing room — INCREASE this from session 1 designs]  │
│                                                            │
│   🪼 ··· 🪼 ··· 🪼 ··· 🪼 ··· 🪼 ···                       │
│   0.42s  0.18s  0.91s  0.27s  ——                          │
└────────────────────────────────────────────────────────────┘
```

**Spacing fix (important):** the jellyfish row needs more vertical space from the description block above it than what Stitch showed. Bump the gap noticeably — the row should feel like its own zone, not glued to the text.

### Per-step jellyfish markers

Each step in the timeline is rendered as an inline copy of `fej_logo.svg` with one of four state classes applied. The CSS in `fej_logo_animation.css` handles all visuals.

**State classes:**
- `.fej-state-running` — grayscale + 50% opacity + shadow pulse 2.5s
- `.fej-state-done` — full color, no motion (default brand state, no CSS needed)
- `.fej-state-warn` — burnt orange yolk `#E87528` + yolk pulse 1.2s
- `.fej-state-error` — red yolk `#D64545`, no motion

**Hard contract — DO NOT BREAK:**

The CSS targets `#Yolk path` and `#Shadow` selectors inside the SVG. The `<g id="Yolk">` and `<g id="Shadow">` groups in `fej_logo.svg` MUST remain intact. If you minify or process the SVG and lose these IDs, all state animations will silently fail.

**Implementation approach:**
- Inline the SVG in the HTML (don't use `<img>` or `<object>` — CSS won't reach inside)
- Render once with a JS template, then apply state classes per step

### Three-dot connectors

Between every two jellyfish, render three small dots (`···`) that represent the flow.

- Default state: gray, static (`#888780` or similar muted)
- Animated: dots light up sequentially as the flow advances
- Active (flow currently passing through): leftmost dot lights up, then middle, then right, in a ~600ms sequence
- Completed (flow has passed): all three dots match the color of the completed step they connect from (gold for done, burnt orange for warn, etc.)

The animation timing should feel like a "wave" passing through the dots in sync with the running step's pulse.

### Boustrophedon layout (long workflows)

When the row of jellyfish exceeds the container width, **wrap to a new row reading right-to-left**, then back left-to-right, etc.

```
🪼 ··· 🪼 ··· 🪼 ··· 🪼 ··· 🪼 ···
                                  ⋮
🪼 ··· 🪼 ··· 🪼 ··· 🪼 ··· 🪼 ···   (jellyfish flipped via scaleX(-1))
⋮
🪼 ··· 🪼 ···
```

**Implementation requirements:**
- Even-numbered rows (2, 4, 6...) flip the jellyfish: `transform: scaleX(-1)` on the SVG
- Odd-numbered rows (1, 3, 5...) render normally
- Step ordering within a row reverses on even rows so the temporal flow follows the visual eye-path
- Corner connector at row break: three dots arranged vertically (L-shape, not a curve)
- Corner dots animate the same way as horizontal dots — sequential light-up
- Row break responds to container width — use CSS Grid with `auto-fill` or `auto-fit` and let the browser decide where to wrap

**Row-break breakpoint:** let the layout decide based on available width. No fixed step-per-row count.

**Verified by Kenneth:** the flipped jellyfish reads naturally — the shadow stays consistent, legs flow in the direction of motion, silhouette is recognizably the same creature. Don't second-guess this; it's been tested visually.

### Status pill (top-right of workflow card)

There are TWO pills with similar styling but different roles:

**Active card pill** (the one inside the active workflow card):
- During run: mirrors the current step's status — almost always `Running`, briefly other states if a step warns or errors mid-flow
- After run: switches to the terminal aggregate label (see below)
- Width: must accommodate `Done with warnings` (longest label) — let it grow, never truncate

**History pill** (per row in the run history list):
- For the active run: shows `Running`
- For completed runs: shows the terminal aggregate label

**Pill labels:**
| State | Label | Color (suggested) |
|---|---|---|
| In flight | `Running` | burnt orange or gold (match current frame 02) |
| Clean success | `Done` | green or navy (match current frame 03) |
| Soft fail | `Done with warnings` | burnt orange `#E87528` |
| Hard fail | `Done with errors` | red `#D64545` |

### Tooltip on hover

Hovering a past jellyfish (any state except the active running one) shows:

- Step name (bold)
- Step description (if provided)
- Duration (formatted as `0.42 s` or `123 ms`)
- Status (Done / Warning / Error, plus message if warn/error)

Tooltip styling matches the rest of the dashboard. No need to over-design.

### Run history (collapsible top section)

Reference: Stitch frame 07 (history expanded).

- Collapsed by default, click to expand
- Each row shows: workflow name | timestamp ("2 min ago") | status pill | step count | total duration
- Active run is the topmost row, highlighted somehow (background tint)
- Click a historical row to load it into the workflow card below (replacing the active run view if no run is currently in progress)
- In-memory only; persists across browser refreshes only as long as the dashboard server is running

---

## API changes

All changes are in `src/friedegg/_client.py`. The `Event` dataclass and the WebSocket schema also need updating.

### 1. `monitor.step()` gets `description` parameter

**Current signature:**
```python
def step(self, step_name: str, status: str = "done", metadata: dict | None = None) -> None
```

**New signature:**
```python
def step(self, step_name: str, description: str | None = None,
         status: str = "running", metadata: dict | None = None) -> None
```

**Changes:**
- New `description` parameter, optional, second positional. Free-form short string (≤200 chars recommended, no enforcement).
- Default `status` changes from `"done"` to `"running"` — when a user calls `monitor.step("X")`, they are starting step X, not finishing it. The auto-finalization of the previous step (already implemented) handles marking the previous step done.
- `description` flows through to the dashboard via the `Event.metadata["description"]` field. The dashboard renders it as the second-line text in the workflow card (the muted line under the step name).

**Backward compatibility:** the new `description` parameter is keyword-optional; existing calls keep working. The default `status` change is a behavior fix — old calls passing `status="done"` explicitly are unaffected.

### 2. New `monitor.warn()` method

**Signature:**
```python
def warn(self, message: str, details: str | None = None,
         step_name: str | None = None) -> None
```

**Behavior:**
- Emits an event of type `"warn"` (new event type)
- Marks the current step's state as `warn` in the dashboard
- Does NOT terminate the workflow. Subsequent `step()` calls work normally.
- Is symmetric with `error()` — same shape, just less severe semantically

**Event payload structure:**
```python
Event(
    event_type="warn",
    run_id=...,
    workflow_name=...,
    step_name=step_name or self._last_step_name,
    status="warn",
    error_message=message,        # reuse the error_message field
    error_traceback=details,       # reuse the error_traceback field
)
```

(The field names `error_message` / `error_traceback` are now slightly misleading. We're reusing them for warns to avoid schema churn. Optionally, rename to `message` / `details` later — defer that decision.)

### 3. `monitor.error()` behavior clarified (no signature change)

**No code change required**, but document this clearly:

- `error()` is **informational only**. It does NOT terminate the workflow.
- The user's script controls flow. If they want to stop on error, they `raise` themselves.
- This matches the FEJ philosophy: *workflows always run to completion. FEJ records what happened.*

If the user's script raises an unhandled exception after calling `error()` (or without calling anything), the `atexit` hook catches it (see #4 below).

### 4. `atexit` safety net

**Problem:** if the user's script crashes before calling `monitor.done()`, the dashboard never sees a terminal event and the run sits at `Running` forever.

**Solution:** register an `atexit` hook in `_Monitor.start()` that fires a synthetic `workflow_done` event if the run is still open at process exit.

**Implementation sketch:**
```python
import atexit

class _Monitor:
    def start(self, ...):
        # ... existing logic ...
        atexit.register(self._atexit_finalize)

    def _atexit_finalize(self):
        if self._run_id is None:
            return  # already done() was called
        # Close the last open step
        if self._last_step_name is not None:
            now = time.monotonic()
            self._sender.send(Event(
                event_type="step",
                step_name=self._last_step_name,
                status="error",  # crashed mid-step
                duration_ms=(now - self._step_start) * 1000 if self._step_start else None,
                error_message="Workflow ended without monitor.done() — script may have crashed.",
            ))
        # Send terminal event
        self._sender.send(Event(
            event_type="workflow_done",
            run_id=self._run_id,
            workflow_name=self._workflow_name,
            status="done",  # aggregate logic on dashboard side will compute final pill
        ))
        self._sender.stop()
```

**Edge cases:**
- If `done()` was called normally, `_run_id` is `None`, atexit does nothing
- If `start()` was never called, atexit does nothing
- The synthetic step-error event ensures the active step's marker turns red, not stuck as gray-pulsing

### 5. Aggregate state tracking on the dashboard

**Problem:** the dashboard currently plays back events but has no concept of an aggregate "did this run have errors / warnings?" state.

**Solution:** add a per-run aggregate to the dashboard server's run-history store.

**Server-side changes** (likely in `src/friedegg/server.py`):
- Each `Run` object tracks: `has_errors: bool`, `has_warnings: bool`
- On every `error` event: set `has_errors = True`
- On every `warn` event: set `has_warnings = True`
- On `workflow_done` event: compute the final terminal label:
  ```python
  if run.has_errors:
      run.final_status = "done_with_errors"
  elif run.has_warnings:
      run.final_status = "done_with_warnings"
  else:
      run.final_status = "done"
  ```

**Dashboard client (JS) changes:**
- Read `final_status` from the WebSocket event
- Map to pill label:
  - `done_with_errors` → `Done with errors` (red pill)
  - `done_with_warnings` → `Done with warnings` (burnt orange pill)
  - `done` → `Done` (green pill)
  - `running` → `Running` (orange pill, animated dot)

---

## File-level changes summary

| File | Change |
|---|---|
| `src/friedegg/_client.py` | Add `description=` param to `step()`, change default status, add `warn()`, add `atexit` hook |
| `src/friedegg/server.py` | Track per-run `has_errors` / `has_warnings`, compute `final_status` on workflow_done |
| `src/friedegg/dashboard/index.html` | New layout: header with full name, workflow card with prominent step name + description, jellyfish timeline, run history collapsible |
| `src/friedegg/dashboard/style.css` | Import or inline `fej_logo_animation.css`. Add boustrophedon layout, three-dot connectors, pill styles, tooltip styles |
| `src/friedegg/dashboard/script.js` | Render inline jellyfish SVGs per step, manage state classes, handle row-direction flipping for boustrophedon, animate connector dots in sequence, pill update logic |
| `src/friedegg/dashboard/fej_logo.svg` | NEW — copy from `design/fej_logo.svg` into the served assets |
| `tests/test_client.py` | Add tests for `warn()`, `description=`, `atexit` behavior |

---

## Tests CDE should add

At minimum:

- `monitor.warn("msg")` emits a `warn` event with the right shape
- `monitor.warn()` does not terminate the workflow (subsequent `step()` calls work)
- `monitor.step("X", description="desc")` includes description in the event metadata
- `monitor.error()` followed by `monitor.step()` followed by `monitor.done()` produces a final aggregate of `done_with_errors`
- `monitor.warn()` followed by `monitor.done()` produces `done_with_warnings`
- A run that calls only `start()` and `step()` then exits (simulated) triggers atexit and produces a terminal event with `done_with_errors` (because the open step is marked errored)

---

## What CDE should NOT do

- Do not redesign any visual element. Match the Stitch screenshots and the CSS in `fej_logo_animation.css`.
- Do not rename `friedegg` to anything else. Only the displayed brand name is "Fried Egg Jellyfish".
- Do not make `error()` or `warn()` terminate the workflow. They are informational only.
- Do not preserve the current `status="done"` default in `step()` — change it to `"running"`.
- Do not skip the `atexit` hook. It's small but critical to avoid stuck runs.
- Do not change the SVG group IDs (`Yolk`, `Shadow`, `Body`, `LegsWhiteBG`, `ShineYolk`). The CSS depends on them.

---

## Open questions for CDE during implementation

These are intentionally left for CDE to resolve based on what works in code:

- **CSS Grid vs flex-wrap with JS hint** for the boustrophedon layout. Either is acceptable — pick the cleaner implementation.
- **Connector dot timing** — exact ms values for the sequential light-up. Aim for "feels alive but not frantic". Calibrate against the running pulse (2.5s) so the rhythms harmonize.
- **Performance with 30+ steps** — test it. If frame rate suffers, profile and consider switching the running-state animation from `filter: grayscale + opacity` (which can be expensive on many elements) to a simpler approach like a precomputed gray SVG variant.
- **Dark mode** — Stitch frame 08 shows dark mode. CSS variables should already handle most of it; verify the burnt orange and red yolks have enough contrast on dark backgrounds.

If any of these turn into design decisions (not just implementation choices), stop and ask Kenneth.

---

## Definition of done

Phase 1.2 is complete when:

- [ ] All API changes implemented and tested (warn, description, atexit, aggregate state)
- [ ] Dashboard UI matches Stitch screenshots (within reason — small spacing/color tweaks OK)
- [ ] All four jellyfish states render correctly per step
- [ ] Boustrophedon layout works for workflows of varying length
- [ ] Three-dot connectors animate sequentially
- [ ] Pill labels show correctly for all four terminal states
- [ ] Tooltip on past jellyfish shows step details
- [ ] Run history collapsible works
- [ ] All existing Phase 1.1 tests still pass
- [ ] New tests cover warn/description/atexit/aggregate
- [ ] `friedegg dashboard` CLI still launches everything cleanly
- [ ] Header reads "Fried Egg Jellyfish" next to logo

---

## Reference: full color palette used in 1.2

| Token | Hex | Usage |
|---|---|---|
| Navy | `#1B3C5A` | Body, oral arms, default brand |
| Gold | `#F9AA10` | Done state yolk, primary brand accent |
| Teal | `#22A3A4` | Shadow group in static logo |
| White | `#FDFEFE` | Background, oral arm fills |
| Burnt orange | `#E87528` | Warn state yolk, warn pill |
| Red | `#D64545` | Error state yolk, error pill |
| Pending gray | `#888780` | Running state body |
| Pending gray 2 | `#B4B2A9` | Running state yolk |

---

## Handoff checklist for Kenneth

Before this spec is handed to CDE, Kenneth should:

- [ ] Save Stitch screenshots into `design/` with the suggested filenames (frame 02, 03, 07, 08 minimum)
- [ ] Write the v1 tagline (or confirm the existing placeholder is fine for v1)
- [ ] Read this spec end-to-end and flag anything that doesn't match what was decided in sessions 1 and 2
- [ ] Endorse to CDE via the FEJ session log
