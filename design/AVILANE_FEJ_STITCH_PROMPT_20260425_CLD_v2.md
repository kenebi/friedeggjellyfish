# Claude Design (Stitch) Prompt — FEJ Dashboard v1.2

*Drafted: 2026-04-25 by CLD for Kenneth*
*Use in: Claude Design / Google Stitch*
*Goal: Phase 1.2 dashboard redesign for the friedegg open-source library*
*Supersedes: v1 (different visualization model)*

---

## How to use this file

Paste everything below the `=== PROMPT START ===` line into Claude Design.
The prompt is self-contained — Stitch needs no other files.

After Stitch produces the first design, iterate by asking it to refine
specific elements (jellyfish animation, error state, etc.) one at a time.
Don't expect the first output to be final.

---

=== PROMPT START ===

# Design a dashboard for "friedegg" — an open-source Python monitoring tool

I need a clean, technical dashboard UI for an open-source Python library
called **friedegg**. It runs locally in the user's browser and watches
their automation scripts execute in real time. Think of it as the visual
layer that's missing when developers (and non-developers) move from
drag-and-drop tools (n8n, Zapier) to AI-generated code from Claude Code,
Cursor, or similar agents.

## The product in one sentence

A user pastes `monitor.start()`, `monitor.step()`, `monitor.warn()`,
`monitor.error()`, and `monitor.done()` into their Python script. They
launch this dashboard. As the script runs, the dashboard shows what's
happening live — what step is running right now, whether past steps
succeeded or failed, and what the automation is actually doing.

## Aesthetic direction

**Linear / Vercel feel.** Minimal, technical, lots of whitespace.
Sans-serif system fonts, generous padding, subtle borders, no gradients
or shadows beyond what the brand requires. Information-dense but
breathable. This is a tool used by people who appreciate good craft —
every pixel earns its place.

Avoid: cartoonish illustrations, playful gradients, drop-shadow buttons,
busy patterns, colorful tag clouds, "dashboard widgets" with charts.
This is not a marketing dashboard. It is a developer tool that happens
to be approachable enough for non-developers.

## Brand palette (use exact hex values)

| Token | Hex | Use |
|-------|-----|-----|
| Yolk Gold | `#F9AA10` | Yolk of a successfully-completed step |
| Jellyfish Navy | `#1B3C5A` | Outlines, primary text, completed-jellyfish body |
| Tentacle Teal | `#22A3A4` | Drop-shadows on logo, accent, links, hover |
| Egg White | `#FDFEFE` | Background |
| Error Red | `#D64545` | Yolk of a failed step |
| Warning Orange | `#E89B3C` | Yolk of a step that completed with a soft failure / warning |
| Pending Gray | `rgba(27, 60, 90, 0.35)` | Body of an in-progress step (the "alive but not yet committed" state) |
| Muted text | `rgba(27, 60, 90, 0.65)` | Tagline, durations, descriptions |

Design **light mode first.** Dark mode is a follow-up in the same prompt
(see "Dark mode" section near the end).

## Logo

The brand mark is a stylized **fried egg jellyfish** — a sunny-side-up
fried egg whose yolk is the focal point, with a soft teal drop-shadow
offset to the right that reads as "underwater." The logo is a real SVG
the user already has. In the dashboard:

- **Header:** render the full logo at small size (40–48px tall)
- **Step markers in the workflow timeline:** render as **mini jellyfish
  icons** — the same fried-egg-jellyfish silhouette, simplified for small
  size. Critically, the step markers are NOT just dots — they are mini
  jellyfish, including visible tentacles below the egg body. This is the
  brand's signature visual move and the entire design hinges on it.

## Layout — single page, no sidebar

**No sidebar.** The dashboard is one centered column with a max-width
around 800–900px. From top to bottom:

1. **Header bar** (full-width, thin, with bottom border)
   - Left: FEJ logo + wordmark "friedegg" (lowercase, system-sans medium
     weight) + small tagline beneath: "See your automations glow."
   - Right: connection indicator (small colored dot + label) and a
     dark/light mode toggle (sun/moon icon, not a slider).

2. **Run history — collapsible section** (just below the header,
   collapsed by default)
   - Collapsed: a single thin row, "Run history (12)" with a chevron,
     entire row clickable.
   - Expanded: clean list of past run rows. Each row: workflow name,
     timestamp ("2 min ago"), final status pill (Done / Warning / Error),
     step count ("5 steps"), total duration ("3.2 s"). Clicking a row
     replays that run in the workflow card below. Currently-displayed
     run is highlighted.
   - Empty state: "No past runs yet" in muted text.

3. **Active workflow card** — the heart of the page.
   - **Workflow name** at the top (large, navy, semibold) — e.g.,
     "Daily Lead Report"
   - **Status pill** to the right of the workflow name: "Running" (gold),
     "Done" (navy), "Warning" (orange), "Error" (red)
   - **Current step name** (medium-large, navy, regular weight) — e.g.,
     "Pull new leads from HubSpot". This is the most important piece
     of text on the screen for live runs. It tells the user what their
     automation is doing right now.
   - **Current step description** below the step name (small, muted) —
     e.g., "Querying contacts created in the last 24 hours". Hidden if
     not provided. The layout must not look broken when description
     is absent.
   - **Jellyfish timeline** (the visual flow row — see next section)
   - When the workflow finishes, the "current step" area transitions
     to a summary line: "Completed in 4.32 s" or "Failed at step 3:
     Pull new leads from HubSpot" or "Completed with 2 warnings"

4. **Empty state** — when no run has happened yet, show a centered
   message: "Run your automation to see it appear here in real time."
   Below it, a code snippet box showing the 7-line usage example:
   ```
   from friedegg import monitor

   monitor.start("My workflow")
   monitor.step("Step one", description="What this step does")
   monitor.step("Step two")
   monitor.warn("Soft fail message")  # optional
   monitor.done()
   ```

## The jellyfish timeline — the most important screen

This is FEJ's signature visualization. **Read this section twice.**

### Discovery, not pre-declaration

Steps appear **one at a time, left-to-right, as they happen.** The
dashboard does NOT know future steps in advance. It only knows what's
already been called. There are no gray placeholder dots for future
steps — only steps that have happened or are currently happening
appear in the timeline.

When a new step starts, a fresh jellyfish slides in from the right.
The previous jellyfish (which just finished) settles into its final
state with full color. Continue left-to-right as long as the workflow
runs. Old jellyfish drift left as new ones appear.

### Connector between jellyfish

Between consecutive jellyfish, render **three small dots** (not arrows,
not solid lines). The three dots:

- Static + low-opacity navy when both adjacent jellyfish are in their
  resolved state
- Animated left-to-right shimmer when the rightmost jellyfish is the
  currently-running one (signals "flow is moving")
- Subtly shift toward red/orange when leading into a failed/warned step

Keep the dots small. They are connector punctuation, not focal elements.

### Four jellyfish states (this is the entire visual language)

There is no "pending" state because pending steps don't render.

#### 1. In progress — gray jellyfish with literally waving tentacles

This is the rightmost jellyfish whenever a step is currently executing.

- **Body:** the jellyfish silhouette in **Pending Gray** (`rgba(27, 60, 90, 0.35)`)
  — visible but desaturated, like a real jellyfish underwater
- **Yolk:** also gray-toned, no color yet — the jellyfish hasn't
  "committed" to a state
- **Tentacles:** **literally waving** via SVG path animation. The
  tentacles sway gently left and right, like a real jellyfish drifting
  in current. Aim for organic motion — slight phase offset between
  individual tentacles so they don't all sway in unison.
- The whole jellyfish may also breathe slightly (the bell pulses
  outward 1.0 → 1.04 → 1.0 over ~2 seconds) but the tentacle wave is
  the primary motion.
- Cycle length: roughly 2.5–3 seconds. Slow enough to feel calm, fast
  enough to read as "alive."

This animation is the soul of the dashboard. Get it right and the
whole product feels magical. Get it wrong and it feels like a busted
GIF. **Propose three options for the tentacle animation in isolation
if you're not confident on the first take.**

#### 2. Done (success) — full-color jellyfish, no animation

Once the next `monitor.step()` is called or `monitor.done()` is called,
the in-progress jellyfish transitions to its committed state:

- **Body:** **Jellyfish Navy** (`#1B3C5A`), fully opaque
- **Yolk:** **Yolk Gold** (`#F9AA10`)
- **Tentacles:** still, no animation — gracefully draped below the bell
- This is the "real" jellyfish in full brand color. Past steps in the
  timeline read as a row of completed jellyfish glowing in their
  natural form.

The transition from gray-waving to full-color-still should feel like
a satisfying *bloom* — animate over ~400ms with a soft ease-out.

#### 3. Failed — full-color jellyfish, red yolk

Triggered by `monitor.error()`:

- **Body:** Jellyfish Navy (same as success)
- **Yolk:** **Error Red** (`#D64545`) instead of gold
- **Tentacles:** still
- Below the timeline, an inline error panel appears: thin red left
  border, very light red background, monospace font for the error
  message and traceback. Collapsible.

#### 4. Warning — full-color jellyfish, orange yolk

Triggered by `monitor.warn()`:

- **Body:** Jellyfish Navy
- **Yolk:** **Warning Orange** (`#E89B3C`)
- **Tentacles:** still
- Below the timeline, an inline warning panel: thin orange left border,
  very light orange background, normal-text font (not monospace —
  warnings are messages, not tracebacks). Collapsible.
- The workflow does NOT halt on warning — the next step still runs and
  a new jellyfish appears after this one. This is the key difference
  from error.

### Many steps — what happens with long workflows

For workflows with 3–8 steps, the row fits comfortably in the card
width. For workflows with more steps:

- The row scrolls horizontally if needed, OR
- Older jellyfish shrink slightly to fit, OR
- The view auto-scrolls to keep the in-progress jellyfish in view

**Propose what you think reads cleanest.** Don't wrap to a second line
— that loses the "single flow" reading.

### Hover interactions on past jellyfish

Hovering over any non-in-progress jellyfish shows a tooltip:

- Step name (the one passed to `monitor.step()`)
- Description (if provided)
- Duration (e.g., "1.20 s")
- Final status: Done / Warning / Error

This is how users investigate what each step did after the fact.

## States & frames I need

Please produce the following frames (each is a different state of the
same dashboard):

1. **Empty state** — no run yet, code hint shown
2. **In-flight, mid-run** — workflow running, 5 jellyfish visible:
   2 done (full color, gold yolk), 1 warned (orange yolk), the 5th
   currently in progress (gray, tentacles waving). Current step name
   and description shown above the timeline. Status pill "Running".
3. **Completed successfully** — 5 jellyfish, all done (gold yolks),
   summary text "Completed in 4.32 s". Status pill "Done".
4. **Failed mid-flow** — 4 jellyfish: 2 done, 1 warned, 1 errored
   (red yolk). Error panel expanded below showing a Python traceback.
   Status pill "Error".
5. **Warning state in detail** — close-up showing how the warning
   jellyfish, its orange yolk, and its inline warning panel look
6. **Tentacle animation reference** — show 2–3 frames of the in-progress
   jellyfish's tentacle wave, illustrating the keyframe positions
7. **History expanded** — collapsible expanded with 4–5 past runs
8. **Dark mode variant** of frame #2 (the in-flight mid-run view)

## Dark mode

Derive a dark mode that preserves the brand identity:

- **Yolk Gold stays as `#F9AA10`** — it is the brand
- **Background:** deep desaturated navy (around `#0E1B28` — propose
  what you think looks best, don't go pure black)
- **Egg White becomes the text color** instead of background
- **Pending Gray** for in-progress bodies needs adjustment for dark bg
  — a warmer, lighter gray-blue. Propose a value.
- **Tentacle Teal:** brighten slightly for contrast as a hover/link color
- **Error Red and Warning Orange:** unchanged — both work on dark

The dark mode toggle is a sun/moon icon in the header. One click flips
the theme.

## What to skip

- No charts, graphs, KPI tiles
- No avatars, user accounts, login state — local tool, no auth
- No notification bell, no settings gear (no settings exist yet)
- No mobile design — runs on developer's desktop browser

## Tone of voice (for any UI copy)

Concise, direct, confident, warm but not cute. Sample microcopy:
- Empty state heading: "Run your automation to see it appear here in
  real time."
- Connection states: "Connected", "Connecting…", "Disconnected — retrying"
- Status pills: "Running", "Done", "Warning", "Error" — no exclamation,
  no emoji, no "Completed!" or "Failed 😞"
- Summary lines after completion: "Completed in 4.32 s",
  "Completed with 2 warnings", "Failed at step 3: Pull new leads"

No emoji. No exclamation points anywhere.

## Audience reminder

The end user is often a non-developer who's been building automations
with AI coding tools and got lost when the visual workflow disappeared.
The dashboard's job is to **give them their visual back** — clearly,
calmly, and without making them feel like they're using a developer
tool that wasn't meant for them. But it should also feel polished
enough that an actual developer respects it.

The jellyfish timeline carries the visual weight. The text above it
(step name + description) carries the meaning. Together they answer
the only two questions the user has when they look at the dashboard:
"where am I in the flow?" (timeline) and "what is happening right
now?" (text).

=== PROMPT END ===

---

## Notes for Kenneth (don't paste into Stitch)

### After Stitch responds

1. Look at frame #2 (in-flight mid-run) and frame #6 (tentacle
   animation reference) first. These are the most important. If the
   tentacle animation feels wrong or the in-flight composition is off,
   nothing else matters.
2. If the tentacle animation underwhelms, ask Stitch specifically:
   "Show me 3 different tentacle animation styles in isolation — gentle
   sway, current-drift, and tentacle-curl — at 2x size for clarity."
3. Frame #3 (all gold yolks complete) should be the most aesthetically
   satisfying frame in the set. If it's not, push Stitch on the
   gold-yolk treatment.
4. Dark mode often needs a second pass. The Pending Gray value
   especially — what works on white doesn't translate.

### Phase 1.2 scope this design implies (for CDE later)

This design requires real backend additions, not just CSS:

1. **`monitor.step()` gets `description=None` parameter**
   - Update `_Monitor.step()` signature in `_client.py`
   - Include description in the event payload sent over WebSocket
   - Update existing tests; add new tests for description handling

2. **`monitor.warn(message: str)` is a new method**
   - Mirrors `error()` but emits status="warning" instead of "error"
   - Workflow continues after warn (unlike error)
   - Update `__init__.py` if needed
   - New tests for warn behavior

3. **Dashboard JS updates** to render the new states, the description
   text, the tentacle animation, the three-dot connectors, and the
   collapsible run history

4. **SVG asset work** — the jellyfish step markers need to be a real
   SVG component the dashboard can color-swap and animate. Probably
   a single SVG file with CSS-targeted parts (body, yolk, tentacle paths).

5. **README updates** — document the new `description=` parameter and
   `monitor.warn()` method. Update the 5-line example to show them.

This is more than a CSS pass. CDE will need to know going in. I'll
write a clean spec for him after Stitch's design is approved.

### Things still deliberately punted

- **Run history persistence across server restarts:** still in-memory
  only for Phase 1.2. The history list shows runs since the dashboard
  was launched. Phase 2+ feature.
- **Logo replacement in code:** the actual SVG file is at
  `design/AVILANE_FEJ_LOGO_20260423_CLD_v1.svg`. CDE swaps in the real
  SVG during implementation; Stitch designs with a representation.

### What CDE will need from Stitch's output

- Final HTML/CSS for each frame (Stitch can export this)
- Confirmed pixel values: padding, font sizes, jellyfish dimensions,
  tentacle stroke widths, three-dot sizing
- Animation specs: tentacle keyframe positions, timing, easing,
  bloom-on-completion timing
- Dark mode CSS variables alongside light mode
- The mini-jellyfish SVG component as a clean isolated asset
