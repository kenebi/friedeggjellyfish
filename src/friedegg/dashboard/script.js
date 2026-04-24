/* ============================================================
   friedegg dashboard — WebSocket client + live rendering
   ============================================================ */

(() => {
  "use strict";

  const WS_URL = `ws://${location.host}/ws/dashboard`;

  const el = {
    connIndicator: document.getElementById("conn-indicator"),
    connLabel:     document.getElementById("conn-label"),
    workflowCard:  document.getElementById("workflow-card"),
    workflowName:  document.getElementById("workflow-name"),
    workflowStatus:document.getElementById("workflow-status"),
    stepList:      document.getElementById("step-list"),
    emptyState:    document.getElementById("empty-state"),
  };

  // Map of step_name -> <li> element for the current run.
  const stepEls = new Map();
  let currentRunId = null;

  // ---- connection status ------------------------------------------------
  function setConnection(state, label) {
    el.connIndicator.className = `dot dot-${state}`;
    el.connLabel.textContent = label;
  }

  // ---- rendering helpers ------------------------------------------------
  function showCard() {
    el.workflowCard.classList.remove("hidden");
    el.emptyState.classList.add("hidden");
  }

  function resetCard() {
    el.stepList.innerHTML = "";
    stepEls.clear();
  }

  function setWorkflowStatus(label, variant) {
    el.workflowStatus.textContent = label;
    el.workflowStatus.className = `pill pill-${variant}`;
  }

  function formatDuration(ms) {
    if (ms == null) return "";
    if (ms < 1000) return `${Math.round(ms)} ms`;
    return `${(ms / 1000).toFixed(2)} s`;
  }

  function createStepEl(name, status) {
    const li = document.createElement("li");
    li.className = `step ${status || "pending"}`;
    li.innerHTML = `
      <span class="step-marker"></span>
      <span class="step-name"></span>
      <span class="step-duration"></span>
    `;
    li.querySelector(".step-name").textContent = name;
    return li;
  }

  function upsertStep(event) {
    const name = event.step_name;
    if (!name) return;

    let li = stepEls.get(name);
    if (!li) {
      li = createStepEl(name, event.status);
      stepEls.set(name, li);
      el.stepList.appendChild(li);
    }

    li.classList.remove("pending", "running", "done", "error");
    li.classList.add(event.status || "pending");

    const durEl = li.querySelector(".step-duration");
    durEl.textContent = formatDuration(event.duration_ms);

    if (event.event_type === "error" || event.status === "error") {
      let errEl = li.querySelector(".step-error");
      if (!errEl) {
        errEl = document.createElement("div");
        errEl.className = "step-error";
        li.appendChild(errEl);
      }
      const msg = event.error_message || "Unknown error";
      const tb  = event.error_traceback ? `\n\n${event.error_traceback}` : "";
      errEl.textContent = `${msg}${tb}`;
    }
  }

  // ---- event handlers ---------------------------------------------------
  function handleEvent(event) {
    switch (event.event_type) {
      case "workflow_start":
        if (event.run_id !== currentRunId) {
          currentRunId = event.run_id;
          resetCard();
        }
        el.workflowName.textContent = event.workflow_name || "Workflow";
        setWorkflowStatus("Running", "running");
        showCard();
        break;

      case "step":
        showCard();
        upsertStep(event);
        break;

      case "error":
        showCard();
        upsertStep(event);
        setWorkflowStatus("Error", "error");
        break;

      case "workflow_done":
        setWorkflowStatus("Done", "done");
        break;

      default:
        console.warn("Unknown event type:", event);
    }
  }

  // ---- WebSocket lifecycle ---------------------------------------------
  let reconnectDelay = 1000;
  const MAX_RECONNECT_DELAY = 15000;

  function connect() {
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
        console.error("Bad event payload:", msg.data, err);
      }
    };

    ws.onclose = () => {
      setConnection("error", "Disconnected — retrying…");
      setTimeout(connect, reconnectDelay);
      reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_DELAY);
    };

    ws.onerror = () => {
      // onclose will handle reconnect.
    };
  }

  connect();
})();
