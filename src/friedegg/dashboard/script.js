/* ============================================================
   friedegg dashboard — Phase 1.2
   WebSocket client + jellyfish timeline rendering
   ============================================================ */

(() => {
  "use strict";

  const WS_URL = `ws://${location.host}/ws/dashboard`;

  // Severity order for step status — never downgrade.
  const SEVERITY = { error: 4, warn: 3, done: 2, running: 1, pending: 0 };

  // Pill label and CSS class for each terminal state.
  const PILL_MAP = {
    running:           { label: "Running",            cls: "pill-running" },
    done:              { label: "Done",               cls: "pill-done" },
    done_with_warnings:{ label: "Done with warnings", cls: "pill-done-warnings" },
    done_with_errors:  { label: "Done with errors",   cls: "pill-done-errors" },
  };

  // ---------------------------------------------------------------------------
  // Runtime state
  // ---------------------------------------------------------------------------

  // Map<run_id, RunData> — all runs seen this session (for history panel).
  // RunData: { runId, workflowName, startedAt, completedAt, finalStatus,
  //            stepOrder: string[], steps: Map<string, StepData> }
  // StepData: { name, description, status, duration_ms, error_message, warn_message }
  const runs = new Map();

  let currentRunId   = null;  // run currently receiving events
  let displayedRunId = null;  // run shown in the workflow card

  // Cached jellyfish SVG template (fetched once, cloned per step).
  let JELLY_TEMPLATE = null;

  // ---------------------------------------------------------------------------
  // DOM references
  // ---------------------------------------------------------------------------

  const el = {
    connIndicator:    document.getElementById("conn-indicator"),
    connLabel:        document.getElementById("conn-label"),
    headerLogo:       document.getElementById("header-logo"),
    workflowCard:     document.getElementById("workflow-card"),
    workflowName:     document.getElementById("workflow-name"),
    workflowPill:     document.getElementById("workflow-pill"),
    currentStepName:  document.getElementById("current-step-name"),
    currentStepDesc:  document.getElementById("current-step-desc"),
    stepTimeline:     document.getElementById("step-timeline"),
    emptyState:       document.getElementById("empty-state"),
    historyPanel:     document.getElementById("history-panel"),
    historyToggle:    document.getElementById("history-toggle"),
    historyList:      document.getElementById("history-list"),
    tooltip:          document.getElementById("step-tooltip"),
  };

  // ---------------------------------------------------------------------------
  // Jellyfish SVG loading
  // ---------------------------------------------------------------------------

  async function loadJellyfishTemplate() {
    try {
      const resp = await fetch("/static/fej_logo.svg");
      const text = await resp.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(text, "image/svg+xml");
      const svg = doc.querySelector("svg");
      if (!svg) return;

      // Remove inline <style> block to prevent class name pollution in HTML doc.
      svg.querySelector("style")?.remove();

      // Convert class-based fills to presentation attributes.
      const classToFill = { s0: "#ffffff", s1: "#22a3a4", s2: "#1b3c5a", s3: "#f9aa10" };
      svg.querySelectorAll("[class]").forEach(el => {
        const fill = classToFill[el.getAttribute("class")];
        if (fill) {
          el.setAttribute("fill", fill);
          el.removeAttribute("class");
        }
      });

      // Strip path-level IDs (keep group IDs — the animation CSS targets them).
      svg.querySelectorAll("path[id]").forEach(p => p.removeAttribute("id"));

      JELLY_TEMPLATE = svg;
      renderHeaderLogo();
    } catch (e) {
      console.warn("FEJ: could not load jellyfish SVG", e);
    }
  }

  function cloneJellyfish(stateClass) {
    if (!JELLY_TEMPLATE) {
      // Fallback: empty div so layout doesn't break.
      const fb = document.createElement("div");
      fb.className = "step-jelly";
      return fb;
    }
    const svg = JELLY_TEMPLATE.cloneNode(true);
    svg.classList.add("fej-logo", "step-jelly");
    if (stateClass) svg.classList.add(stateClass);
    return svg;
  }

  function renderHeaderLogo() {
    if (!JELLY_TEMPLATE || !el.headerLogo) return;
    el.headerLogo.innerHTML = "";
    const svg = JELLY_TEMPLATE.cloneNode(true);
    svg.classList.add("fej-logo");
    // Header logo is always full-color static (no state class).
    el.headerLogo.appendChild(svg);
  }

  // ---------------------------------------------------------------------------
  // Status helpers
  // ---------------------------------------------------------------------------

  function resolveStatus(current, incoming) {
    const cur = SEVERITY[current] ?? 0;
    const inc = SEVERITY[incoming] ?? 0;
    return inc > cur ? incoming : current;
  }

  function stepStateClass(status) {
    switch (status) {
      case "running": return "fej-state-running";
      case "done":    return "fej-state-done";
      case "warn":    return "fej-state-warn";
      case "error":   return "fej-state-error";
      default:        return "fej-state-running";
    }
  }

  function formatDuration(ms) {
    if (ms == null) return "—";
    if (ms < 1000) return `${Math.round(ms)} ms`;
    return `${(ms / 1000).toFixed(2)} s`;
  }

  function timeAgo(ts) {
    const diff = Date.now() - ts;
    if (diff < 60000)  return `${Math.round(diff / 1000)}s ago`;
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    return `${Math.floor(diff / 3600000)}h ago`;
  }

  // ---------------------------------------------------------------------------
  // Run data helpers
  // ---------------------------------------------------------------------------

  function getOrCreateRun(runId, workflowName) {
    if (!runs.has(runId)) {
      runs.set(runId, {
        runId,
        workflowName: workflowName || "Workflow",
        startedAt: Date.now(),
        completedAt: null,
        finalStatus: null,
        stepOrder: [],
        steps: new Map(),
      });
    }
    return runs.get(runId);
  }

  function upsertStep(run, event) {
    const name = event.step_name;
    if (!name) return;

    if (!run.steps.has(name)) {
      run.stepOrder.push(name);
      run.steps.set(name, {
        name,
        description: event.metadata?.description ?? null,
        status: "pending",
        duration_ms: null,
        error_message: null,
        warn_message: null,
      });
    }

    const step = run.steps.get(name);

    // Merge description (first non-null wins).
    if (!step.description && event.metadata?.description) {
      step.description = event.metadata.description;
    }

    // Apply status with severity ordering (never downgrade).
    const incoming = event.status || "pending";
    step.status = resolveStatus(step.status, incoming);

    // Duration only comes in on the "done" auto-close event.
    if (event.duration_ms != null) {
      step.duration_ms = event.duration_ms;
    }

    // Capture messages.
    if (event.event_type === "warn" && event.error_message) {
      step.warn_message = event.error_message;
    }
    if ((event.event_type === "error" || incoming === "error") && event.error_message) {
      step.error_message = event.error_message;
    }
  }

  // ---------------------------------------------------------------------------
  // Rendering: connection status
  // ---------------------------------------------------------------------------

  function setConnection(state, label) {
    el.connIndicator.className = `dot dot-${state}`;
    el.connLabel.textContent = label;
  }

  // ---------------------------------------------------------------------------
  // Rendering: pill
  // ---------------------------------------------------------------------------

  function setPill(statusKey) {
    const p = PILL_MAP[statusKey] || PILL_MAP.running;
    el.workflowPill.textContent = p.label;
    el.workflowPill.className = `pill ${p.cls}`;
  }

  // ---------------------------------------------------------------------------
  // Rendering: current step header
  // ---------------------------------------------------------------------------

  function updateCurrentStepHeader(run) {
    if (!run) return;

    if (!run.finalStatus) {
      // Active run: find the running step.
      const runningName = run.stepOrder
        .slice()
        .reverse()
        .find(n => run.steps.get(n)?.status === "running");

      if (runningName) {
        const step = run.steps.get(runningName);
        el.currentStepName.textContent = step.name;
        if (step.description) {
          el.currentStepDesc.textContent = step.description;
          el.currentStepDesc.classList.remove("hidden");
        } else {
          el.currentStepDesc.classList.add("hidden");
        }
        return;
      }
    }

    // Workflow complete or historical: show terminal status.
    const fs = run.finalStatus;
    if (fs) {
      el.currentStepName.textContent =
        fs === "done"               ? "Workflow complete" :
        fs === "done_with_warnings" ? "Completed with warnings" :
                                     "Completed with errors";
    } else {
      el.currentStepName.textContent = run.workflowName;
    }
    el.currentStepDesc.classList.add("hidden");
  }

  // ---------------------------------------------------------------------------
  // Rendering: boustrophedon timeline
  // ---------------------------------------------------------------------------

  function connectorClass(fromStep, toStep) {
    // Active if the "to" step is currently running.
    if (toStep && toStep.status === "running") return "connector-active";
    switch (fromStep?.status) {
      case "done":  return "connector-gold";
      case "warn":  return "connector-warn";
      case "error": return "connector-error";
      default:      return "";
    }
  }

  function createConnectorEl(fromStep, toStep) {
    const div = document.createElement("div");
    div.className = "connector";
    const cls = connectorClass(fromStep, toStep);
    if (cls) div.classList.add(cls);
    for (let i = 0; i < 3; i++) {
      const dot = document.createElement("div");
      dot.className = "connector-dot";
      div.appendChild(dot);
    }
    return div;
  }

  function createCornerEl(fromRowIsRTL) {
    const div = document.createElement("div");
    div.className = `corner-connector ${fromRowIsRTL ? "corner-left" : "corner-right"}`;
    for (let i = 0; i < 3; i++) {
      const dot = document.createElement("div");
      dot.className = "corner-dot";
      div.appendChild(dot);
    }
    return div;
  }

  function createStepMarkerEl(step) {
    const wrap = document.createElement("div");
    wrap.className = "step-marker";
    wrap.dataset.step = step.name;
    wrap.dataset.state = step.status;

    const jelly = cloneJellyfish(stepStateClass(step.status));
    wrap.appendChild(jelly);

    const dur = document.createElement("div");
    dur.className = "step-duration-label";
    dur.textContent = formatDuration(step.duration_ms);
    wrap.appendChild(dur);

    // Tooltip (shown on hover for completed steps via JS).
    attachTooltipListeners(wrap, step);

    return wrap;
  }

  function renderTimeline(run) {
    const container = el.stepTimeline;
    container.innerHTML = "";
    if (!run || run.stepOrder.length === 0) return;

    const steps = run.stepOrder.map(n => run.steps.get(n));

    // Determine steps per row based on container width.
    // Each step-marker is ~48px + connector ~34px = ~82px per unit.
    const containerWidth = container.clientWidth || 700;
    const UNIT_W = 82;
    const stepsPerRow = Math.max(2, Math.floor(containerWidth / UNIT_W));

    // Chunk steps into rows.
    const rows = [];
    for (let i = 0; i < steps.length; i += stepsPerRow) {
      rows.push(steps.slice(i, i + stepsPerRow));
    }

    rows.forEach((rowSteps, rowIdx) => {
      const isRTL = rowIdx % 2 === 1;

      const rowEl = document.createElement("div");
      rowEl.className = `timeline-row${isRTL ? " timeline-row-rtl" : ""}`;

      rowSteps.forEach((step, colIdx) => {
        const isLastInRow   = colIdx === rowSteps.length - 1;
        const isLastOverall = rowIdx === rows.length - 1 && isLastInRow;

        const marker = createStepMarkerEl(step);
        rowEl.appendChild(marker);

        if (!isLastOverall) {
          // Connector after each step except the last step overall.
          // After the last step in a row, still add a connector — the corner
          // connector below visually extends it.
          const nextStep = !isLastInRow ? rowSteps[colIdx + 1] : null;
          const conn = createConnectorEl(step, nextStep);
          rowEl.appendChild(conn);
        }
      });

      container.appendChild(rowEl);

      // Corner connector between rows (not after the last row).
      if (rowIdx < rows.length - 1) {
        container.appendChild(createCornerEl(isRTL));
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Rendering: run history panel
  // ---------------------------------------------------------------------------

  function updateHistoryPanel() {
    if (runs.size === 0) return;

    el.historyList.innerHTML = "";
    const sorted = [...runs.values()].sort((a, b) => b.startedAt - a.startedAt);

    sorted.forEach(run => {
      const row = document.createElement("div");
      row.className = "history-row";
      if (run.runId === currentRunId) row.classList.add("active-run");

      const statusKey = run.finalStatus || (run.runId === currentRunId ? "running" : "running");
      const pill = PILL_MAP[statusKey] || PILL_MAP.running;

      row.innerHTML = `
        <span class="history-name">${escHtml(run.workflowName)}</span>
        <span class="history-time">${timeAgo(run.startedAt)}</span>
        <span class="history-steps">${run.stepOrder.length} step${run.stepOrder.length !== 1 ? "s" : ""}</span>
        <span class="pill ${pill.cls}">${pill.label}</span>
      `;

      row.addEventListener("click", () => {
        displayedRunId = run.runId;
        renderCard(run);
      });

      el.historyList.appendChild(row);
    });

    // Show panel if there's at least one completed run or more than one total.
    if (runs.size > 1 || [...runs.values()].some(r => r.finalStatus)) {
      el.historyPanel.style.display = "";
    }
  }

  function escHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // ---------------------------------------------------------------------------
  // Rendering: full workflow card
  // ---------------------------------------------------------------------------

  function renderCard(run) {
    if (!run) return;
    displayedRunId = run.runId;

    el.workflowCard.classList.remove("hidden");
    el.emptyState.classList.add("hidden");

    el.workflowName.textContent = run.workflowName;

    // Pill.
    if (run.finalStatus) {
      setPill(run.finalStatus);
    } else {
      setPill("running");
    }

    updateCurrentStepHeader(run);
    renderTimeline(run);
  }

  // ---------------------------------------------------------------------------
  // Tooltip
  // ---------------------------------------------------------------------------

  function attachTooltipListeners(markerEl, step) {
    markerEl.addEventListener("mouseenter", (e) => {
      if (step.status === "running" || step.status === "pending") return;
      showTooltip(e, step);
    });
    markerEl.addEventListener("mousemove", (e) => {
      if (step.status === "running" || step.status === "pending") return;
      positionTooltip(e);
    });
    markerEl.addEventListener("mouseleave", () => {
      el.tooltip.classList.add("hidden");
      el.tooltip.setAttribute("aria-hidden", "true");
    });
  }

  function showTooltip(e, step) {
    const statusLabel =
      step.status === "done"  ? "Done"    :
      step.status === "warn"  ? "Warning" :
      step.status === "error" ? "Error"   : step.status;

    const statusCls =
      step.status === "warn"  ? "tooltip-status-warn"  :
      step.status === "error" ? "tooltip-status-error" :
                                "tooltip-status-done";

    let html = `<div class="tooltip-name">${escHtml(step.name)}</div>`;
    if (step.description) {
      html += `<div class="tooltip-desc">${escHtml(step.description)}</div>`;
    }
    html += `<div class="tooltip-meta">`;
    html += `<span class="tooltip-duration">${formatDuration(step.duration_ms)}</span>`;
    html += `<span class="${statusCls}">${statusLabel}</span>`;
    html += `</div>`;
    if (step.warn_message) {
      html += `<div class="tooltip-message">${escHtml(step.warn_message)}</div>`;
    }
    if (step.error_message) {
      html += `<div class="tooltip-message" style="color:var(--fej-error)">${escHtml(step.error_message)}</div>`;
    }

    el.tooltip.innerHTML = html;
    el.tooltip.classList.remove("hidden");
    el.tooltip.setAttribute("aria-hidden", "false");
    positionTooltip(e);
  }

  function positionTooltip(e) {
    const pad = 12;
    const tw = el.tooltip.offsetWidth;
    const th = el.tooltip.offsetHeight;
    let x = e.clientX + pad;
    let y = e.clientY - th - pad;
    if (x + tw > window.innerWidth)  x = e.clientX - tw - pad;
    if (y < 0)                       y = e.clientY + pad;
    el.tooltip.style.left = `${x}px`;
    el.tooltip.style.top  = `${y}px`;
  }

  // ---------------------------------------------------------------------------
  // Event handling
  // ---------------------------------------------------------------------------

  function handleEvent(event) {
    const { event_type, run_id, workflow_name } = event;
    if (!run_id) return;

    const run = getOrCreateRun(run_id, workflow_name);

    switch (event_type) {
      case "workflow_start":
        currentRunId  = run_id;
        displayedRunId = run_id;
        renderCard(run);
        updateHistoryPanel();
        break;

      case "step":
        upsertStep(run, event);
        if (displayedRunId === run_id) {
          updateCurrentStepHeader(run);
          renderTimeline(run);
        }
        updateHistoryPanel();
        break;

      case "warn":
      case "error":
        upsertStep(run, event);
        if (displayedRunId === run_id) {
          updateCurrentStepHeader(run);
          renderTimeline(run);
        }
        break;

      case "workflow_done":
        run.completedAt  = Date.now();
        run.finalStatus  = event.final_status || "done";
        if (displayedRunId === run_id) {
          setPill(run.finalStatus);
          updateCurrentStepHeader(run);
          renderTimeline(run);
        }
        updateHistoryPanel();
        break;

      default:
        // Ignore unknown events silently.
        break;
    }
  }

  // ---------------------------------------------------------------------------
  // History toggle
  // ---------------------------------------------------------------------------

  el.historyToggle.addEventListener("click", () => {
    const expanded = el.historyToggle.getAttribute("aria-expanded") === "true";
    el.historyToggle.setAttribute("aria-expanded", String(!expanded));
    el.historyList.hidden = expanded;
    if (!expanded) updateHistoryPanel(); // refresh timestamps on open
  });

  // Hide history panel initially (shown once there are runs).
  el.historyPanel.style.display = "none";

  // ---------------------------------------------------------------------------
  // ResizeObserver: re-render timeline on container width change
  // ---------------------------------------------------------------------------

  if (window.ResizeObserver) {
    new ResizeObserver(() => {
      const run = runs.get(displayedRunId);
      if (run) renderTimeline(run);
    }).observe(el.stepTimeline);
  }

  // ---------------------------------------------------------------------------
  // WebSocket lifecycle
  // ---------------------------------------------------------------------------

  let reconnectDelay = 1000;
  const MAX_RECONNECT_DELAY = 15000;

  function connectWS() {
    setConnection("pending", "Connecting…");
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setConnection("connected", "Connected");
      reconnectDelay = 1000;
    };

    ws.onmessage = (msg) => {
      try {
        handleEvent(JSON.parse(msg.data));
      } catch (err) {
        console.error("FEJ: bad event payload", msg.data, err);
      }
    };

    ws.onclose = () => {
      setConnection("error", "Disconnected — retrying…");
      setTimeout(connectWS, reconnectDelay);
      reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_DELAY);
    };

    ws.onerror = () => {
      // onclose handles reconnect.
    };
  }

  // ---------------------------------------------------------------------------
  // Boot
  // ---------------------------------------------------------------------------

  loadJellyfishTemplate().then(() => connectWS());

})();
