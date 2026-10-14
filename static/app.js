"use strict";

/* ================================================================ icons */
const ICONS = {
  upload: '<path d="M12 15V3"/><path d="m7 8 5-5 5 5"/><path d="M20 21H4"/>',
  sliders: '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
  folder: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
  file: '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/>',
  fileText: '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/>',
  captions: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 15h4M15 15h2M7 11h2M13 11h4"/>',
  braces: '<path d="M8 3H7a2 2 0 0 0-2 2v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5a2 2 0 0 0 2 2h1M16 3h1a2 2 0 0 1 2 2v5a2 2 0 0 0 2 2 2 2 0 0 0-2 2v5a2 2 0 0 1-2 2h-1"/>',
  audio: '<path d="M2 10v4M6 6v12M10 3v18M14 8v8M18 5v14M22 10v4"/>',
  users: '<circle cx="9" cy="8" r="4"/><path d="M2 21a7 7 0 0 1 14 0"/><path d="M16 4a4 4 0 0 1 0 8"/><path d="M22 21a7 7 0 0 0-4-6.3"/>',
  sparkles: '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 3v4M17 5h4"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  x: '<path d="M18 6 6 18M6 6l12 12"/>',
  refresh: '<path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/>',
  copy: '<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
  pencil: '<path d="M17 3a2.8 2.8 0 0 1 4 4L7.5 20.5 2 22l1.5-5.5z"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
  moon: '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
  monitor: '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>',
  alert: '<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/>',
  listCheck: '<path d="m3 7 2 2 4-4"/><path d="m3 17 2 2 4-4"/><path d="M13 6h8M13 12h8M13 18h8"/>',
  flag: '<path d="M4 22V4"/><path d="M4 4h13l-2 4 2 4H4"/>',
  help: '<circle cx="12" cy="12" r="9"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3"/><path d="M12 17h.01"/>',
  list: '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
  mic: '<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M19 10a7 7 0 0 1-14 0M12 17v4"/>',
  chevron: '<path d="m6 9 6 6 6-6"/>',
  cpu: '<rect x="5" y="5" width="14" height="14" rx="2"/><path d="M9 9h6v6H9zM9 1v4M15 1v4M9 19v4M15 19v4M1 9h4M1 15h4M19 9h4M19 15h4"/>',
  cloud: '<path d="M17.5 19H7a5 5 0 1 1 1-9.9A6 6 0 0 1 19.5 11 4 4 0 0 1 17.5 19z"/>',
  off: '<circle cx="12" cy="12" r="9"/><path d="M5.6 5.6l12.8 12.8"/>',
  globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
  arrowRight: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  lock: '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
  trash: '<path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6M10 11v6M14 11v6"/>',
  hourglass:'<path d="M6 2h12M6 22h12M7 2v4a5 5 0 0 0 10 0V2M7 22v-4a5 5 0 0 1 10 0v4"/>',
};
const icon = (name, cls = "") => `<svg class="i ${cls}" viewBox="0 0 24 24" aria-hidden="true">${ICONS[name] || ""}</svg>`;
const hydrate = (root = document) => root.querySelectorAll("[data-icon]").forEach((el) => {
  if (!el.firstElementChild) el.innerHTML = icon(el.dataset.icon);
});

/* ================================================================ helpers */
const $ = (sel, root = document) => root.querySelector(sel);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (sec) => {
  sec = Math.max(0, Math.floor(sec || 0));
  const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
  return h ? `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}` : `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
};
const humanDur = (sec) => {
  sec = Math.round(sec || 0);
  if (sec < 60) return `${sec}s`;
  const m = Math.round(sec / 60);
  return m < 60 ? `${m} min` : `${Math.floor(m / 60)}h ${m % 60}m`;
};
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* storage unavailable */ } },
};
const SPEAKER_COLORS = ["#7c6cff", "#f2766b", "#1fb5a3", "#eaa23a", "#3b9df7", "#e062ad", "#78b846", "#a5826a", "#8e8e9a"];
const LANGS = { auto: "Auto-detect", en: "English", es: "Spanish", fr: "French", de: "German", it: "Italian", pt: "Portuguese", nl: "Dutch", pl: "Polish", ja: "Japanese", zh: "Chinese", ko: "Korean", hi: "Hindi", ar: "Arabic" };

async function api(path, opts = {}) {
  // X-Minutes marks requests as coming from this page; the server rejects writes without it.
  const init = { ...opts, headers: { "X-Minutes": "1" } };
  if (opts.body && typeof opts.body !== "string" && !(opts.body instanceof FormData)) {
    init.body = JSON.stringify(opts.body);
    init.headers["Content-Type"] = "application/json";
  }
  const res = await fetch(path, init);
  if (!res.ok) {
    let msg = res.statusText;
    try { msg = (await res.json()).detail || msg; } catch { /* not json */ }
    throw new Error(msg);
  }
  return res.json();
}

function toast(text, kind = "ok", ms = 2600) {
  const el = document.createElement("div");
  el.className = `toast ${kind}`;
  el.innerHTML = `${icon(kind === "err" ? "alert" : kind === "info" ? "sparkles" : "check")}<span>${esc(text)}</span>`;
  $("#toasts").appendChild(el);
  setTimeout(() => { el.classList.add("out"); setTimeout(() => el.remove(), 260); }, ms);
}

function confirmDialog({ title, body, confirm }) {
  return new Promise((resolve) => {
    const wrap = document.createElement("div");
    wrap.className = "modal-scrim";
    wrap.innerHTML = `<div class="modal" role="dialog" aria-modal="true">
      <div class="modal-icon">${icon("trash")}</div>
      <h3>${esc(title)}</h3><p>${body}</p>
      <div class="modal-actions"><button class="btn" data-a="0">Cancel</button><button class="btn danger" data-a="1">${esc(confirm)}</button></div></div>`;
    const close = (v) => {
      wrap.classList.add("out");
      document.removeEventListener("keydown", onKey, true);
      setTimeout(() => wrap.remove(), 200);
      resolve(v);
    };
    const onKey = (e) => {
      if (e.key === "Escape") { e.stopPropagation(); close(false); }
      if (e.key === "Enter") { e.preventDefault(); close(true); }
    };
    wrap.onclick = (e) => { if (e.target === wrap) close(false); };
    wrap.querySelectorAll("[data-a]").forEach((b) => (b.onclick = () => close(b.dataset.a === "1")));
    document.addEventListener("keydown", onKey, true);
    document.body.appendChild(wrap);
    wrap.querySelector('[data-a="0"]').focus();
  });
}

/* ================================================================ state */
const state = {
  status: null,
  settings: null,
  jobs: [],
  uploads: new Map(), // temp id -> {name, pct}
  meetings: [],
  meetingsKey: "",
  selected: null,
  meeting: null,
  tab: "summary",
  search: "",
  stageClock: {}, // job id -> {stage, t0}
  seenDone: new Set(),
};

/* ================================================================ theme */
const THEMES = ["system", "light", "dark"];
function applyTheme(t) {
  if (t === "system") delete document.documentElement.dataset.theme;
  else document.documentElement.dataset.theme = t;
  $("#themeBtn").innerHTML = icon(t === "light" ? "sun" : t === "dark" ? "moon" : "monitor");
  $("#themeBtn").title = `Theme: ${t}`;
}
let theme = store.get("theme", "system");
applyTheme(theme);
$("#themeBtn").onclick = () => {
  theme = THEMES[(THEMES.indexOf(theme) + 1) % 3];
  store.set("theme", theme);
  applyTheme(theme);
  toast(`Theme: ${theme}`, "info", 1400);
};

/* ================================================================ status pills */
function renderStatus() {
  const s = state.status;
  if (!s) return;
  const pills = [];
  pills.push({ dot: s.whisper.cached ? "ok" : "warn", label: "Whisper", tip: s.whisper.cached ? `${s.whisper.model} ready` : "Model downloads on first use (~1.6 GB)" });
  if (s.speakers.enabled) {
    pills.push({ dot: s.speakers.ready ? "ok" : "warn", label: "Speakers", tip: s.speakers.ready ? "Speaker detection on" : "Add a Hugging Face token in Settings" });
  } else pills.push({ dot: "", label: "Speakers off", tip: "Speaker detection is off" });
  if (s.engine === "ollama") {
    const dot = !s.ollama.running ? "err" : s.ollama.installed ? "ok" : "warn";
    const tip = !s.ollama.running ? "Ollama isn't running" : s.ollama.installed ? `Ollama · ${s.ollama.model}` : `Model ${s.ollama.model} not installed`;
    pills.push({ dot, label: "Ollama", tip });
  } else if (s.engine === "claude") {
    pills.push({ dot: s.claude.ready ? "ok" : "warn", label: "Claude", tip: s.claude.ready ? s.claude.model : "Add an API key in Settings" });
  } else pills.push({ dot: "", label: "Summary off", tip: "Summaries are off" });
  $("#status").innerHTML = pills.map((p) => `<button class="pill" title="${esc(p.tip)}"><span class="dot ${p.dot}"></span>${esc(p.label)}</button>`).join("");
  $("#status").querySelectorAll(".pill").forEach((b) => (b.onclick = openSettings));
}

/* ================================================================ uploads */
function uploadFiles(files) {
  [...files].forEach((file) => {
    const tmp = "u" + Math.random().toString(36).slice(2, 9);
    state.uploads.set(tmp, { name: file.name, pct: 0 });
    renderQueue();
    const fd = new FormData();
    fd.append("file", file);
    fd.append("last_modified", String(file.lastModified || Date.now()));
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/upload");
    xhr.setRequestHeader("X-Minutes", "1");
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) { state.uploads.get(tmp).pct = e.loaded / e.total; renderQueue(); }
    };
    xhr.onload = () => {
      state.uploads.delete(tmp);
      if (xhr.status >= 200 && xhr.status < 300) {
        state.jobs.push(JSON.parse(xhr.responseText));
      } else toast(`Upload failed: ${file.name}`, "err");
      renderQueue();
      poll(true);
    };
    xhr.onerror = () => { state.uploads.delete(tmp); renderQueue(); toast(`Upload failed: ${file.name}`, "err"); };
    xhr.send(fd);
  });
}
$("#fileInput").onchange = (e) => { uploadFiles(e.target.files); e.target.value = ""; };

let dragDepth = 0;
window.addEventListener("dragenter", (e) => { if (e.dataTransfer?.types.includes("Files")) { dragDepth++; $("#dragover").classList.add("on"); } });
window.addEventListener("dragleave", () => { dragDepth = Math.max(0, dragDepth - 1); if (!dragDepth) $("#dragover").classList.remove("on"); });
window.addEventListener("dragover", (e) => e.preventDefault());
window.addEventListener("drop", (e) => {
  e.preventDefault(); dragDepth = 0; $("#dragover").classList.remove("on");
  if (e.dataTransfer?.files?.length) uploadFiles(e.dataTransfer.files);
});

/* ================================================================ queue */
const STAGE_LABEL = { audio: "Audio", transcribe: "Transcribe", speakers: "Speakers", summary: "Summary", save: "Save" };
const jobEls = new Map();

function jobCard(id) {
  let el = jobEls.get(id);
  if (!el) {
    el = document.createElement("div");
    el.className = "job";
    el.innerHTML = `<div class="job-head"><span class="job-state"></span><span class="job-name"></span><button class="icon-btn job-x"></button></div>
      <div class="steps"></div><div class="job-meta"><span class="msg"></span><span class="pct"></span></div><div class="job-extra"></div>`;
    jobEls.set(id, el);
  }
  return el;
}

function renderQueue() {
  const container = $("#queue");
  const live = new Set();
  let any = false;

  for (const [id, u] of state.uploads) {
    any = true; live.add(id);
    const el = jobCard(id);
    $(".job-state", el).innerHTML = '<span class="spinner"></span>';
    $(".job-name", el).textContent = u.name;
    $(".job-x", el).hidden = true;
    $(".steps", el).innerHTML = `<div class="step active" style="flex:5"><b style="width:${u.pct * 100}%"></b></div>`;
    $(".msg", el).textContent = "Uploading…";
    $(".pct", el).textContent = `${Math.round(u.pct * 100)}%`;
    if (!el.isConnected) container.appendChild(el);
  }

  for (const job of state.jobs) {
    any = true; live.add(job.id);
    const el = jobCard(job.id);
    el.classList.toggle("done", job.status === "done");
    const running = job.status === "running";
    $(".job-state", el).innerHTML =
      job.status === "done" ? `<span class="check">${icon("check")}</span>` :
      job.status === "error" ? `<span class="queued-dot" style="color:var(--err)">${icon("alert")}</span>` :
      job.status === "cancelled" ? `<span class="queued-dot">${icon("off")}</span>` :
      running ? '<span class="spinner"></span>' : `<span class="queued-dot">${icon("hourglass")}</span>`;
    if ($(".job-state", el).dataset.s !== job.status) $(".job-state", el).dataset.s = job.status;
    $(".job-name", el).textContent = job.kind === "summarize" ? `Summary · ${job.filename}` : job.filename;
    const x = $(".job-x", el);
    x.hidden = false;
    x.innerHTML = icon("x");
    x.title = job.status === "queued" || running ? "Cancel" : "Dismiss";
    x.onclick = async (e) => {
      e.stopPropagation();
      if (job.status === "queued" || running) { await api(`/api/jobs/${job.id}/cancel`, { method: "POST" }); toast("Cancelled", "info"); }
      else { await api(`/api/jobs/${job.id}`, { method: "DELETE" }); }
      poll(true);
    };

    // stepper
    const cur = job.stages.indexOf(job.stage);
    $(".steps", el).innerHTML = job.stages.map((st, i) => {
      let cls = "step", w = 0;
      if (job.skipped.includes(st)) cls += " skip";
      else if (job.status === "done" || (cur > -1 && i < cur)) { cls += " done"; w = 100; }
      else if (i === cur && running) {
        cls += " active"; w = job.stage_progress * 100;
        if (st === "summary" && job.stage_progress < 0.05) cls += " indeterminate";
      }
      return `<div class="${cls}" title="${STAGE_LABEL[st]}"><b style="width:${w}%"></b></div>`;
    }).join("");

    // message + eta
    let msg = job.message || "", pct = "";
    if (job.status === "queued") msg = "Waiting in queue…";
    if (job.status === "done") msg = job.kind === "summarize" ? "Summary updated" : "Done · click to open";
    if (job.status === "cancelled") msg = "Cancelled";
    if (job.status === "error") msg = `Failed during ${STAGE_LABEL[job.stage] || "processing"}`;
    if (running) {
      const clock = state.stageClock[job.id];
      if (!clock || clock.stage !== job.stage) state.stageClock[job.id] = { stage: job.stage, t0: Date.now() };
      const p = job.stage_progress;
      if (job.stage === "transcribe" && p > 0.03) {
        const el2 = (Date.now() - state.stageClock[job.id].t0) / 1000;
        const left = (el2 * (1 - p)) / p;
        pct = `${Math.round(p * 100)}% · ~${humanDur(left)} left`;
      } else if (p > 0 && p < 1 && job.stage !== "summary") pct = `${Math.round(p * 100)}%`;
    }
    $(".msg", el).textContent = msg;
    $(".pct", el).textContent = pct;

    let extra = "";
    if (running && job.preview) extra += `<div class="job-preview">“${esc(job.preview)}”</div>`;
    if (job.error) extra += `<div class="job-error">${esc(job.error)}</div>`;
    for (const w of job.warnings) extra += `<div class="job-warn">${icon("alert")}<span>${esc(w)}</span></div>`;
    const ex = $(".job-extra", el);
    if (ex.dataset.html !== extra) { ex.innerHTML = extra; ex.dataset.html = extra; }

    el.onclick = job.status === "done" && job.meeting_id ? () => select(job.meeting_id) : null;
    if (!el.isConnected) container.appendChild(el);
  }

  for (const [id, el] of jobEls) if (!live.has(id)) { el.remove(); jobEls.delete(id); }
  $("#queueSection").hidden = !any;
  const busy = state.uploads.size > 0 || state.jobs.some((j) => j.status === "running");
  $("#logo").classList.toggle("busy", busy);
  document.title = busy ? "Working… · Minutes" : "Minutes";
}

/* ================================================================ history */
function renderHistory() {
  const box = $("#history");
  if (!state.meetings.length) {
    box.innerHTML = `<div class="empty-list">No meetings yet</div>`;
    return;
  }
  box.innerHTML = state.meetings.map((m, i) => {
    const d = m.meeting_date ? new Date(m.meeting_date + "T12:00:00") : null;
    const label = m.title || m.name;
    return `<button class="meeting-row ${m.id === state.selected ? "active" : ""}" data-id="${m.id}" style="animation-delay:${Math.min(i, 12) * 25}ms">
      <span class="m-badge"><b>${d ? d.getDate() : "–"}</b><small>${d ? d.toLocaleString(undefined, { month: "short" }) : ""}</small></span>
      <span class="m-body"><div class="m-title">${esc(label)}</div>
        <div class="m-sub"><span>${icon("clock")}${humanDur(m.duration)}</span>${m.speakers ? `<span>${icon("users")}${m.speakers}</span>` : ""}${m.action_items ? `<span>${icon("listCheck")}${m.action_items}</span>` : ""}</div>
      </span></button>`;
  }).join("");
  box.querySelectorAll(".meeting-row").forEach((b) => (b.onclick = () => select(b.dataset.id)));
}

async function loadMeetings() {
  const list = await api("/api/meetings");
  const key = JSON.stringify(list);
  if (key !== state.meetingsKey) {
    state.meetings = list; state.meetingsKey = key;
    renderHistory();
  }
}

/* ================================================================ detail */
async function select(id, keepTab = false) {
  state.selected = id;
  if (!keepTab) { state.tab = "summary"; state.search = ""; }
  renderHistory();
  try {
    state.meeting = await api(`/api/meetings/${id}`);
  } catch (e) {
    // e.g. deleted in Explorer, or from a job card whose meeting is gone
    toast(e.message === "Meeting not found" ? "That meeting no longer exists" : e.message, "err");
    state.selected = null; state.meeting = null;
    await loadMeetings(); renderHistory();
  }
  renderDetail();
}

function renderHero() {
  const bars = Array.from({ length: 28 }, (_, i) => {
    const h = 20 + Math.round(80 * Math.abs(Math.sin(i * 0.9) * Math.cos(i * 0.31)));
    return `<i style="height:${h}%;animation-delay:${-(i * 0.17).toFixed(2)}s"></i>`;
  }).join("");
  $("#detail").innerHTML = `<div class="hero"><div class="hero-inner">
    <div class="hero-art">${bars}</div>
    <h1>Turn meetings into minutes</h1>
    <p>Drop a recording anywhere on this window. Transcription and speaker detection run entirely on this computer.</p>
    <label class="btn accent" for="fileInput">${icon("upload")}Choose a recording</label>
    <div class="flow"><span>${icon("file")}MP4</span><span class="arrow">${icon("arrowRight")}</span><span>${icon("mic")}Transcript</span><span class="arrow">${icon("arrowRight")}</span><span>${icon("users")}Speakers</span><span class="arrow">${icon("arrowRight")}</span><span>${icon("sparkles")}Summary</span></div>
  </div></div>`;
}

function speakerColor(m, label) {
  const labels = Object.keys(m.speakers || {});
  const i = labels.indexOf(label);
  return SPEAKER_COLORS[(i < 0 ? labels.length : i) % SPEAKER_COLORS.length];
}
const displayName = (m, label) => (label ? (m.speakers || {})[label] || label : null);

function fileNamesFor(name) {
  return [`${name}_transcript.txt`, `${name}_summary.md`, `${name}.srt`, `${name}.json`];
}

function renderDetail() {
  const m = state.meeting;
  if (!m) return renderHero();
  const speakerCount = new Set(Object.values(m.speakers || {})).size;
  const busy = state.jobs.some((j) => j.meeting_id === m.id && j.kind === "summarize" && ["queued", "running"].includes(j.status));
  $("#detail").innerHTML = `<div class="detail-inner">
    <div class="d-eyebrow">
      <span>${icon("calendar")}${esc(new Date(m.meeting_date + "T12:00:00").toLocaleDateString(undefined, { weekday: "short", month: "long", day: "numeric", year: "numeric" }))}</span>
      <span>${icon("clock")}${fmt(m.duration)}</span>
      ${speakerCount ? `<span>${icon("users")}${speakerCount} speaker${speakerCount > 1 ? "s" : ""}</span>` : ""}
      <span>${icon("globe")}${esc(LANGS[m.language] || (m.language || "").toUpperCase())}</span>
    </div>
    <div class="name-row"><input class="name-input" id="nameInput" value="${esc(m.name)}" spellcheck="false" title="Click to rename"></div>
    <div class="name-hint" id="nameHint">${icon("pencil")}<span>Click the name to rename the folder and every file</span></div>
    <div class="actions">
      <button class="btn" id="openBtn">${icon("folder")}Open folder</button>
      <div class="split"><button class="btn" id="resumBtn" ${busy ? "disabled" : ""}>${icon(busy ? "hourglass" : "sparkles")}${busy ? "Summarizing…" : m.summary ? "Re-summarize" : "Summarize"}${icon("chevron")}</button></div>
      ${m.summary ? `<button class="btn" id="copyBtn">${icon("copy")}Copy summary</button>` : ""}
      <button class="btn danger-ghost" id="deleteBtn" title="Move to Recycle Bin">${icon("trash")}Delete</button>
    </div>
    <nav class="tabs" id="tabs">
      <button class="tab" data-tab="summary">${icon("sparkles")}Summary</button>
      <button class="tab" data-tab="transcript">${icon("fileText")}Transcript<span class="count">${m.segments.length}</span></button>
      <button class="tab" data-tab="speakers">${icon("users")}Speakers${speakerCount ? `<span class="count">${speakerCount}</span>` : ""}</button>
      <button class="tab" data-tab="files">${icon("folder")}Files<span class="count">${(m.files || []).length}</span></button>
      <span class="tab-ink" id="tabInk"></span>
    </nav>
    <div id="panel"></div>
  </div>`;

  // rename
  const input = $("#nameInput"), hint = $("#nameHint");
  input.oninput = () => {
    const v = input.value.trim();
    hint.innerHTML = v && v !== m.name
      ? `${icon("fileText")}<span>Will save as <b>${esc(fileNamesFor(v)[0])}</b>, <b>${esc(fileNamesFor(v)[1])}</b>… · Enter to apply, Esc to cancel</span>`
      : `${icon("pencil")}<span>Click the name to rename the folder and every file</span>`;
  };
  input.onkeydown = (e) => {
    if (e.key === "Enter") input.blur();
    if (e.key === "Escape") { input.value = m.name; input.oninput(); input.blur(); }
  };
  input.onblur = async () => {
    const v = input.value.trim();
    if (!v || v === m.name) { input.value = m.name; input.oninput(); return; }
    try {
      state.meeting = await api(`/api/meetings/${m.id}`, { method: "POST", body: { name: v } });
      toast("Renamed folder and files");
      await loadMeetings();
      renderDetail();
    } catch (e) { toast(e.message, "err"); input.value = m.name; input.oninput(); }
  };

  $("#openBtn").onclick = () => api(`/api/meetings/${m.id}/open`, { method: "POST" }).catch((e) => toast(e.message, "err"));
  $("#resumBtn").onclick = (e) => { e.stopPropagation(); summaryMenu($("#resumBtn").parentElement, m); };
  if ($("#copyBtn")) $("#copyBtn").onclick = async () => {
    try { await navigator.clipboard.writeText(summaryMarkdown(m)); toast("Summary copied"); }
    catch { toast("Couldn't access the clipboard", "err"); }
  };

  $("#deleteBtn").onclick = async () => {
    const ok = await confirmDialog({
      title: "Delete this meeting?",
      body: `<b>${esc(m.name)}</b> and its ${(m.files || []).length} files will be moved to the Recycle Bin. You can restore them from there.`,
      confirm: "Move to Recycle Bin",
    });
    if (!ok) return;
    try {
      await api(`/api/meetings/${m.id}`, { method: "DELETE" });
      toast("Moved to Recycle Bin");
      state.selected = null; state.meeting = null;
      await loadMeetings();
      renderHistory(); renderDetail();
    } catch (e) { toast(e.message, "err", 5000); }
  };

  document.querySelectorAll(".tab").forEach((t) => (t.onclick = () => { state.tab = t.dataset.tab; renderPanel(); }));
  renderPanel();
}

function moveInk() {
  const active = $(`.tab[data-tab="${state.tab}"]`), ink = $("#tabInk");
  if (!active || !ink) return;
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t === active));
  ink.style.left = active.offsetLeft + "px";
  ink.style.width = active.offsetWidth + "px";
}

function renderPanel() {
  moveInk();
  const m = state.meeting, panel = $("#panel");
  panel.className = "panel";
  void panel.offsetWidth; // restart fade
  ({ summary: panelSummary, transcript: panelTranscript, speakers: panelSpeakers, files: panelFiles })[state.tab](panel, m);
}

/* ---------------- summary */
function summaryMenu(anchor, m) {
  document.querySelectorAll(".menu").forEach((x) => x.remove());
  const s = state.status;
  const menu = document.createElement("div");
  menu.className = "menu";
  const ollamaOk = s?.ollama.running;
  const claudeOk = s?.claude.ready;
  menu.innerHTML = `
    <button data-e="ollama" ${ollamaOk ? "" : "disabled"}>${icon("cpu")}<span>Ollama · local<small>${esc(ollamaOk ? s.ollama.model : "Not running")}</small></span></button>
    <button data-e="claude" ${claudeOk ? "" : "disabled"}>${icon("cloud")}<span>Claude<small>${esc(claudeOk ? s.claude.model : "Add an API key in Settings")}</small></span></button>`;
  anchor.appendChild(menu);
  menu.querySelectorAll("button").forEach((b) => (b.onclick = async (e) => {
    e.stopPropagation(); menu.remove();
    try {
      const job = await api(`/api/meetings/${m.id}/summarize`, { method: "POST", body: { engine: b.dataset.e } });
      state.jobs.push(job); renderQueue(); renderDetail();
      toast(`Summarizing with ${b.dataset.e === "claude" ? "Claude" : "Ollama"}…`, "info");
      poll(true);
    } catch (err) { toast(err.message, "err"); }
  }));
  setTimeout(() => document.addEventListener("click", () => menu.remove(), { once: true }), 0);
}

function summaryMarkdown(m) {
  const s = m.summary; if (!s) return "";
  const L = [`# ${s.title || m.name}`, "", s.overview, ""];
  if (s.decisions.length) L.push("## Decisions", ...s.decisions.map((d) => `- ${d}`), "");
  if (s.action_items.length) L.push("## Action items", ...s.action_items.map((a) => `- [ ] ${a.task}${a.owner ? ` — ${a.owner}` : ""}${a.due ? ` (due ${a.due})` : ""}`), "");
  if (s.open_questions.length) L.push("## Open questions", ...s.open_questions.map((q) => `- ${q}`), "");
  if (s.topics.length) L.push("## Topics", ...s.topics.map((t) => `- ${fmt(t.start)} ${t.topic}`), "");
  return L.join("\n");
}

function panelSummary(panel, m) {
  const s = m.summary;
  if (!s) {
    panel.innerHTML = `<div class="blank"><div class="big">${icon("sparkles")}</div><strong>No summary yet</strong>
      <p>${state.status?.engine === "none" ? "Summaries are turned off in Settings." : "The summary engine wasn't available when this was processed."}</p>
      <button class="btn accent" id="genBtn">${icon("sparkles")}Generate summary</button></div>`;
    $("#genBtn").onclick = (e) => { e.stopPropagation(); summaryMenu($("#genBtn").parentElement, m); };
    return;
  }
  const done = new Set(store.get(`todos:${m.id}`, []));
  const card = (cls, ic, title, n, body, delay) =>
    `<div class="card ${cls}" style="animation-delay:${delay}ms"><h4><span class="ic">${icon(ic)}</span>${title}<span class="n">${n || ""}</span></h4>${body}</div>`;
  const list = (items, fn) => (items.length ? `<ul>${items.map(fn).join("")}</ul>` : `<div class="none">None noted</div>`);

  panel.innerHTML = `
    <p class="overview">${esc(s.overview)}</p>
    <div class="summary-grid">
      ${card("wide", "listCheck", "Action items", s.action_items.length, list(s.action_items, (a, i) => `
        <li class="${done.has(i) ? "done" : ""}"><button class="todo ${done.has(i) ? "on" : ""}" data-i="${i}" aria-label="Mark done">${icon("check")}</button>
        <span><span class="t">${esc(a.task)}</span><span class="chips">${a.owner ? `<span class="chip owner">${icon("user")}${esc(a.owner)}</span>` : ""}${a.due ? `<span class="chip">${icon("calendar")}${esc(a.due)}</span>` : ""}</span></span></li>`), 0)}
      ${card("", "flag", "Decisions", s.decisions.length, list(s.decisions, (d) => `<li><span class="bullet"></span><span>${esc(d)}</span></li>`), 60)}
      ${card("", "help", "Open questions", s.open_questions.length, list(s.open_questions, (q) => `<li><span class="bullet"></span><span>${esc(q)}</span></li>`), 120)}
      ${card("wide timeline", "list", "Topics", s.topics.length, list(s.topics, (t) => `<li data-t="${t.start}"><span class="ts">${fmt(t.start)}</span><span>${esc(t.topic)}</span></li>`), 180)}
    </div>
    <div class="summary-foot">${icon(String(m.summary_engine || "").startsWith("Claude") ? "cloud" : "cpu")}Summary by ${esc(m.summary_engine || "AI")} · always double-check against the transcript</div>`;

  panel.querySelectorAll(".todo").forEach((b) => (b.onclick = () => {
    const i = +b.dataset.i;
    done.has(i) ? done.delete(i) : done.add(i);
    store.set(`todos:${m.id}`, [...done]);
    b.classList.toggle("on"); b.closest("li").classList.toggle("done");
  }));
  panel.querySelectorAll(".timeline li").forEach((li) => (li.onclick = () => jumpTo(+li.dataset.t)));
}

/* ---------------- transcript */
function groupSegments(m) {
  const blocks = [];
  for (const seg of m.segments) {
    const last = blocks[blocks.length - 1];
    if (last && last.speaker === seg.speaker && seg.start - last.end < 30 && last.texts.length < 8) {
      last.texts.push(seg.text); last.end = seg.end;
    } else blocks.push({ speaker: seg.speaker, start: seg.start, end: seg.end, texts: [seg.text] });
  }
  return blocks;
}

function panelTranscript(panel, m) {
  const blocks = groupSegments(m);
  panel.innerHTML = `<div class="t-tools"><label class="search">${icon("search")}<input id="tSearch" placeholder="Search transcript" value="${esc(state.search)}"><span class="hits" id="hits"></span></label>
    <button class="btn" id="copyT">${icon("copy")}Copy</button></div><div id="tBody"></div>`;
  const body = $("#tBody");
  const draw = () => {
    const q = state.search.trim();
    const re = q ? new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi") : null;
    let hits = 0;
    const html = blocks.map((b) => {
      const text = b.texts.join(" ");
      if (re) { const n = (text.match(re) || []).length; if (!n) return ""; hits += n; }
      const who = displayName(m, b.speaker);
      const body = b.texts.map((t) => { let h = esc(t); if (re) h = h.replace(new RegExp(esc(q).replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi"), (x) => `<mark>${x}</mark>`); return h; }).join(" ");
      return `<div class="utt" data-start="${b.start}"><div class="when">${fmt(b.start)}</div><div>
        ${who ? `<div class="who"><i style="background:${speakerColor(m, b.speaker)}"></i>${esc(who)}</div>` : ""}<div class="txt">${body}</div></div></div>`;
    }).join("");
    body.innerHTML = html || `<div class="none" style="padding:20px 0">No matches</div>`;
    $("#hits").textContent = re ? `${hits} match${hits === 1 ? "" : "es"}` : "";
  };
  draw();
  $("#tSearch").oninput = (e) => { state.search = e.target.value; draw(); };
  $("#copyT").onclick = async () => {
    const txt = blocks.map((b) => `[${fmt(b.start)}] ${displayName(m, b.speaker) ? displayName(m, b.speaker) + ": " : ""}${b.texts.join(" ")}`).join("\n\n");
    try { await navigator.clipboard.writeText(txt); toast("Transcript copied"); } catch { toast("Couldn't access the clipboard", "err"); }
  };
}

function jumpTo(t) {
  state.tab = "transcript"; state.search = "";
  renderPanel();
  const utts = [...document.querySelectorAll(".utt")];
  let target = utts[0];
  for (const u of utts) if (+u.dataset.start <= t + 0.5) target = u;
  if (!target) return;
  target.scrollIntoView({ behavior: "smooth", block: "center" });
  target.classList.add("flash");
  setTimeout(() => target.classList.remove("flash"), 1600);
}

/* ---------------- speakers */
function panelSpeakers(panel, m) {
  const labels = Object.keys(m.speakers || {});
  if (!labels.length) {
    panel.innerHTML = `<div class="blank"><div class="big">${icon("users")}</div><strong>No speaker labels</strong>
      <p>Turn on speaker detection in Settings (needs a free Hugging Face token), then process the recording again.</p>
      <button class="btn" id="goSettings">${icon("sliders")}Open settings</button></div>`;
    $("#goSettings").onclick = openSettings;
    return;
  }
  const talk = {}, quote = {};
  for (const s of m.segments) {
    if (!s.speaker) continue;
    talk[s.speaker] = (talk[s.speaker] || 0) + (s.end - s.start);
    if (!quote[s.speaker] || (s.text.length > quote[s.speaker].length && s.text.length < 160)) quote[s.speaker] = s.text;
  }
  const total = Object.values(talk).reduce((a, b) => a + b, 0) || 1;
  panel.innerHTML = `<div class="spk-list">${labels.map((l, i) => {
    const name = m.speakers[l];
    const initials = name.split(/\s+/).filter(Boolean).map((w) => w[0]).join("").slice(0, 2).toUpperCase();
    const pct = Math.round((100 * (talk[l] || 0)) / total);
    return `<div class="spk" style="animation-delay:${i * 50}ms"><div class="avatar" style="background:${speakerColor(m, l)}">${esc(/^Speaker \d+$/.test(name) ? name.split(" ")[1] : initials)}</div>
      <div><input data-l="${esc(l)}" value="${esc(name)}" placeholder="${esc(l)}" spellcheck="false"><div class="quote">“${esc(quote[l] || "")}”</div></div>
      <div class="talk">${pct}% · ${humanDur(talk[l])}<div class="bar"><b style="width:0;background:${speakerColor(m, l)}" data-w="${pct}"></b></div></div></div>`;
  }).join("")}</div>
  <div class="spk-actions"><span class="none" style="margin-right:auto;align-self:center">Names update the transcript, summary and every saved file.</span>
  <button class="btn accent" id="saveSpk" disabled>${icon("check")}Save names</button></div>`;
  requestAnimationFrame(() => panel.querySelectorAll(".bar b").forEach((b) => (b.style.width = b.dataset.w + "%")));
  const inputs = [...panel.querySelectorAll(".spk input")];
  const dirty = () => inputs.some((x) => x.value.trim() !== m.speakers[x.dataset.l]);
  inputs.forEach((x) => {
    x.oninput = () => ($("#saveSpk").disabled = !dirty());
    x.onkeydown = (e) => { if (e.key === "Enter" && dirty()) $("#saveSpk").click(); };
  });
  $("#saveSpk").onclick = async () => {
    const speakers = Object.fromEntries(inputs.map((x) => [x.dataset.l, x.value.trim() || x.dataset.l]));
    try {
      state.meeting = await api(`/api/meetings/${m.id}`, { method: "POST", body: { speakers } });
      toast("Speaker names saved");
      await loadMeetings();
      renderDetail();
    } catch (e) { toast(e.message, "err"); }
  };
}

/* ---------------- files */
function panelFiles(panel, m) {
  const describe = (f) =>
    f.endsWith("_transcript.txt") ? ["fileText", "Readable transcript with timestamps"] :
    f.endsWith("_summary.md") ? ["sparkles", "Summary (Markdown)"] :
    f.endsWith(".srt") ? ["captions", "Subtitles for video players"] :
    f.endsWith(".json") ? ["braces", "Full data (also used by Minutes)"] :
    f.endsWith(".wav") ? ["audio", "16 kHz mono audio"] : ["file", ""];
  panel.innerHTML = `<div class="folder-line">${icon("folder")}${esc(m.folder)}</div><div class="files">${(m.files || []).map((f, i) => {
    const [ic, d] = describe(f);
    return `<div class="file" style="animation-delay:${i * 40}ms"><span class="fi">${icon(ic)}</span><span class="fn" title="${esc(f)}">${esc(f)}</span><span class="fd">${d}</span></div>`;
  }).join("")}</div>
  <div class="callout" style="margin-top:16px">${icon("pencil")}<span>Rename the meeting at the top of the page and the folder and every file are renamed to match.</span></div>`;
}

/* ================================================================ settings drawer */
function openSettings() {
  renderSettings();
  $("#drawer").classList.add("open");
  $("#scrim").classList.add("open");
}
function closeSettings() {
  $("#drawer").classList.remove("open");
  $("#scrim").classList.remove("open");
}
$("#settingsBtn").onclick = openSettings;
$("#scrim").onclick = closeSettings;
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeSettings(); });

let saveTimer = null;
async function saveSetting(patch, quiet = false) {
  try {
    state.settings = await api("/api/settings", { method: "POST", body: patch });
    if (!quiet) toast("Saved", "ok", 1200);
    refreshStatus().then(() => { if ($("#drawer").classList.contains("open")) renderSettings(true); });
  } catch (e) { toast(e.message, "err"); }
}

function renderSettings(keepScroll = false) {
  const s = state.settings, st = state.status;
  if (!s || !st) return;
  const scroll = $(".drawer-body")?.scrollTop || 0;
  const opt = (v, label, cur) => `<option value="${esc(v)}" ${String(v) === String(cur) ? "selected" : ""}>${esc(label)}</option>`;
  const ollamaModels = [...new Set([...(st.ollama.models || []), s.ollama_model])];
  const engines = [["ollama", "cpu", "Ollama"], ["claude", "cloud", "Claude"], ["none", "off", "Off"]];

  $("#drawer").innerHTML = `<div class="drawer-head"><h2>Settings</h2><button class="icon-btn" id="closeDrawer">${icon("x")}</button></div>
  <div class="drawer-body">
    <div class="group"><h3>${icon("mic")}Transcription</h3>
      <div class="row">
        <div class="field"><label>Whisper model</label><select class="select" data-k="whisper_model">
          ${opt("large-v3-turbo", "large-v3-turbo · recommended", s.whisper_model)}${opt("large-v3", "large-v3 · most accurate, slow", s.whisper_model)}
          ${opt("medium", "medium", s.whisper_model)}${opt("small", "small · fast drafts", s.whisper_model)}${opt("base", "base · fastest", s.whisper_model)}</select></div>
        <div class="field"><label>Language</label><select class="select" data-k="language">${Object.entries(LANGS).map(([k, v]) => opt(k, v, s.language)).join("")}</select></div>
      </div>
      <div class="field"><label>Vocabulary</label><textarea class="textarea" data-k="vocabulary" placeholder="Names, products and acronyms, e.g. Priya, Kubernetes, EcoRouter, OKRs">${esc(s.vocabulary)}</textarea>
        <div class="help">Helps Whisper spell names and jargon correctly.</div></div>
      <div class="field"><label>CPU threads</label><input class="input" type="number" min="0" max="64" data-k="cpu_threads" value="${s.cpu_threads}">
        <div class="help">0 = automatic (one per physical core).</div></div>
    </div>

    <div class="group"><h3>${icon("users")}Speakers</h3>
      <label class="toggle field"><span class="tl">Identify who's speaking<small>Runs pyannote locally after transcription</small></span><input type="checkbox" data-k="diarization" ${s.diarization ? "checked" : ""}><span class="switch"></span></label>
      <div class="row">
        <div class="field" style="flex:2"><label>Hugging Face token</label><input class="input" type="password" data-k="hf_token" data-secret placeholder="${s.hf_token ? esc(s.hf_token) : "hf_…"}" autocomplete="off"></div>
        <div class="field"><label>Speakers</label><select class="select" data-k="num_speakers">${opt(0, "Auto", s.num_speakers)}${[2, 3, 4, 5, 6, 7, 8, 10].map((n) => opt(n, n, s.num_speakers)).join("")}</select></div>
      </div>
      ${s.diarization && !s.hf_token ? `<div class="callout warn">${icon("alert")}<span>Needs a free token: accept the terms on
        <a href="https://huggingface.co/pyannote/speaker-diarization-3.1" target="_blank" rel="noreferrer">speaker-diarization-3.1</a> and
        <a href="https://huggingface.co/pyannote/segmentation-3.0" target="_blank" rel="noreferrer">segmentation-3.0</a>, then create a read token at
        <a href="https://huggingface.co/settings/tokens" target="_blank" rel="noreferrer">huggingface.co/settings/tokens</a>.</span></div>` : ""}
    </div>

    <div class="group"><h3>${icon("sparkles")}Summary</h3>
      <div class="field"><div class="seg" id="engineSeg"><span class="seg-ink"></span>${engines.map(([k, ic, l]) => `<button data-v="${k}" class="${s.summary_engine === k ? "on" : ""}">${icon(ic)}${l}</button>`).join("")}</div></div>
      ${s.summary_engine === "ollama" ? `
        <div class="field"><label>Ollama model</label>
          ${st.ollama.running && st.ollama.models.length
            ? `<select class="select" data-k="ollama_model">${ollamaModels.map((x) => opt(x, x, s.ollama_model)).join("")}</select>`
            : `<input class="input" data-k="ollama_model" value="${esc(s.ollama_model)}">`}
          <div class="help">Runs on this computer. Nothing leaves your machine.</div></div>
        ${!st.ollama.running ? `<div class="callout warn">${icon("alert")}<span>Ollama isn't running. Install it from <a href="https://ollama.com/download" target="_blank" rel="noreferrer">ollama.com</a>, then run <code>ollama pull ${esc(s.ollama_model)}</code>.</span></div>`
          : !st.ollama.installed ? `<div class="callout warn">${icon("alert")}<span>Model not installed. Run <code>ollama pull ${esc(s.ollama_model)}</code> in a terminal.</span></div>` : ""}
      ` : ""}
      ${s.summary_engine === "claude" ? `
        <div class="field"><label>Claude model</label><select class="select" data-k="claude_model">
          ${opt("claude-opus-5-5", "Claude Opus 5.5 · best quality", s.claude_model)}${opt("claude-sonnet-5-5", "Claude Sonnet 5.5 · faster, cheaper", s.claude_model)}${opt("claude-haiku-5-5", "Claude Haiku 5.5 · cheapest", s.claude_model)}</select></div>
        <div class="field"><label>Anthropic API key</label><input class="input" type="password" data-k="anthropic_api_key" data-secret placeholder="${s.anthropic_api_key ? esc(s.anthropic_api_key) : "sk-ant-…"}" autocomplete="off"></div>
        <div class="field"><label>Workspace ID <span style="color:var(--faint);font-weight:400">· optional</span></label><input class="input" data-k="anthropic_workspace_id" value="${esc(s.anthropic_workspace_id || "")}" placeholder="wrkspc_…" spellcheck="false" autocomplete="off">
          <div class="help">Only needed if your key isn't scoped to a workspace. Find it in the Anthropic console under Workspaces.</div></div>
        <div class="callout">${icon("cloud")}<span>The transcript text (not the audio) is sent to Anthropic for the summary. Transcription and speakers still run locally.</span></div>
      ` : ""}
      ${s.summary_engine !== "none" ? `<div class="help" style="margin-top:8px">You can switch engines for any meeting with “Re-summarize”.</div>` : ""}
    </div>

    <div class="group"><h3>${icon("folder")}Output</h3>
      <div class="field"><label>Save meetings to</label><div class="row" style="gap:8px"><input class="input" data-k="output_dir" value="${esc(s.output_dir)}" style="flex:1"><button class="btn" id="openOut" style="flex:none">${icon("folder")}</button></div>
        <div class="help">Each meeting gets its own folder, named like <code style="font-family:var(--mono)">2026-10-14_Q4-Budget-Review</code>.</div></div>
      <label class="toggle field"><span class="tl">Keep a WAV copy<small>16 kHz mono, saved next to the transcript</small></span><input type="checkbox" data-k="keep_wav" ${s.keep_wav ? "checked" : ""}><span class="switch"></span></label>
    </div>
    <div class="callout">${icon("lock")}<span>Keys are stored only in <code>data/settings.json</code> on this computer.</span></div>
  </div>`;

  const body = $(".drawer-body");
  if (keepScroll) body.scrollTop = scroll;
  $("#closeDrawer").onclick = closeSettings;
  $("#openOut").onclick = () => api("/api/open-output", { method: "POST" });

  body.querySelectorAll("[data-k]").forEach((el) => {
    const k = el.dataset.k;
    const value = () => el.type === "checkbox" ? el.checked : el.type === "number" || k === "num_speakers" ? Number(el.value) : el.value;
    if (el.tagName === "SELECT" || el.type === "checkbox") el.onchange = () => saveSetting({ [k]: value() });
    else if (el.dataset.secret !== undefined) el.onchange = () => { if (el.value.trim()) saveSetting({ [k]: el.value.trim() }); };
    else el.oninput = () => { clearTimeout(saveTimer); saveTimer = setTimeout(() => saveSetting({ [k]: value() }, true), 600); };
  });

  const seg = $("#engineSeg"), ink = $(".seg-ink", seg);
  const placeInk = () => { const on = $("button.on", seg); if (on) { ink.style.left = on.offsetLeft + "px"; ink.style.width = on.offsetWidth + "px"; } };
  requestAnimationFrame(placeInk);
  seg.querySelectorAll("button").forEach((b) => (b.onclick = () => {
    seg.querySelectorAll("button").forEach((x) => x.classList.toggle("on", x === b));
    placeInk();
    setTimeout(() => saveSetting({ summary_engine: b.dataset.v }), 220);
  }));
}

/* ================================================================ polling */
async function refreshStatus() {
  try { state.status = await api("/api/status"); renderStatus(); } catch { /* server restarting */ }
}

let pollTimer = null;
async function poll(now = false) {
  clearTimeout(pollTimer);
  try {
    const jobs = await api("/api/jobs");
    if (!state.primed) {
      // Jobs that finished before this page loaded were already announced; don't
      // re-toast them or jump to their meeting on every reload.
      state.primed = true;
      for (const j of jobs) if (["done", "error", "cancelled"].includes(j.status)) state.seenDone.add(j.id);
    }
    for (const j of jobs) {
      if (j.status === "done" && !state.seenDone.has(j.id)) {
        state.seenDone.add(j.id);
        await loadMeetings();
        if (j.kind === "process") {
          toast(j.warnings.length ? "Done, with warnings" : "Meeting ready", j.warnings.length ? "info" : "ok");
          if (!state.selected) select(j.meeting_id);
          // done cards clear themselves after a moment; the meeting is in the list
          if (!j.warnings.length) setTimeout(() => api(`/api/jobs/${j.id}`, { method: "DELETE" }).then(() => poll(true)), 9000);
        } else {
          toast("Summary updated");
          if (state.selected === j.meeting_id) select(j.meeting_id, true);
          setTimeout(() => api(`/api/jobs/${j.id}`, { method: "DELETE" }).then(() => poll(true)), 5000);
        }
      }
      if (j.status === "error" && !state.seenDone.has(j.id)) {
        state.seenDone.add(j.id);
        toast(j.error || "Something went wrong", "err", 5000);
        if (j.kind === "summarize" && state.selected === j.meeting_id) renderDetail();
      }
    }
    const wasBusy = state.jobs.some((j) => j.kind === "summarize" && ["queued", "running"].includes(j.status) && j.meeting_id === state.selected);
    state.jobs = jobs;
    const isBusy = state.jobs.some((j) => j.kind === "summarize" && ["queued", "running"].includes(j.status) && j.meeting_id === state.selected);
    if (wasBusy !== isBusy && state.meeting) renderDetail();
    renderQueue();
    // Pick up meetings added, renamed or deleted outside this page (e.g. in Explorer).
    if (Date.now() - (state.lastListLoad || 0) > 5000) {
      state.lastListLoad = Date.now();
      await loadMeetings();
      if (state.selected && !state.meetings.some((m) => m.id === state.selected)) {
        state.selected = null; state.meeting = null;
        renderHistory(); renderDetail();
      }
    }
  } catch { /* server not reachable; keep trying */ }
  const active = state.uploads.size || state.jobs.some((j) => ["queued", "running"].includes(j.status));
  pollTimer = setTimeout(poll, active ? 900 : 4000);
}

/* ================================================================ boot */
(async function boot() {
  hydrate();
  $("#settingsBtn").innerHTML = icon("sliders");
  $("#openOutput").innerHTML = icon("folder");
  $("#openOutput").onclick = () => api("/api/open-output", { method: "POST" });
  renderHero();
  await Promise.all([
    refreshStatus(),
    api("/api/settings").then((s) => (state.settings = s)),
    loadMeetings(),
  ]);
  poll();
  setInterval(refreshStatus, 15000);
  window.addEventListener("resize", moveInk);
})();
