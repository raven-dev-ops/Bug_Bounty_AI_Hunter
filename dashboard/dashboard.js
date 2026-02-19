(() => {
  "use strict";

  // This file populates dashboard.html with repo-derived views.

  const $id = (id) => document.getElementById(id);
  const $all = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function cssEscape(s) {
    const text = String(s || "");
    try {
      if (typeof CSS !== "undefined" && CSS && typeof CSS.escape === "function")
        return CSS.escape(text);
    } catch {
      // Ignore and fall back.
    }
    return text.replace(/[^a-zA-Z0-9_-]/g, (ch) => `\\${ch}`);
  }

  const state = {
    mode: "auto", // auto | import
    view: "overview", // overview | docs | workflow | tools | bounties | artifacts | all
    theme: "light", // light | dark
    fileMap: new Map(), // relPath -> File
    loaded: {},
    errors: [],
    cache: {
      dossiers: new Map(), // detailsPath -> parsed bugcrowd detail
    },
    ui: {
      sponsorKey: null,
      docsCatId: "All",
      docsFilter: "",
      workflowCaseId: null,
      workflowFilter: "",
    },
  };

  const RESOURCES = {
    hackTypes: { path: "docs/HACK_TYPES.md", kind: "md" },
    knowledgeIndex: { path: "docs/KNOWLEDGE_INDEX.md", kind: "md" },
    mkdocsConfig: { path: "mkdocs.yml", kind: "yml" },
    scriptsReadme: { path: "scripts/README.md", kind: "md" },
    bugcrowdBoard: { path: "bounty_board/bugcrowd/INDEX.md", kind: "md" },
    bugcrowdVdp: { path: "bounty_board/bugcrowd_vdp/INDEX.md", kind: "md" },
    programRegistry: { path: "data/program_registry.json", kind: "json" },
    findingsDb: { path: "data/findings_db.json", kind: "json" },
    workflowTracker: { path: "data/workflow_tracker.json", kind: "json" },
    roadmap: { path: "ROADMAP.md", kind: "md" },
  };

  const EXAMPLE_ARTIFACTS = [
    "examples/outputs/report.md",
    "examples/outputs/compliance_checklist.md",
    "examples/outputs/findings.json",
    "examples/outputs/attachments_manifest.json",
    "examples/outputs/reproducibility_pack.json",
    "examples/outputs/high_quality_report.md",
    "examples/outputs/master_catalog.md",
    "examples/outputs/program_brief_example.md",
    "examples/outputs/program_briefs/example.md",
    "examples/outputs/program_briefs/other-program.md",
  ];

  const EXAMPLE_EXPORTS = [
    "examples/exports/summary.md",
    "examples/exports/summary.json",
    "examples/exports/summary.csv",
    "examples/exports/jira_issues.csv",
    "examples/exports/finding_reports/finding-001.md",
    "examples/exports/github_issues/finding-001.md",
    "examples/exports/platforms/bugcrowd_finding-001.md",
    "examples/exports/platforms/hackerone_finding-001.md",
  ];

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function setCounters() {
    const loadMode = $id("loadMode");
    const viewMode = $id("viewMode");
    const themeMode = $id("themeMode");
    const themeModeTop = $id("themeModeTop");
    const loadedCount = $id("loadedCount");
    const errorCount = $id("errorCount");
    const dataStatus = $id("dataStatus");
    if (loadMode) loadMode.textContent = state.mode;
    if (viewMode) viewMode.textContent = state.view;
    if (themeMode) themeMode.textContent = state.theme;
    if (themeModeTop) themeModeTop.textContent = state.theme;
    if (loadedCount) loadedCount.textContent = String(Object.keys(state.loaded).length);
    if (errorCount) errorCount.textContent = String(state.errors.length);
    if (dataStatus) {
      if (state.mode === "import" && state.fileMap && state.fileMap.size) {
        dataStatus.textContent = `Imported ${state.fileMap.size} file(s). Loading from folder.`;
      } else {
        dataStatus.textContent =
          "Server mode (fetch). Import is optional and only needed for file:// or repo-wide artifact matching.";
      }
    }
  }

  function setBanner(kind, text) {
    const line = $id("bannerLine");
    if (!line) return;
    const cls =
      kind === "ok"
        ? "pilltag ok"
        : kind === "warn"
        ? "pilltag warn"
        : kind === "bad"
        ? "pilltag bad"
        : "pilltag neutral";
    line.innerHTML = `<span class="${cls}">${esc(text)}</span>`;
  }

  function isValidTheme(theme) {
    return theme === "light" || theme === "dark";
  }

  function systemTheme() {
    try {
      return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
    } catch {
      return "light";
    }
  }

  function loadStoredTheme() {
    try {
      const v = localStorage.getItem("bbhai:theme") || "";
      return isValidTheme(v) ? v : null;
    } catch {
      return null;
    }
  }

  function saveStoredTheme(theme) {
    try {
      localStorage.setItem("bbhai:theme", theme);
    } catch {
      // ignore
    }
  }

  function applyTheme(theme, opts = {}) {
    const persist = opts.persist !== false;
    const t = isValidTheme(theme) ? theme : systemTheme();
    state.theme = t;
    document.documentElement.dataset.theme = t;
    if (persist) saveStoredTheme(t);
    setCounters();
  }

  async function fetchText(path) {
    const res = await fetch(path, { cache: "no-store" });
    if (!res.ok) throw new Error(`Fetch failed: ${path} (${res.status})`);
    return await res.text();
  }

  async function readImported(path) {
    const file = state.fileMap.get(path);
    if (!file) throw new Error(`Missing imported file: ${path}`);
    return await file.text();
  }

  async function loadText(path) {
    if (state.mode === "import") return await readImported(path);
    try {
      return await fetchText(path);
    } catch (err) {
      if (state.fileMap.size > 0) {
        state.mode = "import";
        setCounters();
        return await readImported(path);
      }
      throw err;
    }
  }

  async function loadJson(path) {
    const text = await loadText(path);
    try {
      return JSON.parse(text);
    } catch {
      throw new Error(`Invalid JSON: ${path}`);
    }
  }

  function parsePipeTable(mdText, startAfterHeading) {
    const lines = String(mdText || "").split(/\r?\n/);
    let start = 0;
    if (startAfterHeading) {
      for (let i = 0; i < lines.length; i++) {
        if (lines[i].trim() === startAfterHeading) {
          start = i + 1;
          break;
        }
      }
    }

    let headerIdx = -1;
    for (let i = start; i < lines.length - 1; i++) {
      const a = lines[i].trim();
      const b = lines[i + 1].trim();
      if (a.startsWith("|") && b.startsWith("|") && b.includes("---")) {
        headerIdx = i;
        break;
      }
    }
    if (headerIdx === -1) return { headers: [], rows: [] };

    const headers = lines[headerIdx]
      .trim()
      .split("|")
      .slice(1, -1)
      .map((h) => h.trim());

    const rows = [];
    for (let i = headerIdx + 2; i < lines.length; i++) {
      const line = lines[i];
      if (!line.trim()) break;
      if (!line.trim().startsWith("|")) break;
      const cols = line
        .trim()
        .split("|")
        .slice(1, -1)
        .map((c) => c.trim());
      if (cols.length) rows.push(cols);
    }
    return { headers, rows };
  }

  function parseMdLinkCell(cell) {
    const m = String(cell || "").match(/^\[([^\]]+)\]\(([^)]+)\)$/);
    if (!m) return null;
    return { text: m[1], href: m[2] };
  }

  function parseRewardRange(rewardText) {
    const s = String(rewardText || "").trim();
    const nums = Array.from(s.matchAll(/\$([0-9][0-9,]*)/g)).map((m) =>
      Number(m[1].replace(/,/g, ""))
    );
    if (nums.length === 0) return { min: null, max: null, text: s };
    if (nums.length === 1) return { min: null, max: nums[0], text: s };
    return { min: nums[0], max: nums[nums.length - 1], text: s };
  }

  function parseValidationHours(text) {
    const s = String(text || "").trim().toLowerCase();
    if (!s || s === "n/a") return null;
    const hour = s.match(/(\d+)\s*hour/);
    if (hour) return Number(hour[1]);
    const day = s.match(/(\d+)\s*day/);
    if (day) return Number(day[1]) * 24;
    const month = s.match(/(\d+)\s*month/);
    if (month) return Number(month[1]) * 30 * 24;
    if (s.includes("about") && s.includes("hour")) return 1;
    if (s.includes("about") && s.includes("day")) return 24;
    if (s.includes("about") && s.includes("month")) return 30 * 24;
    return null;
  }

  function tierFromRewardMax(rewardMax) {
    if (rewardMax == null || !Number.isFinite(rewardMax)) return "unknown";
    if (rewardMax >= 25000) return "25k+";
    if (rewardMax >= 10000) return "10k+";
    if (rewardMax >= 5000) return "5k+";
    return "<5k";
  }

  function approachForProgram(row) {
    const steps = [];
    steps.push("Confirm written authorization and read ROE.");
    steps.push("Capture scope + prohibitions before testing.");
    if (row.private === true) steps.push("Assume confidentiality by default.");
    if (row.validationHours != null && row.validationHours <= 72)
      steps.push("Optimize for fast-to-verify, high-signal reports.");
    else steps.push("Bias toward deep modeling and high-confidence validation.");
    if (row.rewardMax != null && row.rewardMax >= 10000)
      steps.push("Focus on authz boundaries and high-impact logic.");
    else steps.push("Build reps: triage quickly and avoid rabbit holes.");

    const summary =
      row.tier === "25k+"
        ? "Top payout band. Optimize for high-confidence impact."
        : row.tier === "10k+"
        ? "High payout band. Optimize for high-confidence impact."
        : row.tier === "5k+"
        ? "Mid payout band. Plan carefully and avoid noise."
        : row.tier === "<5k"
        ? "Starter payout band. Use it to build workflow discipline."
        : "Unknown payout band. Validate rewards and rules in the platform.";

    return { summary, steps };
  }

  function normLower(s) {
    return String(s || "").trim().toLowerCase();
  }

  function formatMoney(n) {
    if (n == null || !Number.isFinite(Number(n))) return "n/a";
    try {
      return `$${Number(n).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
    } catch {
      return `$${Math.round(Number(n))}`;
    }
  }

  function formatDateTime(dt) {
    if (!(dt instanceof Date) || Number.isNaN(dt.getTime())) return "n/a";
    try {
      return dt.toLocaleString(undefined, { year: "numeric", month: "short", day: "2-digit" });
    } catch {
      return dt.toISOString();
    }
  }

  function parseFetchedAt(mdText) {
    const m = String(mdText || "").match(/Fetched at \\(UTC\\):\\s*([^\\s]+)/);
    if (!m) return null;
    const dt = new Date(m[1]);
    if (Number.isNaN(dt.getTime())) return null;
    return dt;
  }

  function sponsorFromEngagement(name) {
    let s = String(name || "").trim();
    s = s.replace(/\\s*\\([^)]*\\)\\s*$/, "").trim();
    const patterns = [
      /\\s+Managed\\s+Bug\\s+Bounty\\s+Engagement$/i,
      /\\s+Managed\\s+Bug\\s+Bounty\\s+Program$/i,
      /\\s+Bug\\s+Bounty\\s+Engagement$/i,
      /\\s+Bug\\s+Bounty\\s+Program$/i,
      /\\s+Managed\\s+Bug\\s+Bounty$/i,
      /\\s+Bug\\s+Bounty$/i,
      /\\s+Public$/i,
      /\\s+Corporate$/i,
    ];
    for (const re of patterns) s = s.replace(re, "").trim();
    s = s.replace(/[:\\-|]+\\s*$/, "").trim();
    return s || String(name || "").trim();
  }

  function classifySurface(text) {
    const t = normLower(text);
    if (/(xbox|playstation|\\bps\\d\\b|nintendo|switch|console)/.test(t)) return "console";
    if (/(mobile|android|\\bios\\b|iphone|ipad|\\bapp\\b|\\bapps\\b)/.test(t)) return "mobile";
    if (/(\\bapi\\b|graphql|rest|endpoint|swagger|openapi)/.test(t)) return "api";
    if (/(desktop|launcher|\\bclient\\b|agent\\b|\\bpc\\b)/.test(t)) return "desktop";
    if (/(firmware|embedded|iot|\\bhardware\\b)/.test(t)) return "other";
    return "web";
  }

  function classifyDevice(text) {
    const t = normLower(text);
    if (/(xbox|playstation|\\bps\\d\\b|nintendo|switch|console)/.test(t)) return "console";
    if (/(mobile|android|\\bios\\b|iphone|ipad|\\bapp\\b|\\bapps\\b)/.test(t)) return "mobile";
    if (/(windows|linux|macos|os\\s*x|desktop|\\bpc\\b|client)/.test(t)) return "pc";
    return "other";
  }

  function classifyOsGroup(text) {
    const t = normLower(text);
    if (/\\bwindows\\b/.test(t)) return "windows";
    if (/\\blinux\\b/.test(t)) return "linux";
    if (/(\\bios\\b|iphone|ipad)/.test(t)) return "ios";
    return "other";
  }

  function cssVarForSurface(surface) {
    const s = String(surface || "");
    if (s === "web") return "--tag-web-rgb";
    if (s === "mobile") return "--tag-mobile-rgb";
    if (s === "api") return "--tag-api-rgb";
    if (s === "desktop") return "--tag-desktop-rgb";
    if (s === "console") return "--tag-console-rgb";
    return "--tag-other-rgb";
  }

  function cssVarForDevice(device) {
    const d = String(device || "");
    if (d === "mobile") return "--tag-mobile-rgb";
    if (d === "pc") return "--tag-desktop-rgb";
    if (d === "console") return "--tag-console-rgb";
    return "--tag-other-rgb";
  }

  function cssVarForOsGroup(osGroup) {
    const o = String(osGroup || "");
    if (o === "windows") return "--tag-web-rgb";
    if (o === "linux") return "--band-lt5k-rgb";
    if (o === "ios") return "--tag-mobile-rgb";
    return "--tag-other-rgb";
  }

  function cssVarForRewardBand(band) {
    const t = String(band || "");
    if (t === "25k+") return "--band-25k-rgb";
    if (t === "10k+") return "--band-10k-rgb";
    if (t === "5k+") return "--band-5k-rgb";
    if (t === "<5k") return "--band-lt5k-rgb";
    return "--band-unknown-rgb";
  }

  function normalizeLevel(level) {
    const t = String(level || "").trim().toUpperCase();
    return /^P[0-4]$/.test(t) ? t : "";
  }

  function levelRank(level) {
    const t = normalizeLevel(level);
    if (t === "P0") return 0;
    if (t === "P1") return 1;
    if (t === "P2") return 2;
    if (t === "P3") return 3;
    if (t === "P4") return 4;
    return 9;
  }

  function levelFromNote(noteText) {
    const t = normLower(noteText);
    if (!t) return "";
    if (/\bp0\b/.test(t)) return "P0";
    if (/\bp1\b/.test(t)) return "P1";
    if (/\bp2\b/.test(t)) return "P2";
    if (/\bp3\b/.test(t)) return "P3";
    if (/\bp4\b/.test(t)) return "P4";
    return "";
  }

  function levelFromRewardMax(rewardMax) {
    const n = Number(rewardMax);
    if (!Number.isFinite(n)) return "P4";
    if (n >= 25000) return "P0";
    if (n >= 10000) return "P1";
    if (n >= 5000) return "P2";
    if (n >= 1000) return "P3";
    return "P4";
  }

  function levelForRow(row, noteText) {
    const override = levelFromNote(noteText);
    if (override) return override;
    return levelFromRewardMax(row && row.rewardMax);
  }

  function cssVarForLevel(level) {
    const t = normalizeLevel(level);
    if (t === "P0") return "--bad-rgb";
    if (t === "P1") return "--accent-2-rgb";
    if (t === "P2") return "--accent-3-rgb";
    if (t === "P3") return "--ok-rgb";
    if (t === "P4") return "--tag-other-rgb";
    return "--tag-other-rgb";
  }

  function tagPill(label, cssVarName) {
    const v = cssVarName || "--neutral-rgb";
    return `<span class="pilltag tag" style="--tag-rgb: var(${esc(v)})">${esc(
      label
    )}</span>`;
  }

  function bandPill(label, cssVarName) {
    const v = cssVarName || "--band-unknown-rgb";
    return `<span class="pilltag band" style="--band-rgb: var(${esc(v)})">${esc(
      label
    )}</span>`;
  }

  function levelPill(level, cssVarName) {
    const lbl = normalizeLevel(level) || "P4";
    const v = cssVarName || cssVarForLevel(lbl);
    return `<span class="pilltag level" style="--level-rgb: var(${esc(v)})">${esc(
      lbl
    )}</span>`;
  }

  function termsFromRow(row) {
    const parts = [];
    if (row.access) parts.push(`Access: ${row.access}`);
    parts.push(`Private: ${row.private ? "yes" : "no"}`);
    if (row.validation) parts.push(`Validation: ${row.validation}`);
    if (row.service) parts.push(`Service: ${row.service}`);
    if (row.scopeRank) parts.push(`Scope rank: ${row.scopeRank}`);
    return parts.join(" | ");
  }

  function noteKeyForRow(row) {
    return String(row.detailsPath || row.name || "unknown");
  }

  function loadNote(noteKey) {
    try {
      return localStorage.getItem(`bbhai:note:${noteKey}`) || "";
    } catch {
      return "";
    }
  }

  function saveNote(noteKey, text) {
    try {
      localStorage.setItem(`bbhai:note:${noteKey}`, String(text || ""));
      return true;
    } catch {
      return false;
    }
  }

  function specialBadges(row, noteText) {
    const badges = [];
    const service = normLower(row.service);
    if (service.includes("priority")) badges.push("priority triage");
    if (service.includes("24/7")) badges.push("24/7");
    if (normLower(row.rewardText).includes("points")) badges.push("points");
    if (row.private) badges.push("private");
    const note = normLower(noteText);
    if (note.includes("double") && note.includes("p0")) badges.push("double p0 (note)");
    else if (note.includes("p0")) badges.push("p0 note");
    return badges;
  }

  function renderTable(headers, rows, ariaLabel) {
    const thead = headers.map((h) => `<th>${esc(h)}</th>`).join("");
    const body = rows
      .map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join("")}</tr>`)
      .join("");
    const aria = ariaLabel ? ` aria-label="${esc(ariaLabel)}"` : "";
    return `<table${aria}><thead><tr>${thead}</tr></thead><tbody>${body}</tbody></table>`;
  }

  function renderErrors() {
    const wrap = $id("errorsWrap");
    if (!wrap) return;
    wrap.classList.remove("muted");

    if (state.errors.length === 0) {
      wrap.innerHTML =
        '<p class="muted">No load/render errors. If you opened via file://, use Import or run a local server.</p>';
      return;
    }

    const rows = state.errors.map((e) => [
      `<span class="pilltag warn">${esc(e.key || "n/a")}</span>`,
      `<code>${esc(e.path || "")}</code>`,
      `<span class="muted">${esc(e.error || "")}</span>`,
    ]);
    wrap.innerHTML =
      '<p class="muted">Some files could not be loaded. Tip: run <code>python -m http.server 8000</code> or use Import.</p>' +
      `<div class="table-scroll">${renderTable(
        ["Key", "Path", "Error"],
        rows,
        "Load errors"
      )}</div>`;
  }

  async function openFileModal(title, path) {
    const dialog = $id("modal");
    $id("modalTitle").textContent = title;
    const rich = $id("modalRich");
    if (rich) rich.innerHTML = "";
    const raw = $id("modalRaw");
    if (raw) raw.open = true;
    $id("modalPre").innerHTML = "<code>Loading...</code>";
    try {
      const text = await loadText(path);
      $id("modalPre").innerHTML = `<code>${esc(text)}</code>`;
    } catch (err) {
      const msg = String(err && err.message ? err.message : err);
      $id("modalPre").innerHTML = `<code>${esc(msg)}</code>`;
    }
    if (dialog && typeof dialog.showModal === "function") dialog.showModal();
  }

  function closeNavDrops() {
    $all("details.drop[open]").forEach((d) => d.removeAttribute("open"));
  }

  function wireNav() {
    document.addEventListener("click", (e) => {
      const t = e.target;
      const inDrop = t && t.closest && t.closest("details.drop");
      if (!inDrop) closeNavDrops();
    });

    const toggle = $id("navToggle");
    const nav = $id("mainNav");
    if (toggle && nav) {
      toggle.addEventListener("click", () => {
        const open = nav.classList.toggle("open");
        toggle.setAttribute("aria-expanded", String(open));
      });

      nav.addEventListener("click", (e) => {
        const a = e.target && e.target.closest ? e.target.closest("a") : null;
        if (!a) return;
        closeNavDrops();
        if (nav.classList.contains("open")) {
          nav.classList.remove("open");
          toggle.setAttribute("aria-expanded", "false");
        }
      });
    }
  }

  function wireModal() {
    const close = $id("modalCloseBtn");
    if (!close) return;
    close.addEventListener("click", () => {
      const dialog = $id("modal");
      if (dialog && dialog.open) dialog.close();
    });
  }

  function wireImgFallback(root) {
    const ctx = root || document;
    $all("img[data-srcs]", ctx).forEach((img) => {
      if (img.dataset.wired === "1") return;
      img.dataset.wired = "1";

      if (!img.getAttribute("src")) {
        img.style.display = "none";
      }

      img.addEventListener("load", () => {
        const prev = img.previousElementSibling;
        if (prev && prev.classList && prev.classList.contains("fallback")) prev.style.display = "none";
      });

      img.addEventListener("error", () => {
        img.style.display = "none";
      });
    });
  }

  function wireImport() {
    const importBtn = $id("importRepoBtn");
    const picker = $id("repoPicker");
    if (!importBtn || !picker) return;

    importBtn.addEventListener("click", () => picker.click());

    picker.addEventListener("change", async (e) => {
      const files = Array.from(e.target.files || []);
      if (!files.length) return;
      const m = new Map();
      for (const f of files) {
        const rel = String(f.webkitRelativePath || f.name);
        const parts = rel.split("/").filter(Boolean);
        const repoRel = parts.length > 1 ? parts.slice(1).join("/") : parts[0];
        m.set(repoRel, f);
      }
      state.fileMap = m;
      state.mode = "import";
      setCounters();
      setBanner("ok", `Imported ${files.length} file(s). Loading from folder.`);
      await loadAll();
    });
  }

  function wireReload() {
    const btn = $id("reloadBtn");
    if (!btn) return;
    btn.addEventListener("click", async () => {
      await loadAll();
    });
  }

  function wireThemeToggle() {
    const btn = $id("themeToggleBtn");
    if (!btn) return;
    btn.addEventListener("click", () => {
      const next = state.theme === "dark" ? "light" : "dark";
      applyTheme(next);
      rerenderBounties();
    });
  }

  function clearLocalStorageKeys(prefix) {
    try {
      const keys = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && String(k).startsWith(prefix)) keys.push(k);
      }
      for (const k of keys) localStorage.removeItem(k);
      return keys.length;
    } catch {
      return 0;
    }
  }

  function wireClearLocal() {
    const btn = $id("clearLocalBtn");
    if (!btn) return;
    btn.addEventListener("click", () => {
      const ok = window.confirm(
        "Clear local dashboard data (notes, sponsor sites, theme/view prefs) from this browser?"
      );
      if (!ok) return;
      clearLocalStorageKeys("bbhai:");
      applyTheme(systemTheme(), { persist: false });
      setView("overview", { persist: false });
      setBanner("ok", "Cleared local dashboard data.");
      rerenderBounties();
    });
  }

  function wireSearch() {
    const input = $id("pageSearch");
    if (!input) return;
    input.addEventListener("keydown", (e) => {
      if (e.key !== "Enter") return;
      const q = (input.value || "").trim().toLowerCase();
      if (!q) return;
      const sections = $all("main section");
      const hit = sections.find((s) => (s.textContent || "").toLowerCase().includes(q));
      if (!hit) return;
      const page = pageForElement(hit);
      if (page) setView(page);
      requestAnimationFrame(() => hit.scrollIntoView({ block: "start" }));
    });
  }

  const VIEW_DEFAULT_ANCHOR = {
    overview: "home",
    docs: "docs-forum",
    workflow: "workflow-tracker",
    tools: "cli",
    bounties: "bounty-lens",
    artifacts: "artifacts",
    all: "home",
  };

  function isValidView(view) {
    return (
      view === "overview" ||
      view === "docs" ||
      view === "workflow" ||
      view === "tools" ||
      view === "bounties" ||
      view === "artifacts" ||
      view === "all"
    );
  }

  function pageForElement(el) {
    if (!el || !el.closest) return null;
    const sec = el.closest("section[data-page]");
    const page = sec ? sec.getAttribute("data-page") : null;
    return isValidView(page) ? page : null;
  }

  function loadStoredView() {
    try {
      const v = localStorage.getItem("bbhai:view") || "";
      const mapped = v === "knowledge" ? "docs" : v;
      return isValidView(mapped) ? mapped : null;
    } catch {
      return null;
    }
  }

  function saveStoredView(view) {
    try {
      localStorage.setItem("bbhai:view", view);
    } catch {
      // ignore
    }
  }

  function applyViewVisibility() {
    $all("main section[data-page]").forEach((sec) => {
      const page = sec.getAttribute("data-page");
      const show = state.view === "all" || page === "all" || page === state.view;
      sec.hidden = !show;
    });
    document.documentElement.dataset.view = state.view;
  }

  function applyNavActive() {
    $all("nav.mainnav a[data-nav-view]").forEach((a) => {
      const v = a.getAttribute("data-nav-view");
      const active = !!v && v === state.view;
      a.classList.toggle("active", active);
      if (active) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }

  function setView(view, opts = {}) {
    const next = isValidView(view) ? view : "overview";
    state.view = next;
    if (opts.persist !== false) saveStoredView(next);

    const sel = $id("viewSelect");
    if (sel) sel.value = next;
    setCounters();
    applyViewVisibility();
    applyNavActive();
  }

  function gotoView(view) {
    setView(view);
    const anchor = VIEW_DEFAULT_ANCHOR[view] || "home";
    const el = $id(anchor);
    if (el) {
      el.scrollIntoView({ block: "start" });
      try {
        history.replaceState(null, "", `#${anchor}`);
      } catch {
        // ignore
      }
    }
  }

  function gotoId(id) {
    const el = $id(id);
    if (!el) return;
    const page = pageForElement(el);
    if (page) setView(page);
    requestAnimationFrame(() => el.scrollIntoView({ block: "start" }));
    try {
      history.replaceState(null, "", `#${id}`);
    } catch {
      // ignore
    }
  }

  function rerenderBounties() {
    if (!Array.isArray(state.loaded.bountyRows)) return;
    renderMostWanted(state.loaded.bountyRows);
    renderBountyLens(state.loaded.bountyRows);
    renderBountyProfiles(state.loaded.bountyRows);
    renderLeaderboards(state.loaded.bountyRows);
  }

  function viewForHash(hash) {
    const id = String(hash || "").replace(/^#/, "");
    if (!id) return null;
    if (id === "home") return "overview";
    const el = $id(id);
    if (!el) return null;
    return pageForElement(el);
  }

  function applyViewFromHash() {
    const page = viewForHash(location.hash);
    if (page) setView(page);
    const id = String(location.hash || "").replace(/^#/, "");
    const el = id ? $id(id) : null;
    if (el) requestAnimationFrame(() => el.scrollIntoView({ block: "start" }));
  }

  function wireViewSelect() {
    const sel = $id("viewSelect");
    if (!sel) return;
    sel.addEventListener("change", () => {
      const v = sel.value;
      gotoView(v);
    });
  }

  function wireHashView() {
    window.addEventListener("hashchange", () => {
      applyViewFromHash();
    });
  }

  function renderStaticSections() {
    const repoMap = $id("repoMap");
    if (repoMap) {
      repoMap.classList.remove("muted");
      repoMap.innerHTML = `<pre><code>${esc(
        [
          "docs/         MkDocs source, policies, lifecycle",
          "knowledge/    cards, checklists, sources (source of truth)",
          "scripts/      automation modules (python -m scripts.<name>)",
          "schemas/      JSONSchema for artifacts and inputs",
          "templates/    reporting + engagement workspace scaffolds",
          "examples/     sample inputs/outputs/exports",
          "bounty_board/ platform boards (public metadata only)",
          "data/         registries and indexes (some generated)",
          "evidence/     evidence registry entries (planning + examples)",
          "",
          "Tip (best UX): python -m http.server 8000",
          "Open: http://localhost:8000/dashboard.html",
        ].join("\\n")
      )}</code></pre>`;
    }

    const workflows = $id("workflowsGrid");
    if (workflows) {
      workflows.classList.remove("muted");
      workflows.innerHTML = `
        <div class="tiles">
          <a class="tile" href="docs/TARGET_PROFILE.md"><span class="tile-title">Scope</span><span class="tile-desc">Targets, rules, prohibitions.</span></a>
          <a class="tile" href="docs/THREAT_MODEL.md"><span class="tile-title">Model</span><span class="tile-desc">Dataflow + threats.</span></a>
          <a class="tile" href="docs/PIPELINE.md"><span class="tile-title">Plan</span><span class="tile-desc">Safe plan + guardrails.</span></a>
          <a class="tile" href="docs/TESTING.md"><span class="tile-title">Execute</span><span class="tile-desc">Only when allowed.</span></a>
          <a class="tile" href="docs/TRIAGE.md"><span class="tile-title">Triage</span><span class="tile-desc">Review and prioritize.</span></a>
          <a class="tile" href="docs/REPORTING.md"><span class="tile-title">Report</span><span class="tile-desc">Repro steps + exports.</span></a>
        </div>
      `;
    }

    const generated = $id("generatedTable");
    if (generated) {
      generated.classList.remove("muted");
      generated.innerHTML = `<div class="table-scroll">${renderTable(
        ["File/Folder", "Generator", "Notes"],
        [
          [
            "<code>knowledge/INDEX.md</code>",
            "<code>python -m scripts.knowledge_index</code>",
            "Curated knowledge index.",
          ],
          [
            "<code>docs/KNOWLEDGE_INDEX.md</code>",
            "<code>python -m scripts.publish_knowledge_docs</code>",
            "MkDocs published index.",
          ],
          [
            "<code>docs/knowledge/</code>",
            "<code>python -m scripts.publish_knowledge_docs</code>",
            "MkDocs knowledge pages.",
          ],
          [
            "<code>docs/COVERAGE_MATRIX.md</code>",
            "<code>python -m scripts.coverage_matrix</code>",
            "Generated from docs/coverage_matrix.yaml.",
          ],
          [
            "<code>data/component_registry_index.json</code>",
            "<code>python -m scripts.component_registry_index</code>",
            "Machine-readable component index.",
          ],
          [
            "<code>docs/BUGCROWD.md</code>, <code>docs/GUIDE.md</code>",
            "<code>python -m scripts.sync_mkdocs_copies</code>",
            "MkDocs copies of root docs.",
          ],
        ],
        "Generated files"
      )}</div>`;
    }

    const cli = $id("cliCheatsheet");
    if (cli) {
      cli.classList.remove("muted");
      cli.innerHTML = `<pre><code>${esc(
        [
          "# Workflow",
          "python -m bbhai init --workspace output",
          "python -m bbhai profile --workspace output",
          "python -m bbhai model --workspace output",
          "python -m bbhai plan --workspace output",
          "python -m bbhai report --workspace output --findings examples/outputs/findings.json",
          "",
          "# Catalog",
          "python -m bbhai catalog build --public-only --output data/program_registry.json",
          "python -m bbhai catalog score --public-only --output data/program_scoring_output.json",
          "python -m scripts.suggested_approach --input data/program_scoring_output.json --output data/suggested_approach_output.json",
        ].join("\\n")
      )}</code></pre>`;
    }

    const templates = $id("templatesWrap");
    if (templates) {
      templates.classList.remove("muted");
      templates.innerHTML = `
        <div class="tiles">
          <a class="tile" href="templates/reporting/README.md"><span class="tile-title">Reporting templates</span><span class="tile-desc">templates/reporting</span></a>
          <a class="tile" href="templates/platforms/README.md"><span class="tile-title">Platform exports</span><span class="tile-desc">templates/platforms</span></a>
          <a class="tile" href="templates/reporting/standard/README.md"><span class="tile-title">Standard report</span><span class="tile-desc">Markdown templates</span></a>
          <a class="tile" href="templates/engagement_workspace/README.md"><span class="tile-title">Engagement workspace</span><span class="tile-desc">Notes + recon logs</span></a>
          <a class="tile" href="templates/scan_plans/README.md"><span class="tile-title">Scan plans</span><span class="tile-desc">Template-driven plans</span></a>
        </div>
        <pre><code>${esc(
          "python -m scripts.init_engagement_workspace --platform bugcrowd --slug example-program"
        )}</code></pre>
      `;
    }

    const validation = $id("validationWrap");
    if (validation) {
      validation.classList.remove("muted");
      validation.innerHTML = `<pre><code>${esc(
        ["python -m scripts.check_all --fast", "python -m scripts.check_all"].join("\\n")
      )}</code></pre>`;
    }

    const plans = $id("platformPlansWrap");
    if (plans) {
      plans.classList.remove("muted");
      plans.innerHTML = `<pre><code>${esc(
        [
          "# Planned: bugbounty.com connector",
          "# - scripts/connectors/bugbounty_com.py",
          "# - fixtures + tests",
          "# - write to data/program_registry.json via catalog build",
          "",
          "# Reminder: public listings are not authorization to test.",
        ].join("\\n")
      )}</code></pre>`;
    }
  }

  function renderGlance() {
    const wrap = $id("glanceWrap");
    if (!wrap) return;
    wrap.classList.remove("muted");

    let hackTypes = null;
    if (state.loaded.hackTypesMd) {
      const parsed = parsePipeTable(state.loaded.hackTypesMd, "## Catalog");
      hackTypes = parsed.rows.length;
    }

    let knowledgeItems = null;
    if (state.loaded.knowledgeIndexMd) {
      const k = parseKnowledgeIndex(state.loaded.knowledgeIndexMd);
      knowledgeItems = k.cards.rows.length + k.checklists.rows.length + k.sources.rows.length;
    }

    const scripts = Array.isArray(state.loaded.scripts) ? state.loaded.scripts.length : null;
    const bounties = Array.isArray(state.loaded.bountyRows) ? state.loaded.bountyRows.length : null;
    const registry = state.loaded.programRegistryJson
      ? ((state.loaded.programRegistryJson.programs || []).length || 0)
      : null;

    const bcAt = state.loaded.bugcrowdBoardMd ? parseFetchedAt(state.loaded.bugcrowdBoardMd) : null;
    const vdpAt = state.loaded.bugcrowdVdpMd ? parseFetchedAt(state.loaded.bugcrowdVdpMd) : null;

    wrap.innerHTML = `
      <div class="statgrid cols3">
        <a class="statcard" href="#hack-types">
          <div class="statlabel">Hack types</div>
          <div class="statvalue">${esc(hackTypes == null ? "..." : String(hackTypes))}</div>
        </a>
        <a class="statcard" href="#knowledge-index">
          <div class="statlabel">Knowledge items</div>
          <div class="statvalue">${esc(
            knowledgeItems == null ? "..." : String(knowledgeItems)
          )}</div>
        </a>
        <a class="statcard" href="#scripts">
          <div class="statlabel">Scripts</div>
          <div class="statvalue">${esc(scripts == null ? "..." : String(scripts))}</div>
        </a>
        <a class="statcard" href="#bounty-lens">
          <div class="statlabel">Bounties</div>
          <div class="statvalue">${esc(bounties == null ? "..." : String(bounties))}</div>
        </a>
        <a class="statcard" href="#program-registry">
          <div class="statlabel">Registry programs</div>
          <div class="statvalue">${esc(registry == null ? "..." : String(registry))}</div>
        </a>
        <a class="statcard" href="#artifacts">
          <div class="statlabel">Artifacts</div>
          <div class="statvalue">Examples</div>
        </a>
      </div>
      <p class="muted">
        Bugcrowd fetched: ${esc(bcAt ? formatDateTime(bcAt) : "n/a")} |
        Bugcrowd VDP fetched: ${esc(vdpAt ? formatDateTime(vdpAt) : "n/a")}
      </p>
    `;
  }

  function renderHackTypes(mdText) {
    const parsed = parsePipeTable(mdText, "## Catalog");
    const headers = parsed.headers;
    const rows = parsed.rows.map((cols) => cols.map((c) => esc(c)));
    $id("hackCount").textContent = String(rows.length);
    const wrap = $id("hackTypesTableWrap");
    if (wrap) wrap.classList.remove("muted");
    $id("hackTypesTableWrap").innerHTML = `<div class="table-scroll">${renderTable(
      headers,
      rows,
      "Hack types"
    )}</div>`;
  }

  function parseKnowledgeIndex(mdText) {
    return {
      checklists: parsePipeTable(mdText, "## Checklists"),
      cards: parsePipeTable(mdText, "## Cards"),
      sources: parsePipeTable(mdText, "## Sources"),
    };
  }

  function renderKnowledgeIndex(mdText) {
    const sections = parseKnowledgeIndex(mdText);
    state.loaded.knowledge = sections;

    function flatten(kind, parsed) {
      const idxId = parsed.headers.findIndex((h) => h.toLowerCase() === "id");
      const idxTitle = parsed.headers.findIndex((h) => h.toLowerCase() === "title");
      const idxStatus = parsed.headers.findIndex((h) => h.toLowerCase() === "status");
      const idxPage = parsed.headers.findIndex((h) => h.toLowerCase() === "page");
      return parsed.rows.map((cols) => {
        const id = cols[idxId] || "";
        const title = cols[idxTitle] || "";
        const status = cols[idxStatus] || "";
        const page = cols[idxPage] || "";
        const link = parseMdLinkCell(page);
        const pageHtml = link
          ? `<a href="docs/${esc(link.href)}">${esc(link.text)}</a>`
          : esc(page);
        const statusCls = status === "reviewed" ? "pilltag ok" : "pilltag warn";
        return [
          `<span class="pilltag neutral">${esc(kind)}</span>`,
          `<span class="pilltag">${esc(id)}</span>`,
          esc(title),
          `<span class="${statusCls}">${esc(status || "n/a")}</span>`,
          pageHtml,
        ];
      });
    }

    const rows = [
      ...flatten("checklist", sections.checklists),
      ...flatten("card", sections.cards),
      ...flatten("source", sections.sources),
    ];
    $id("knowledgeCount").textContent = String(rows.length);
    const wrap = $id("knowledgeIndexWrap");
    if (wrap) wrap.classList.remove("muted");
    $id("knowledgeIndexWrap").innerHTML = `<div class="table-scroll">${renderTable(
      ["Type", "ID", "Title", "Status", "Page"],
      rows,
      "Knowledge index"
    )}</div>`;
  }

  function extractMkdocsNavLines(ymlText) {
    const lines = String(ymlText || "").split(/\r?\n/);
    const idx = lines.findIndex((l) => l.trim() === "nav:");
    if (idx === -1) return [];
    const out = [];
    for (let i = idx + 1; i < lines.length; i++) {
      const line = lines[i];
      if (!line.trim()) continue;
      if (!/^\s/.test(line)) break;
      out.push(line);
    }
    return out;
  }

  function parseMkdocsNav(ymlText) {
    const navLines = extractMkdocsNavLines(ymlText);
    const root = { kind: "category", title: "root", children: [] };
    const stack = [{ indent: -1, node: root }];

    for (const line of navLines) {
      const m = line.match(/^(\s*)-\s+(.*)$/);
      if (!m) continue;
      const indent = m[1].length;
      const body = m[2];
      const idx = body.indexOf(":");
      if (idx === -1) continue;
      const title = body.slice(0, idx).trim();
      const rest = body.slice(idx + 1).trim();
      if (!title) continue;

      const node =
        rest === ""
          ? { kind: "category", title, children: [] }
          : { kind: "page", title, path: rest };

      while (stack.length > 1 && indent <= stack[stack.length - 1].indent) stack.pop();
      const parent = stack[stack.length - 1].node;
      parent.children.push(node);
      if (node.kind === "category") stack.push({ indent, node });
    }

    return root;
  }

  function normalizeDocPath(relPath) {
    const p = String(relPath || "").trim();
    if (!p) return "";
    if (p.startsWith("docs/")) return p;
    return `docs/${p}`;
  }

  function countNavPages(node) {
    if (!node) return 0;
    if (node.kind === "page") return 1;
    if (!Array.isArray(node.children)) return 0;
    return node.children.reduce((sum, child) => sum + countNavPages(child), 0);
  }

  function buildDocsForumModel(ymlText) {
    const nav = parseMkdocsNav(ymlText);
    const categories = [];
    const pages = [];
    const catById = new Map();

    function visit(node, catPath, depth) {
      if (!node) return;
      if (node.kind === "page") {
        pages.push({
          title: node.title,
          relPath: String(node.path || ""),
          docPath: normalizeDocPath(node.path),
          catPath: catPath || "",
        });
        return;
      }
      if (node.kind !== "category") return;
      const id = catPath ? `${catPath} / ${node.title}` : node.title;
      catById.set(id, node);
      categories.push({
        id,
        title: node.title,
        depth: depth || 0,
        parentId: catPath || null,
        topicCount: countNavPages(node),
      });
      for (const child of node.children || []) visit(child, id, (depth || 0) + 1);
    }

    for (const child of nav.children || []) {
      if (child.kind === "category") visit(child, "", 0);
      else if (child.kind === "page") {
        pages.push({
          title: child.title,
          relPath: String(child.path || ""),
          docPath: normalizeDocPath(child.path),
          catPath: "",
        });
      }
    }

    const rootDocs = [
      { title: "README", path: "README.md" },
      { title: "ROADMAP", path: "ROADMAP.md" },
      { title: "CHANGELOG", path: "CHANGELOG.md" },
      { title: "CONTEXT", path: "CONTEXT.md" },
      { title: "CONTRIBUTING", path: "CONTRIBUTING.md" },
      { title: "SECURITY", path: "SECURITY.md" },
      { title: "GUIDE (root)", path: "GUIDE.md" },
      { title: "BUGCROWD (root)", path: "BUGCROWD.md" },
    ];
    categories.unshift({
      id: "Repo",
      title: "Repo",
      depth: 0,
      parentId: null,
      topicCount: rootDocs.length,
    });
    for (const d of rootDocs) {
      pages.push({
        title: d.title,
        relPath: d.path,
        docPath: d.path,
        catPath: "Repo",
      });
    }

    return { categories, pages, catById };
  }

  function renderDocsForumUi() {
    const model = state.loaded.docsForumModel;
    const catsWrap = $id("docsForumCats");
    const topicsWrap = $id("docsForumTopics");
    const countEl = $id("docsForumCount");
    if (!catsWrap || !topicsWrap || !countEl) return;

    if (!model) {
      catsWrap.classList.remove("muted");
      topicsWrap.classList.remove("muted");
      catsWrap.innerHTML = `<p class="muted">MkDocs nav not loaded. Import the repo folder or run a local server.</p>`;
      topicsWrap.innerHTML = `<p class="muted">No docs to show yet.</p>`;
      countEl.textContent = "0";
      return;
    }

    const active = String(state.ui.docsCatId || "All");
    const q = String(state.ui.docsFilter || "").trim().toLowerCase();

    const catButtons = [];
    const allActive = active === "All";
    const totalTopics = model.pages.length;
    catButtons.push(
      `<button class="forum-board${allActive ? " active" : ""}" data-cat-id="All"><span class="board-title">All</span><span class="board-meta">${esc(
        String(totalTopics)
      )} topics</span></button>`
    );
    for (const c of model.categories) {
      const isActive = active === c.id;
      const pad = 10 + Math.min(5, Math.max(0, c.depth)) * 14;
      catButtons.push(
        `<button class="forum-board${isActive ? " active" : ""}" data-cat-id="${esc(
          c.id
        )}" style="padding-left:${pad}px"><span class="board-title">${esc(
          c.title
        )}</span><span class="board-meta">${esc(String(c.topicCount))} topics</span></button>`
      );
    }
    catsWrap.classList.remove("muted");
    catsWrap.innerHTML = `<div class="forum-boards">${catButtons.join("")}</div>`;

    let pages = model.pages;
    if (q) {
      pages = pages.filter((p) => {
        return (
          String(p.title || "").toLowerCase().includes(q) ||
          String(p.relPath || "").toLowerCase().includes(q) ||
          String(p.catPath || "").toLowerCase().includes(q)
        );
      });
    } else if (!allActive) {
      const prefix = `${active} /`;
      pages = pages.filter((p) => p.catPath === active || p.catPath.startsWith(prefix));
    }

    countEl.textContent = String(pages.length);
    topicsWrap.classList.remove("muted");
    if (pages.length === 0) {
      topicsWrap.innerHTML = `<p class="muted">No matching docs.</p>`;
      return;
    }

    const topicCards = pages.map((p) => {
      const crumb = p.catPath ? p.catPath : "Root";
      return `<button class="forum-topic" data-doc-path="${esc(p.docPath)}" data-doc-title="${esc(
        p.title
      )}">
        <div class="topic-title">${esc(p.title)}</div>
        <div class="topic-meta"><span class="pilltag neutral">${esc(
          crumb
        )}</span> <code>${esc(p.relPath)}</code></div>
      </button>`;
    });
    topicsWrap.innerHTML = `<div class="forum-topics">${topicCards.join("")}</div>`;
  }

  function renderDocsForum(ymlText) {
    const wrap = $id("docsForumCats");
    if (wrap) wrap.classList.remove("muted");
    const topics = $id("docsForumTopics");
    if (topics) topics.classList.remove("muted");

    const text = String(ymlText || "").trim();
    if (!text) {
      state.loaded.docsForumModel = null;
      renderDocsForumUi();
      return;
    }
    try {
      state.loaded.docsForumModel = buildDocsForumModel(text);
    } catch {
      state.loaded.docsForumModel = null;
    }
    renderDocsForumUi();
  }

  function wireDocsForum() {
    const input = $id("docsForumFilter");
    if (input && input.dataset.wired !== "1") {
      input.dataset.wired = "1";
      input.addEventListener("input", () => {
        state.ui.docsFilter = String(input.value || "");
        renderDocsForumUi();
      });
    }

    const cats = $id("docsForumCats");
    if (cats && cats.dataset.wired !== "1") {
      cats.dataset.wired = "1";
      cats.addEventListener("click", (e) => {
        const btn = e.target && e.target.closest ? e.target.closest("button[data-cat-id]") : null;
        if (!btn) return;
        state.ui.docsCatId = btn.getAttribute("data-cat-id") || "All";
        renderDocsForumUi();
      });
    }

    const topics = $id("docsForumTopics");
    if (topics && topics.dataset.wired !== "1") {
      topics.dataset.wired = "1";
      topics.addEventListener("click", (e) => {
        const btn = e.target && e.target.closest ? e.target.closest("button[data-doc-path]") : null;
        if (!btn) return;
        const path = btn.getAttribute("data-doc-path") || "";
        const title = btn.getAttribute("data-doc-title") || path;
        if (path) openFileModal(title, path);
      });
    }
  }

  function renderScripts(mdText) {
    const lines = String(mdText || "").split(/\\r?\\n/);
    const items = [];
    for (const line of lines) {
      const m = line.match(/^\\-\\s+`([^`]+)`\\s+\\-\\s+(.*)$/);
      if (!m) continue;
      items.push({ name: m[1].trim(), desc: m[2].trim() });
    }
    state.loaded.scripts = items;
    $id("scriptCount").textContent = String(items.length);
    const rows = items.map((it) => [
      `<code>${esc(it.name)}</code>`,
      `<span class="muted">${esc(it.desc)}</span>`,
    ]);
    const wrap = $id("scriptsWrap");
    if (wrap) wrap.classList.remove("muted");
    $id("scriptsWrap").innerHTML = `<div class="table-scroll">${renderTable(
      ["Script", "Purpose"],
      rows,
      "Scripts"
    )}</div>`;
  }

  const WORKFLOW_TRACKER_STORAGE_KEY = "bbhai:workflowTracker";

  function cloneJson(value) {
    try {
      return JSON.parse(JSON.stringify(value));
    } catch {
      return null;
    }
  }

  function loadStoredWorkflowTracker() {
    try {
      const raw = localStorage.getItem(WORKFLOW_TRACKER_STORAGE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed === "object" ? parsed : null;
    } catch {
      return null;
    }
  }

  function saveStoredWorkflowTracker(tracker) {
    try {
      localStorage.setItem(WORKFLOW_TRACKER_STORAGE_KEY, JSON.stringify(tracker, null, 2));
      return true;
    } catch {
      return false;
    }
  }

  function clearStoredWorkflowTracker() {
    try {
      localStorage.removeItem(WORKFLOW_TRACKER_STORAGE_KEY);
    } catch {
      // ignore
    }
  }

  function nowIso() {
    try {
      return new Date().toISOString();
    } catch {
      return "";
    }
  }

  async function copyText(text) {
    const t = String(text || "");
    try {
      if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
        await navigator.clipboard.writeText(t);
        return true;
      }
    } catch {
      // fall through
    }

    try {
      const ta = document.createElement("textarea");
      ta.value = t;
      ta.setAttribute("readonly", "readonly");
      ta.style.position = "fixed";
      ta.style.left = "-1000px";
      ta.style.top = "-1000px";
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand("copy");
      document.body.removeChild(ta);
      return !!ok;
    } catch {
      return false;
    }
  }

  function normalizeWorkflowTracker(tracker) {
    const t = tracker && typeof tracker === "object" ? tracker : {};
    if (!Array.isArray(t.stages) || t.stages.length === 0) {
      t.stages = [
        { key: "discovery", label: "Discovery" },
        { key: "validation", label: "Validation" },
        { key: "reporting", label: "Reporting" },
        { key: "qa", label: "QA" },
        { key: "publishing", label: "Publishing" },
        { key: "closed", label: "Closed" },
      ];
    }
    if (!Array.isArray(t.cases)) t.cases = [];
    for (const c of t.cases) {
      if (!c || typeof c !== "object") continue;
      if (!Array.isArray(c.timeline)) c.timeline = [];
      if (!Array.isArray(c.links)) c.links = [];
      if (!c.status) c.status = "active";
      if (!c.stage) c.stage = String(t.stages[0]?.key || "discovery");
    }
    return t;
  }

  function stageLabelFor(tracker, key) {
    const k = String(key || "");
    for (const s of tracker.stages || []) {
      if (String(s.key || "") === k) return String(s.label || s.key || k);
    }
    return k || "n/a";
  }

  function stageIndexFor(tracker, key) {
    const k = String(key || "");
    const stages = tracker.stages || [];
    for (let i = 0; i < stages.length; i++) {
      if (String(stages[i].key || "") === k) return i;
    }
    return 0;
  }

  function workflowStatusClass(status) {
    const s = String(status || "").toLowerCase();
    if (s === "closed") return "pilltag ok";
    if (s === "blocked") return "pilltag warn";
    if (s === "paused") return "pilltag warn";
    return "pilltag neutral";
  }

  function renderWorkflowTrackerUi() {
    const fileTracker = state.loaded.workflowTrackerFile || null;
    const stored = loadStoredWorkflowTracker();
    const base = stored || (fileTracker ? cloneJson(fileTracker) : null);
    const tracker = base ? normalizeWorkflowTracker(base) : null;
    state.loaded.workflowTrackerActive = tracker;
    state.ui.workflowUsingLocal = !!stored;

    const casesWrap = $id("workflowCasesWrap");
    const detailWrap = $id("workflowDetailWrap");
    const countEl = $id("workflowCaseCount");
    const filterEl = $id("workflowCaseFilter");
    if (!casesWrap || !detailWrap || !countEl) return;

    if (filterEl) filterEl.value = String(state.ui.workflowFilter || "");

    casesWrap.classList.remove("muted");
    detailWrap.classList.remove("muted");

    if (!tracker) {
      casesWrap.innerHTML =
        '<p class="muted">Tracker not loaded. Add <code>data/workflow_tracker.json</code> or use Import/server mode.</p>';
      detailWrap.innerHTML = '<p class="muted">No tracker data.</p>';
      countEl.textContent = "0";
      return;
    }

    const q = String(state.ui.workflowFilter || "").trim().toLowerCase();
    let cases = tracker.cases || [];
    if (q) {
      cases = cases.filter((c) => {
        const hay = `${c.id || ""} ${c.title || ""} ${(c.program && c.program.name) || ""}`.toLowerCase();
        return hay.includes(q);
      });
    }

    countEl.textContent = String(cases.length);
    if (cases.length === 0) {
      casesWrap.innerHTML = '<p class="muted">No cases.</p>';
      detailWrap.innerHTML = '<p class="muted">No case selected.</p>';
      return;
    }

    const selectedId = String(state.ui.workflowCaseId || "");
    const selected =
      cases.find((c) => String(c.id || "") === selectedId) || cases[0] || null;
    if (selected && String(selected.id || "") !== selectedId) {
      state.ui.workflowCaseId = String(selected.id || "");
    }

    const listHtml = cases
      .map((c) => {
        const id = String(c.id || "");
        const active = selected && String(selected.id || "") === id;
        const program = c.program && c.program.name ? String(c.program.name) : "n/a";
        const stageLabel = stageLabelFor(tracker, c.stage);
        const updated = c.updated_at ? String(c.updated_at) : "";
        const statusCls = workflowStatusClass(c.status);
        return `<button class="case-row${active ? " active" : ""}" data-case-id="${esc(id)}">
          <div class="case-title">${esc(c.title || id || "Untitled")}</div>
          <div class="case-meta">
            <span class="${statusCls}">${esc(String(c.status || "active"))}</span>
            <span class="pilltag">${esc(stageLabel)}</span>
            <span class="muted">${esc(program)}</span>
            ${updated ? `<span class="hint">${esc(updated)}</span>` : ""}
          </div>
        </button>`;
      })
      .join("");
    casesWrap.innerHTML = `<div class="case-list">${listHtml}</div>`;

    if (!selected) {
      detailWrap.innerHTML = '<p class="muted">No case selected.</p>';
      return;
    }

    const localNote = state.ui.workflowUsingLocal ? "Local override active." : "Loaded from file.";
    const headerBadges = [
      `<span class="pilltag">${esc(String(selected.id || ""))}</span>`,
      `<span class="${workflowStatusClass(selected.status)}">${esc(String(selected.status || ""))}</span>`,
      `<span class="pilltag neutral">${esc(stageLabelFor(tracker, selected.stage))}</span>`,
    ].join(" ");

    const stageIdx = stageIndexFor(tracker, selected.stage);
    const stepsHtml = (tracker.stages || [])
      .map((s, idx) => {
        const key = String(s.key || "");
        const label = String(s.label || key);
        const status =
          selected.stage_status && typeof selected.stage_status === "object"
            ? String(selected.stage_status[key] || "")
            : idx < stageIdx
            ? "done"
            : idx === stageIdx
            ? "in_progress"
            : "todo";
        return `<button class="stage-step ${esc(status)}" data-stage-key="${esc(key)}">${esc(
          label
        )}</button>`;
      })
      .join("");

    const links = Array.isArray(selected.links) ? selected.links : [];
    const linksHtml =
      links.length === 0
        ? '<p class="muted">No links.</p>'
        : `<div class="linklist">${links
            .map((l) => {
              const label = String((l && l.label) || "link");
              const href = String((l && (l.href || l.path || l.url)) || "");
              const safeHref = href ? esc(href) : "";
              const title = href ? esc(href) : "";
              return href
                ? `<a class="linkrow" href="${safeHref}" title="${title}"><span>${esc(
                    label
                  )}</span><code>${esc(href)}</code></a>`
                : `<div class="linkrow"><span>${esc(label)}</span><code>n/a</code></div>`;
            })
            .join("")}</div>`;

    const events = Array.isArray(selected.timeline) ? [...selected.timeline] : [];
    events.sort((a, b) => {
      const da = new Date(a && (a.at || a.at_utc || "")).getTime() || 0;
      const db = new Date(b && (b.at || b.at_utc || "")).getTime() || 0;
      return da - db;
    });
    const eventHtml =
      events.length === 0
        ? '<p class="muted">No timeline events.</p>'
        : `<div class="timeline">${events
            .map((ev) => {
              const at = ev && (ev.at || ev.at_utc) ? new Date(ev.at || ev.at_utc) : null;
              const dateText = at && !Number.isNaN(at.getTime()) ? formatDateTime(at) : "n/a";
              const type = String((ev && ev.type) || "event");
              const stage = ev && ev.stage ? stageLabelFor(tracker, ev.stage) : "";
              const summary = String((ev && ev.summary) || "");
              const title = stage ? `${type}: ${stage}` : type;
              const badge = stage ? `<span class="pilltag">${esc(stage)}</span>` : "";
              return `<div class="event">
                <div class="event-head">
                  <div class="event-title">${esc(title)} ${badge}</div>
                  <div class="event-date">${esc(dateText)}</div>
                </div>
                <div class="muted">${esc(summary)}</div>
              </div>`;
            })
            .join("")}</div>`;

    detailWrap.innerHTML = `
      <div class="workflow-head">
        <h3>${esc(selected.title || "Untitled case")}</h3>
        <div class="statusline">${headerBadges}</div>
        <p class="muted">${esc(localNote)}</p>
      </div>
      <div class="stagebar" role="group" aria-label="Workflow stages">
        ${stepsHtml}
      </div>
      <div class="split">
        <div class="panel">
          <h4>Links</h4>
          ${linksHtml}
        </div>
        <div class="panel">
          <h4>Add note</h4>
          <textarea id="workflowNoteText" class="note" placeholder="Add a timeline note..."></textarea>
          <div class="statusline">
            <button class="btn primary" id="workflowAddNoteBtn">Add note</button>
          </div>
        </div>
      </div>
      <h4>Timeline</h4>
      ${eventHtml}
    `;
  }

  function renderWorkflowTracker(fileTrackerJson) {
    state.loaded.workflowTrackerFile = fileTrackerJson;
    renderWorkflowTrackerUi();
  }

  function wireWorkflowTracker() {
    const filter = $id("workflowCaseFilter");
    if (filter && filter.dataset.wired !== "1") {
      filter.dataset.wired = "1";
      filter.addEventListener("input", () => {
        state.ui.workflowFilter = String(filter.value || "");
        renderWorkflowTrackerUi();
      });
    }

    const list = $id("workflowCasesWrap");
    if (list && list.dataset.wired !== "1") {
      list.dataset.wired = "1";
      list.addEventListener("click", (e) => {
        const btn = e.target && e.target.closest ? e.target.closest("button[data-case-id]") : null;
        if (!btn) return;
        state.ui.workflowCaseId = btn.getAttribute("data-case-id") || null;
        renderWorkflowTrackerUi();
      });
    }

    const detail = $id("workflowDetailWrap");
    if (detail && detail.dataset.wired !== "1") {
      detail.dataset.wired = "1";
      detail.addEventListener("click", (e) => {
        const stageBtn =
          e.target && e.target.closest ? e.target.closest("button[data-stage-key]") : null;
        if (stageBtn) {
          const tracker = state.loaded.workflowTrackerActive;
          if (!tracker) return;
          const caseId = String(state.ui.workflowCaseId || "");
          const c = (tracker.cases || []).find((x) => String(x.id || "") === caseId);
          if (!c) return;

          const nextStage = stageBtn.getAttribute("data-stage-key") || "";
          if (!nextStage || String(c.stage || "") === nextStage) return;

          c.stage = nextStage;
          c.updated_at = nowIso();
          tracker.updated_at = nowIso();
          c.timeline = Array.isArray(c.timeline) ? c.timeline : [];
          c.timeline.push({
            at: nowIso(),
            type: "stage",
            stage: nextStage,
            summary: `Stage moved to ${stageLabelFor(tracker, nextStage)}.`,
          });
          saveStoredWorkflowTracker(tracker);
          renderWorkflowTrackerUi();
          return;
        }

        const addBtn = e.target && e.target.closest ? e.target.closest("#workflowAddNoteBtn") : null;
        if (addBtn) {
          const tracker = state.loaded.workflowTrackerActive;
          if (!tracker) return;
          const caseId = String(state.ui.workflowCaseId || "");
          const c = (tracker.cases || []).find((x) => String(x.id || "") === caseId);
          if (!c) return;
          const ta = $id("workflowNoteText");
          const note = ta ? String(ta.value || "").trim() : "";
          if (!note) return;
          c.timeline = Array.isArray(c.timeline) ? c.timeline : [];
          c.timeline.push({ at: nowIso(), type: "note", summary: note });
          c.updated_at = nowIso();
          tracker.updated_at = nowIso();
          if (ta) ta.value = "";
          saveStoredWorkflowTracker(tracker);
          renderWorkflowTrackerUi();
        }
      });
    }

    const exportBtn = $id("workflowExportBtn");
    if (exportBtn && exportBtn.dataset.wired !== "1") {
      exportBtn.dataset.wired = "1";
      exportBtn.addEventListener("click", async () => {
        const tracker = state.loaded.workflowTrackerActive;
        if (!tracker) return;
        const ok = await copyText(JSON.stringify(tracker, null, 2));
        setBanner(ok ? "ok" : "warn", ok ? "Copied tracker JSON." : "Copy failed.");
      });
    }

    const resetBtn = $id("workflowResetBtn");
    if (resetBtn && resetBtn.dataset.wired !== "1") {
      resetBtn.dataset.wired = "1";
      resetBtn.addEventListener("click", () => {
        const ok = window.confirm("Clear local workflow tracker override for this dashboard?");
        if (!ok) return;
        clearStoredWorkflowTracker();
        renderWorkflowTrackerUi();
        setBanner("ok", "Cleared workflow tracker override.");
      });
    }
  }

  function parseBugcrowdBoard(mdText, baseDir) {
    const parsed = parsePipeTable(mdText);
    const headers = parsed.headers;
    const idxEng = headers.findIndex((h) => h.toLowerCase() === "engagement");
    const idxReward = headers.findIndex((h) => h.toLowerCase() === "reward");
    const idxAccess = headers.findIndex((h) => h.toLowerCase() === "access");
    const idxPrivate = headers.findIndex((h) => h.toLowerCase() === "private");
    const idxIndustry = headers.findIndex((h) => h.toLowerCase() === "industry");
    const idxService = headers.findIndex((h) => h.toLowerCase() === "service");
    const idxScopeRank = headers.findIndex((h) => h.toLowerCase() === "scope rank");
    const idxValidation = headers.findIndex((h) => h.toLowerCase() === "validation");

    return parsed.rows.map((cols) => {
      const engCell = cols[idxEng] || "";
      const link = parseMdLinkCell(engCell);
      const name = link ? link.text : engCell;
      const detailsPath = link ? `${baseDir}/${link.href}` : null;
      const reward = parseRewardRange(cols[idxReward] || "");
      const isPrivate = String(cols[idxPrivate] || "").toLowerCase() === "true";
      const validationText = cols[idxValidation] || "";
      const validationHours = parseValidationHours(validationText);

      const row = {
        name,
        detailsPath,
        rewardText: reward.text,
        rewardMax: reward.max,
        access: cols[idxAccess] || "",
        private: isPrivate,
        industry: cols[idxIndustry] || "",
        service: cols[idxService] || "",
        scopeRank: cols[idxScopeRank] || "",
        validation: validationText,
        validationHours,
      };
      row.tier = tierFromRewardMax(row.rewardMax);
      row.approach = approachForProgram(row);
      return row;
    });
  }

  function renderBugcrowdBoard(rows, wrapId, countId, filterId, sortId) {
    function rewardMax(r) {
      return r.rewardMax == null ? -1 : r.rewardMax;
    }
    function valHours(r) {
      return r.validationHours == null ? 10 ** 12 : r.validationHours;
    }
    function tierClass(tier) {
      if (tier === "25k+") return "pilltag bad";
      if (tier === "10k+") return "pilltag warn";
      if (tier === "5k+") return "pilltag neutral";
      if (tier === "<5k") return "pilltag ok";
      return "pilltag";
    }

    function filteredSorted() {
      const q = ($id(filterId)?.value || "").trim().toLowerCase();
      let list = rows;
      if (q) {
        list = rows.filter((r) => {
          return (
            r.name.toLowerCase().includes(q) ||
            String(r.rewardText).toLowerCase().includes(q) ||
            String(r.industry).toLowerCase().includes(q) ||
            String(r.service).toLowerCase().includes(q) ||
            String(r.tier).toLowerCase().includes(q)
          );
        });
      }

      const sort = $id(sortId)?.value || "name_asc";
      const by = [...list];
      if (sort === "reward_max_desc") by.sort((a, b) => rewardMax(b) - rewardMax(a));
      else if (sort === "reward_max_asc") by.sort((a, b) => rewardMax(a) - rewardMax(b));
      else if (sort === "validation_asc") by.sort((a, b) => valHours(a) - valHours(b));
      else by.sort((a, b) => a.name.localeCompare(b.name));
      return by;
    }

    function render() {
      const list = filteredSorted();
      $id(countId).textContent = String(list.length);
      const wrap = $id(wrapId);
      if (wrap) wrap.classList.remove("muted");
      const headers = [
        "Engagement",
        "Reward",
        "Reward band",
        "Reward max",
        "Access",
        "Private",
        "Industry",
        "Service",
        "Scope rank",
        "Validation",
        "Recommended approach",
      ];

      const body = list.map((r, i) => {
        const name = r.detailsPath
          ? `<a href="#" data-dossier="1" data-idx="${esc(String(i))}">${esc(r.name)}</a>`
          : esc(r.name);
        const rewardMaxText = formatMoney(r.rewardMax);
        return [
          name,
          esc(r.rewardText),
          `<span class="${tierClass(r.tier)}">${esc(r.tier)}</span>`,
          `<span class="pilltag">${esc(rewardMaxText)}</span>`,
          esc(r.access),
          r.private ? `<span class="pilltag warn">private</span>` : "",
          esc(r.industry),
          esc(r.service),
          esc(r.scopeRank),
          esc(r.validation),
          `<span class="muted">${esc(r.approach.summary)}</span>`,
        ];
      });

      $id(wrapId).innerHTML = `<div class="table-scroll">${renderTable(
        headers,
        body,
        "Bugcrowd board"
      )}</div>`;
      $all("[data-dossier]", $id(wrapId)).forEach((a) => {
        a.addEventListener("click", async (e) => {
          e.preventDefault();
          const idx = Number(a.getAttribute("data-idx") || "-1");
          const r = list[idx];
          if (r) await openBugcrowdDossier(r);
        });
      });
    }

    $id(filterId)?.addEventListener("input", render);
    $id(sortId)?.addEventListener("change", render);
    render();
  }

  function parseBugcrowdDetail(mdText) {
    const text = String(mdText || "");
    const lines = text.split(/\r?\n/);
    const titleLine = lines.find((l) => l.startsWith("# "));
    const title = titleLine ? titleLine.replace(/^#\s+/, "").trim() : "Program";

    function parseKeyValues(heading) {
      const out = {};
      const idx = lines.findIndex((l) => l.trim() === heading);
      if (idx < 0) return out;
      for (let i = idx + 1; i < lines.length; i++) {
        const line = lines[i];
        if (!line.trim()) continue;
        if (line.startsWith("## ")) break;
        const m = line.match(/^\-\s+([^:]+)\:\s+(.*)$/);
        if (!m) continue;
        out[m[1].trim()] = m[2].trim();
      }
      return out;
    }

    function parseParagraph(heading) {
      const idx = lines.findIndex((l) => l.trim() === heading);
      if (idx < 0) return "";
      const parts = [];
      for (let i = idx + 1; i < lines.length; i++) {
        const line = lines[i];
        if (line.startsWith("## ")) break;
        if (!line.trim()) {
          if (parts.length) break;
          continue;
        }
        parts.push(line.trim());
      }
      return parts.join(" ").trim();
    }

    const overview = parseKeyValues("## Overview");
    const stats = parseKeyValues("## Stats (Public)");
    const community = parseKeyValues("## Community (Public)");
    const endpoints = parseKeyValues("## Public JSON Endpoints");
    const tagline = parseParagraph("## Tagline");
    return {
      title,
      overview,
      stats,
      community,
      endpoints,
      tagline,
      logo: overview.Logo || "",
      engagementUrl: overview["Engagement URL"] || "",
      briefUrl: overview["Hacker Portal brief URL"] || "",
      listingUrl: overview["Listing URL"] || "",
      fetchedAt: overview["Fetched at (UTC)"] || "",
    };
  }

  async function openBugcrowdDossier(row) {
    const dialog = $id("modal");
    const title = String(row && row.name ? row.name : "Details");
    $id("modalTitle").textContent = title;

    const rich = $id("modalRich");
    if (rich) rich.innerHTML = `<p class="muted">Loading dossier...</p>`;
    const raw = $id("modalRaw");
    if (raw) raw.open = false;
    $id("modalPre").innerHTML = "<code>Loading...</code>";

    if (!row || !row.detailsPath) {
      await openFileModal(title, row && row.detailsPath ? row.detailsPath : "");
      return;
    }

    try {
      const mdText = await loadText(row.detailsPath);
      $id("modalPre").innerHTML = `<code>${esc(mdText)}</code>`;

      const parsed = parseBugcrowdDetail(mdText);
      const sponsor = sponsorFromEngagement(parsed.title || row.name);
      const classifyText = `${row.name} ${parsed.tagline} ${row.industry} ${row.service}`;
      const surface = classifySurface(classifyText);
      const device = classifyDevice(classifyText);
      const osGroup = classifyOsGroup(classifyText);
      const noteKey = noteKeyForRow(row);
      const noteText = loadNote(noteKey);
      const specials = specialBadges(row, noteText);
      const level = levelForRow(row, noteText);
      const specialHtml = specials.length
        ? specials.map((b) => `<span class="pilltag warn">${esc(b)}</span>`).join(" ")
        : `<span class="muted">None</span>`;

      const sourceLabel =
        row.sourceKey === "bugcrowd_vdp" ? "Bugcrowd VDP" : row.sourceKey === "bugcrowd" ? "Bugcrowd" : "Board";

      const metaTags = [
        `<span class="pilltag neutral">${esc(sourceLabel)}</span>`,
        tagPill(surface, cssVarForSurface(surface)),
        tagPill(device, cssVarForDevice(device)),
        tagPill(osGroup, cssVarForOsGroup(osGroup)),
        `<span class="pilltag">${esc(row.industry || "n/a")}</span>`,
        row.private ? `<span class="pilltag warn">private</span>` : `<span class="pilltag ok">public</span>`,
        `<span class="pilltag">${esc(row.access || "n/a")}</span>`,
        bandPill(row.tier || "unknown", cssVarForRewardBand(row.tier)),
        levelPill(level),
        `<span class="pilltag">${esc(row.rewardText || "n/a")}</span>`,
      ].join(" ");

      const actions = [];
      if (parsed.engagementUrl)
        actions.push(
          `<a class="btn" href="${esc(parsed.engagementUrl)}" target="_blank" rel="noreferrer">Open engagement</a>`
        );
      if (parsed.briefUrl)
        actions.push(
          `<a class="btn" href="${esc(parsed.briefUrl)}" target="_blank" rel="noreferrer">Open brief</a>`
        );

      const overviewRows = Object.entries(parsed.overview || {})
        .filter(([k]) => !/^(Logo)$/i.test(k))
        .slice(0, 10)
        .map(
          ([k, v]) =>
            `<tr><td><strong>${esc(k)}</strong></td><td><span class="muted">${esc(v)}</span></td></tr>`
        )
        .join("");

      const statsRows = Object.entries(parsed.stats || {})
        .slice(0, 10)
        .map(
          ([k, v]) =>
            `<tr><td><strong>${esc(k)}</strong></td><td><span class="muted">${esc(v)}</span></td></tr>`
        )
        .join("");

      const communityRows = Object.entries(parsed.community || {})
        .slice(0, 10)
        .map(
          ([k, v]) =>
            `<tr><td><strong>${esc(k)}</strong></td><td><span class="muted">${esc(v)}</span></td></tr>`
        )
        .join("");

      const endpointRows = Object.entries(parsed.endpoints || {})
        .slice(0, 10)
        .map(([k, v]) => {
          const url = String(v || "");
          const link = url.startsWith("http")
            ? `<a href="${esc(url)}" target="_blank" rel="noreferrer">open</a>`
            : `<span class="muted">${esc(url)}</span>`;
          return `<tr><td><strong>${esc(k)}</strong></td><td>${link}</td></tr>`;
        })
        .join("");

      const noteEsc = esc(noteText);
      if (rich) {
        rich.innerHTML = `
          <div class="dossier-top">
            ${
              parsed.logo
                ? `<img class="logo" src="${esc(parsed.logo)}" alt="${esc(sponsor)} logo" loading="lazy" />`
                : `<img class="logo" src="" alt="" style="display:none" />`
            }
            <div>
              <div class="event-title">${esc(sponsor)}</div>
              <div class="dossier-meta">${metaTags}</div>
              <p class="muted">${esc(parsed.tagline || "No public tagline found in the cached export.")}</p>
              <div class="dossier-actions">
                ${actions.join("")}
                <button class="btn primary" data-note-save="${esc(noteKey)}">Save note</button>
                <button class="btn" data-note-clear="${esc(noteKey)}">Clear note</button>
              </div>
            </div>
          </div>

          <div class="grid2">
            <div class="panel">
              <h3>Terms (Summary)</h3>
              <p class="muted">${esc(termsFromRow(row))}</p>
              <p class="muted">Always follow platform rules and docs/ROE.md.</p>
              <h3>Special</h3>
              <p>${specialHtml}</p>
            </div>

            <div class="panel">
              <h3>Notes (Local)</h3>
              <p class="muted">Stored in your browser (localStorage). Use this for updates like \"double bounty on P0\".</p>
              <textarea class="note" data-note-box="${esc(noteKey)}">${noteEsc}</textarea>
              <div class="statusline">
                <span class="muted" data-note-status="${esc(noteKey)}"></span>
              </div>
            </div>
          </div>

           <div class="grid2">
             <div class="panel">
               <h3>Overview (Public Export)</h3>
               <div class="table-scroll">
                 <table aria-label="Overview"><tbody>${overviewRows || ""}</tbody></table>
               </div>
             </div>
             <div class="panel">
               <h3>Stats (Public)</h3>
               <div class="table-scroll">
                 <table aria-label="Stats"><tbody>${statsRows || ""}</tbody></table>
               </div>
             </div>
           </div>

           <div class="grid2">
             <div class="panel">
               <h3>Community (Public)</h3>
               <div class="table-scroll">
                 <table aria-label="Community"><tbody>${communityRows || ""}</tbody></table>
               </div>
             </div>
             <div class="panel">
               <h3>Public JSON Endpoints</h3>
               <div class="table-scroll">
                 <table aria-label="Endpoints"><tbody>${endpointRows || ""}</tbody></table>
               </div>
             </div>
           </div>
         `;

        const box = rich.querySelector(`[data-note-box="${cssEscape(noteKey)}"]`);
        const status = rich.querySelector(`[data-note-status="${cssEscape(noteKey)}"]`);
        const saveBtn = rich.querySelector(`[data-note-save="${cssEscape(noteKey)}"]`);
        const clearBtn = rich.querySelector(`[data-note-clear="${cssEscape(noteKey)}"]`);

        if (saveBtn && box) {
          saveBtn.onclick = () => {
            const ok = saveNote(noteKey, box.value || "");
            if (status)
              status.textContent = ok ? "Saved." : "Could not save (localStorage blocked).";
            if (ok) rerenderBounties();
          };
        }
        if (clearBtn && box) {
          clearBtn.onclick = () => {
            box.value = "";
            const ok = saveNote(noteKey, "");
            if (status)
              status.textContent = ok ? "Cleared." : "Could not clear (localStorage blocked).";
            if (ok) rerenderBounties();
          };
        }
      }
    } catch (err) {
      const msg = String(err && err.message ? err.message : err);
      if (rich) rich.innerHTML = `<p class="muted">${esc(msg)}</p>`;
      $id("modalPre").innerHTML = `<code>${esc(msg)}</code>`;
    }

    if (dialog && typeof dialog.showModal === "function") dialog.showModal();
  }

  function countBy(items, keyFn) {
    const m = new Map();
    for (const it of items || []) {
      const k = String(keyFn(it) || "n/a");
      m.set(k, (m.get(k) || 0) + 1);
    }
    return m;
  }

  function topBuckets(map, maxBuckets, otherLabel) {
    const items = Array.from(map.entries()).sort((a, b) => b[1] - a[1]);
    if (items.length <= maxBuckets) return items;
    const head = items.slice(0, maxBuckets);
    const tail = items.slice(maxBuckets);
    const other = tail.reduce((sum, [, v]) => sum + v, 0);
    head.push([otherLabel, other]);
    return head;
  }

  function cssTriplet(varName) {
    const raw = String(
      getComputedStyle(document.documentElement).getPropertyValue(varName) || ""
    )
      .trim()
      .replace(/,/g, " ");
    const parts = raw
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 3)
      .map((n) => Number(n));
    if (parts.length !== 3) return null;
    if (!parts.every((n) => Number.isFinite(n))) return null;
    return parts;
  }

  function rgbaFromTriplet(triplet, alpha) {
    if (!triplet || triplet.length !== 3) return `rgba(204, 204, 204, ${alpha})`;
    const [r, g, b] = triplet;
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  function rgbaFromCssVar(varName, alpha, fallbackCss) {
    const trip = cssTriplet(varName);
    if (!trip) return fallbackCss || `rgba(204, 204, 204, ${alpha})`;
    return rgbaFromTriplet(trip, alpha);
  }

  function drawDonut(canvas, slices) {
    const size = 220;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.floor(size * dpr);
    canvas.height = Math.floor(size * dpr);
    canvas.style.width = `${size}px`;
    canvas.style.height = `${size}px`;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const cx = size / 2;
    const cy = size / 2;
    const r = size / 2 - 8;
    const total = slices.reduce((sum, s) => sum + (s.value || 0), 0) || 1;
    let start = -Math.PI / 2;

    for (const s of slices) {
      const frac = (s.value || 0) / total;
      const ang = frac * Math.PI * 2;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, r, start, start + ang);
      ctx.closePath();
      ctx.fillStyle = s.color || "#ccc";
      ctx.fill();
      start += ang;
    }

    // Donut hole.
    ctx.globalCompositeOperation = "destination-out";
    ctx.beginPath();
    ctx.arc(cx, cy, r * 0.58, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalCompositeOperation = "source-over";

    // Subtle outline.
    ctx.strokeStyle = rgbaFromCssVar("--ink-rgb", 0.12, "rgba(0,0,0,0.10)");
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
  }

  function renderChartCard(title, entries, colorFor) {
    const total = entries.reduce((sum, [, v]) => sum + v, 0) || 1;
    const slices = entries.map(([label, value], i) => ({
      label,
      value,
      color: (typeof colorFor === "function" ? colorFor(label, i) : null) || "#ccc",
    }));

    const legend = slices
      .map((s) => {
        const pct = Math.round((s.value / total) * 100);
        return `
          <div class="legend-item">
            <span class="legend-left">
              <span class="legend-swatch" style="background:${esc(s.color)}"></span>
              <span>${esc(s.label)}</span>
            </span>
            <span class="legend-right">${esc(String(s.value))} (${esc(String(pct))}%)</span>
          </div>
        `;
      })
      .join("");

    const id = `chart_${Math.random().toString(16).slice(2)}`;
    const html = `
      <div class="chart-card">
        <div class="chart-head">
          <h3>${esc(title)}</h3>
          <span class="muted">n=${esc(String(total))}</span>
        </div>
        <div class="chart-body">
          <canvas data-chart="${esc(id)}"></canvas>
          <div class="legend">${legend}</div>
        </div>
      </div>
    `;
    return { id, html, slices };
  }

  function renderBountyCharts(rows) {
    const wrap = $id("bountyChartsWrap");
    if (!wrap) return;
    wrap.classList.remove("muted");

    const list = rows || [];
    if (list.length === 0) {
      wrap.innerHTML = `<p class="muted">No bounty rows loaded yet.</p>`;
      return;
    }

    const palette = [
      rgbaFromCssVar("--accent-rgb", 0.95, "#0e6f6a"),
      rgbaFromCssVar("--accent-2-rgb", 0.95, "#b24a2c"),
      rgbaFromCssVar("--accent-3-rgb", 0.95, "#2f4a7c"),
      rgbaFromCssVar("--ok-rgb", 0.95, "#1f7a3a"),
      rgbaFromCssVar("--warn-rgb", 0.95, "#8a5a00"),
      rgbaFromCssVar("--bad-rgb", 0.95, "#9c1a1a"),
    ];
    const pick = (i) => palette[i % palette.length];
    const colorVar = (cssVarName, fallback) =>
      rgbaFromCssVar(cssVarName, 0.95, fallback || pick(0));
    const cards = [];

    cards.push(
      renderChartCard(
        "Type",
        topBuckets(countBy(list, (r) => r.surface || "web"), 6, "Other"),
        (label) => colorVar(cssVarForSurface(label), pick(0))
      )
    );
    cards.push(
      renderChartCard(
        "Device",
        topBuckets(countBy(list, (r) => r.device), 6, "Other"),
        (label) => colorVar(cssVarForDevice(label), pick(1))
      )
    );
    cards.push(
      renderChartCard(
        "OS (group)",
        topBuckets(countBy(list, (r) => r.osGroup), 6, "Other"),
        (label) => colorVar(cssVarForOsGroup(label), pick(2))
      )
    );
    cards.push(
      renderChartCard(
        "Industry",
        topBuckets(countBy(list, (r) => r.industry || "n/a"), 6, "Other"),
        (label, i) => pick(i)
      )
    );
    cards.push(
      renderChartCard(
        "Reward band",
        topBuckets(countBy(list, (r) => r.tier || "unknown"), 6, "Other"),
        (label) => colorVar(cssVarForRewardBand(label), pick(3))
      )
    );

    const lvlCounts = countBy(list, (r) => {
      const lvl = r && r.level ? r.level : levelForRow(r, r && r.noteText);
      return normalizeLevel(lvl) || "P4";
    });
    const lvlOrder = ["P0", "P1", "P2", "P3", "P4"];
    const lvlEntries = lvlOrder
      .map((l) => [l, lvlCounts.get(l) || 0])
      .filter(([, v]) => v > 0);
    cards.push(
      renderChartCard(
        "Level",
        lvlEntries.length ? lvlEntries : [["P4", list.length]],
        (label) => colorVar(cssVarForLevel(label), pick(4))
      )
    );
    cards.push(
      renderChartCard(
        "Sponsor (top)",
        topBuckets(countBy(list, (r) => r.sponsor || "n/a"), 6, "Other"),
        (label, i) => pick(i)
      )
    );

    wrap.innerHTML = `<div class="chart-grid">${cards.map((c) => c.html).join("")}</div>`;
    for (const c of cards) {
      const canvas = wrap.querySelector(`canvas[data-chart="${cssEscape(c.id)}"]`);
      if (!canvas) continue;
      drawDonut(canvas, c.slices);
    }
  }

  function renderBountySummary(rows) {
    const wrap = $id("bountySummaryWrap");
    if (!wrap) return;
    wrap.classList.remove("muted");

    const list = rows || [];
    if (list.length === 0) {
      wrap.innerHTML = `<p class="muted">No rows match the current filters.</p>`;
      return;
    }

    const total = list.length;
    const privateCount = list.filter((r) => r.private).length;
    const noted = list.filter((r) => normLower(r.noteText)).length;

    const topReward = list.reduce((best, r) => {
      const a = best && best.rewardMax != null ? best.rewardMax : -1;
      const b = r && r.rewardMax != null ? r.rewardMax : -1;
      return b > a ? r : best;
    }, null);

    const fastest = list.reduce((best, r) => {
      const a = best && best.validationHours != null ? best.validationHours : 10 ** 12;
      const b = r && r.validationHours != null ? r.validationHours : 10 ** 12;
      return b < a ? r : best;
    }, null);

    const topSponsors = topBuckets(countBy(list, (r) => r.sponsor), 4, "Other");
    const sponsorHtml = topSponsors
      .map(([name, n]) => `<span class="pilltag"><strong>${esc(name)}</strong> ${esc(String(n))}</span>`)
      .join(" ");

    const lvlCounts = countBy(list, (r) => {
      const lvl = r && r.level ? r.level : levelForRow(r, r && r.noteText);
      return normalizeLevel(lvl) || "P4";
    });
    const lvlOrder = ["P0", "P1", "P2", "P3", "P4"];
    const lvlHtml = lvlOrder
      .map((l) => {
        const n = lvlCounts.get(l) || 0;
        if (!n) return "";
        return `<span class="pilltag level" style="--level-rgb: var(${esc(
          cssVarForLevel(l)
        )})">${esc(l)}: ${esc(String(n))}</span>`;
      })
      .filter(Boolean)
      .join(" ");

    wrap.innerHTML = `
      <div class="statgrid">
        <div class="statcard">
          <div class="statlabel">Programs</div>
          <div class="statvalue">${esc(String(total))}</div>
        </div>
        <div class="statcard">
          <div class="statlabel">Private</div>
          <div class="statvalue">${esc(String(privateCount))}</div>
        </div>
        <div class="statcard">
          <div class="statlabel">Notes</div>
          <div class="statvalue">${esc(String(noted))}</div>
        </div>
        <div class="statcard">
          <div class="statlabel">Top Reward</div>
          <div class="statvalue">${esc(formatMoney(topReward && topReward.rewardMax))}</div>
        </div>
      </div>
      <p>
        <span class="muted"><strong>Top reward:</strong></span>
        ${esc(topReward ? topReward.sponsor : "n/a")}
        <span class="muted">|</span>
        <span class="muted"><strong>Fastest validation:</strong></span>
        ${esc(fastest ? `${fastest.sponsor} (${fastest.validation || "n/a"})` : "n/a")}
      </p>
      <p>
        <span class="muted"><strong>Top sponsors (by count):</strong></span>
        ${sponsorHtml || "-"}
      </p>
      <p>
        <span class="muted"><strong>Levels:</strong></span>
        ${lvlHtml || "-"}
      </p>
    `;
  }

  function renderBountyTimeline(meta) {
    const wrap = $id("bountyTimelineWrap");
    if (!wrap) return;
    wrap.classList.remove("muted");

    const events = [];
    if (meta.bugcrowdFetchedAt)
      events.push({
        when: meta.bugcrowdFetchedAt,
        title: "Bugcrowd board fetched",
        detail: "Public engagements listing snapshot used for bounty_board/bugcrowd/INDEX.md.",
      });
    if (meta.bugcrowdVdpFetchedAt)
      events.push({
        when: meta.bugcrowdVdpFetchedAt,
        title: "Bugcrowd VDP board fetched",
        detail: "Public VDP listing snapshot used for bounty_board/bugcrowd_vdp/INDEX.md.",
      });
    const reg = meta.registryUpdatedAt;
    if (reg instanceof Date && !Number.isNaN(reg.getTime()))
      events.push({
        when: reg,
        title: "Program registry updated",
        detail: "data/program_registry.json updated_at timestamp (public-only catalog).",
      });

    events.sort((a, b) => b.when.getTime() - a.when.getTime());
    if (events.length === 0) {
      wrap.innerHTML = `<p class="muted">No timeline metadata found.</p>`;
      return;
    }

    wrap.innerHTML = `
      <div class="timeline">
        ${events
          .map(
            (e) => `
            <div class="event">
              <div class="event-head">
                <span class="event-title">${esc(e.title)}</span>
                <span class="event-date">${esc(formatDateTime(e.when))}</span>
              </div>
              <p class="muted">${esc(e.detail)}</p>
            </div>
          `
          )
          .join("")}
      </div>
    `;
  }

  function enrichBountyRow(row, sourceKey) {
    const sponsor = sponsorFromEngagement(row.name);
    const classifyText = `${row.name} ${row.industry} ${row.service}`;
    const surface = classifySurface(classifyText);
    const device = classifyDevice(classifyText);
    const osGroup = classifyOsGroup(classifyText);
    const noteKey = noteKeyForRow(row);
    const noteText = loadNote(noteKey);
    const specials = specialBadges(row, noteText);
    const level = levelForRow(row, noteText);
    return {
      ...row,
      sponsor,
      surface,
      device,
      osGroup,
      terms: termsFromRow(row),
      specials,
      level,
      noteKey,
      noteText,
      sourceKey,
    };
  }

  async function renderMostWanted(allRows) {
    const wrap = $id("mostWantedWrap");
    if (!wrap) return;
    wrap.classList.remove("muted");

    const rows = allRows || [];
    if (rows.length === 0) {
      wrap.innerHTML = `<p class="muted">No bounty rows loaded yet.</p>`;
      return;
    }

    const token = (state.ui.mwToken || 0) + 1;
    state.ui.mwToken = token;
    wrap.innerHTML = `<p class="muted">Building shortlist...</p>`;

    const sponsorMap = new Map();
    for (const r of rows) {
      const sponsor = (r && r.sponsor) || sponsorFromEngagement(r && r.name);
      const key = sponsor || "n/a";
      if (!sponsorMap.has(key)) sponsorMap.set(key, []);
      sponsorMap.get(key).push(r);
    }

    function dynamicRow(r) {
      const noteText = loadNote(r.noteKey);
      const specials = specialBadges(r, noteText);
      const level = levelForRow(r, noteText);
      return { ...r, noteText, specials, level };
    }

    function sortPrograms(a, b) {
      const ar = levelRank(a && a.level);
      const br = levelRank(b && b.level);
      if (ar !== br) return ar - br;
      const am = a && a.rewardMax != null ? a.rewardMax : -1;
      const bm = b && b.rewardMax != null ? b.rewardMax : -1;
      if (am !== bm) return bm - am;
      const ah = a && a.validationHours != null ? a.validationHours : 10 ** 12;
      const bh = b && b.validationHours != null ? b.validationHours : 10 ** 12;
      if (ah !== bh) return ah - bh;
      return String(a && a.name ? a.name : "").localeCompare(String(b && b.name ? b.name : ""));
    }

    const sponsors = Array.from(sponsorMap.entries()).map(([sponsor, sponsorRows]) => {
      const list = (sponsorRows || []).map(dynamicRow);
      list.sort(sortPrograms);
      const featured = list[0] || null;

      const max = list.reduce((m, r) => Math.max(m, r && r.rewardMax != null ? r.rewardMax : -1), -1);
      const maxReward = max >= 0 ? max : null;
      const tier = tierFromRewardMax(maxReward);

      const bestLevel = list.reduce((best, r) => {
        const lvl = r && r.level ? r.level : "P4";
        return levelRank(lvl) < levelRank(best) ? lvl : best;
      }, "P4");

      const fastest = list.reduce((best, r) => {
        const a = best && best.validationHours != null ? best.validationHours : 10 ** 12;
        const b = r && r.validationHours != null ? r.validationHours : 10 ** 12;
        return b < a ? r : best;
      }, null);

      const specialAgg = uniqueStrings(list.flatMap((r) => (r && r.specials ? r.specials : []))).slice(0, 3);
      const featuredTags = featured
        ? [
            tagPill(featured.surface || "web", cssVarForSurface(featured.surface)),
            tagPill(featured.device, cssVarForDevice(featured.device)),
            tagPill(featured.osGroup, cssVarForOsGroup(featured.osGroup)),
          ]
        : [];

      return {
        sponsor,
        list,
        featured,
        programCount: list.length,
        maxReward,
        tier,
        bestLevel,
        fastest,
        specialAgg,
        featuredTags,
        site: loadSponsorSite(sponsor),
      };
    });

    sponsors.sort((a, b) => {
      const ar = levelRank(a.bestLevel);
      const br = levelRank(b.bestLevel);
      if (ar !== br) return ar - br;
      const am = a.maxReward == null ? -1 : a.maxReward;
      const bm = b.maxReward == null ? -1 : b.maxReward;
      if (am !== bm) return bm - am;
      const ah = a.fastest && a.fastest.validationHours != null ? a.fastest.validationHours : 10 ** 12;
      const bh = b.fastest && b.fastest.validationHours != null ? b.fastest.validationHours : 10 ** 12;
      if (ah !== bh) return ah - bh;
      return String(a.sponsor).localeCompare(String(b.sponsor));
    });

    const top = sponsors.slice(0, 14);
    if (top.length === 0) {
      wrap.innerHTML = `<p class="muted">No sponsors found.</p>`;
      return;
    }

    const dossiers = await Promise.all(
      top.map(async (it) => {
        const p = it && it.featured && it.featured.detailsPath ? it.featured.detailsPath : "";
        if (!p) return null;
        return await getCachedDossier(p).catch(() => null);
      })
    );
    if (state.ui.mwToken !== token) return;

    const cards = top
      .map((it, idx) => {
        const featured = it.featured;
        const dossier = dossiers[idx] || null;
        const site = it.site || "";
        const srcs = uniqueStrings([
          ...iconCandidatesForSite(site),
          dossier && dossier.logo ? dossier.logo : "",
        ]);

        const avatar = `
          <div class="avatarstack" aria-hidden="true">
            <span class="avatar fallback">${esc(
              String(it.sponsor || "?")
                .slice(0, 1)
                .toUpperCase()
            )}</span>
            ${
              srcs.length
                ? `<img class="avatar overlay" data-srcs="${esc(
                    JSON.stringify(srcs)
                  )}" alt="" loading="lazy" referrerpolicy="no-referrer" />`
                : ""
            }
          </div>
        `;

        const approach =
          featured && featured.approach && featured.approach.summary
            ? String(featured.approach.summary)
            : "n/a";

        const engagementUrl = dossier && dossier.engagementUrl ? String(dossier.engagementUrl) : "";

        return `
          <article class="want-card">
            <div class="want-top">
              ${avatar}
              <div class="want-title">
                <div class="want-name">${esc(it.sponsor)}</div>
                <div class="want-sub muted">
                  ${esc((featured && featured.industry) || "n/a")}
                  <span class="muted"> | </span>
                  ${esc((featured && featured.service) || "n/a")}
                  <span class="muted"> | </span>
                  ${esc((featured && featured.validation) || "n/a")}
                </div>
              </div>
            </div>

            <div class="want-tags">
              ${levelPill(it.bestLevel)}
              ${bandPill(it.tier || "unknown", cssVarForRewardBand(it.tier))}
              ${it.featuredTags.join("")}
              ${it.specialAgg.map((s) => `<span class="pilltag warn">${esc(s)}</span>`).join(" ")}
            </div>

            <div class="want-meta">
              <div><span class="muted">Programs</span><br/><strong>${esc(
                String(it.programCount)
              )}</strong></div>
              <div><span class="muted">Max</span><br/><strong>${esc(
                formatMoney(it.maxReward)
              )}</strong></div>
              <div style="grid-column: span 2">
                <span class="muted">Approach</span><br/>
                <span class="muted">${esc(approach)}</span>
              </div>
            </div>

            <div class="want-actions">
              <button class="btn primary" data-mw-open-profile="${esc(it.sponsor)}">Profile</button>
              ${
                featured && featured.detailsPath
                  ? `<button class="btn" data-open-details="${esc(featured.detailsPath)}">Dossier</button>`
                  : ""
              }
              ${engagementUrl ? `<a class="btn" href="${esc(engagementUrl)}" target="_blank" rel="noreferrer">Engagement</a>` : ""}
              ${site ? `<a class="btn" href="${esc(site)}" target="_blank" rel="noreferrer">Website</a>` : ""}
            </div>

            ${
              featured
                ? `<p class="want-sub muted" style="margin-top:10px">${esc(
                    termsFromRow(featured)
                  )}</p>`
                : ""
            }
          </article>
        `;
      })
      .join("");

    wrap.innerHTML = `
      <div class="carousel-head">
        <div>
          <h3>Targets</h3>
          <p class="muted">Ranked by Level (P0..P4), reward ceiling, and validation speed.</p>
        </div>
        <div class="carousel-actions">
          <button class="btn" data-mw-prev="1" aria-label="Scroll previous">Prev</button>
          <button class="btn" data-mw-next="1" aria-label="Scroll next">Next</button>
        </div>
      </div>
      <div class="carousel" data-mw-carousel="1" tabindex="0" aria-label="Most wanted carousel">
        ${cards}
      </div>
      <p class="muted" style="margin-top:10px">
        Tip: add sponsor websites in <a href="#bounty-profiles">Sponsor Profiles</a> to use official thumbnails.
      </p>
    `;

    wireImgFallback(wrap);

    const byPath = new Map(rows.filter((r) => r && r.detailsPath).map((r) => [r.detailsPath, r]));
    $all("[data-open-details]", wrap).forEach((el) => {
      el.addEventListener("click", async (e) => {
        e.preventDefault();
        const path = el.getAttribute("data-open-details") || "";
        const r = byPath.get(path);
        if (r) await openBugcrowdDossier(r);
      });
    });

    $all("[data-mw-open-profile]", wrap).forEach((btn) => {
      btn.addEventListener("click", () => {
        const sponsor = btn.getAttribute("data-mw-open-profile") || "";
        if (!sponsor) return;
        state.ui.sponsorKey = sponsor;
        const all = Array.isArray(state.loaded.bountyRows) ? state.loaded.bountyRows : rows;
        renderBountyProfiles(all);
        renderSponsorProfile(
          sponsor,
          all.filter((r) => r && String(r.sponsor || "") === sponsor)
        );
        gotoId("bounty-profiles");
      });
    });

    const carousel = wrap.querySelector('[data-mw-carousel="1"]');
    const prev = wrap.querySelector('[data-mw-prev="1"]');
    const next = wrap.querySelector('[data-mw-next="1"]');

    const scrollByCard = (dir) => {
      if (!carousel) return;
      const card = carousel.querySelector(".want-card");
      const dx = card ? Math.round(card.getBoundingClientRect().width + 12) : 340;
      carousel.scrollBy({ left: dir * dx, behavior: "smooth" });
    };

    if (prev) prev.addEventListener("click", () => scrollByCard(-1));
    if (next) next.addEventListener("click", () => scrollByCard(1));
    if (carousel) {
      carousel.addEventListener("keydown", (e) => {
        if (e.key === "ArrowRight") scrollByCard(1);
        else if (e.key === "ArrowLeft") scrollByCard(-1);
      });
    }
  }

  function renderBountyLens(allRows) {
    const wrap = $id("bountyLensWrap");
    if (!wrap) return;
    wrap.classList.remove("muted");

    const filter = $id("bountyFilter");
    const surfaceSel = $id("bountySurface");
    const levelSel = $id("bountyLevel");
    const deviceSel = $id("bountyDevice");
    const osSel = $id("bountyOs");
    const sourceSel = $id("bountySource");
    const sortSel = $id("bountySort");
    const count = $id("bountyCount");

    const rows = allRows || [];

    function rewardMax(r) {
      return r.rewardMax == null ? -1 : r.rewardMax;
    }
    function valHours(r) {
      return r.validationHours == null ? 10 ** 12 : r.validationHours;
    }

    const render = () => {
      const q = normLower(filter && filter.value);
      const surface = surfaceSel ? surfaceSel.value : "all";
      const level = levelSel ? levelSel.value : "all";
      const device = deviceSel ? deviceSel.value : "all";
      const os = osSel ? osSel.value : "all";
      const src = sourceSel ? sourceSel.value : "all";
      const sort = sortSel ? sortSel.value : "reward_max_desc";

      let list = rows.map((r) => {
        const noteText = loadNote(r.noteKey);
        const specials = specialBadges(r, noteText);
        const lvl = levelForRow(r, noteText);
        return { ...r, noteText, specials, level: lvl };
      });
      if (src !== "all") list = list.filter((r) => r.sourceKey === src);
      if (surface !== "all") list = list.filter((r) => r.surface === surface);
      if (level !== "all") list = list.filter((r) => r.level === level);
      if (device !== "all") list = list.filter((r) => r.device === device);
      if (os !== "all") list = list.filter((r) => r.osGroup === os);
      if (q) {
        list = list.filter((r) => {
          const joined = `${r.sponsor} ${r.name} ${r.industry} ${r.service} ${r.rewardText} ${r.terms} ${r.noteText}`;
          return normLower(joined).includes(q);
        });
      }

      const by = [...list];
      if (sort === "reward_max_desc") by.sort((a, b) => rewardMax(b) - rewardMax(a));
      else if (sort === "reward_max_asc") by.sort((a, b) => rewardMax(a) - rewardMax(b));
      else if (sort === "validation_asc") by.sort((a, b) => valHours(a) - valHours(b));
      else by.sort((a, b) => a.name.localeCompare(b.name));

      if (count) count.textContent = String(by.length);

      const headers = [
        "Sponsor",
        "Engagement",
        "Source",
        "Type",
        "Device",
        "OS",
        "Reward",
        "Reward max",
        "Band",
        "Level",
        "Special",
        "Terms",
        "Notes",
      ];

      const body = by.map((r, i) => {
        const sourceLabel =
          r.sourceKey === "bugcrowd_vdp" ? "Bugcrowd VDP" : r.sourceKey === "bugcrowd" ? "Bugcrowd" : r.sourceKey;
        const sponsorHtml = `<strong>${esc(r.sponsor)}</strong><br/><span class="muted">${esc(
          r.industry || "n/a"
        )}</span>`;
        const open = r.detailsPath
          ? `<a href="#" data-dossier="1" data-idx="${esc(String(i))}">${esc(r.name)}</a>`
          : esc(r.name);

        const specials = (r.specials || []).slice(0, 3);
        const specialHtml = specials.length
          ? specials.map((b) => `<span class="pilltag warn">${esc(b)}</span>`).join(" ")
          : "";

        const notePill = r.noteText
          ? `<span class="pilltag warn">note</span>`
          : `<span class="muted">-</span>`;

        return [
          sponsorHtml,
          open,
          `<span class="pilltag neutral">${esc(sourceLabel)}</span>`,
          tagPill(r.surface || "web", cssVarForSurface(r.surface)),
          tagPill(r.device, cssVarForDevice(r.device)),
          tagPill(r.osGroup, cssVarForOsGroup(r.osGroup)),
          esc(r.rewardText || "n/a"),
          `<span class="pilltag">${esc(formatMoney(r.rewardMax))}</span>`,
          bandPill(r.tier || "unknown", cssVarForRewardBand(r.tier)),
          levelPill(r.level),
          specialHtml,
          `<span class="muted">${esc(r.terms)}</span>`,
          notePill,
        ];
      });

      wrap.innerHTML = `<div class="table-scroll">${renderTable(headers, body, "Bounty lens")}</div>`;
      $all("[data-dossier]", wrap).forEach((a) => {
        a.addEventListener("click", async (e) => {
          e.preventDefault();
          const idx = Number(a.getAttribute("data-idx") || "-1");
          const r = by[idx];
          if (r) await openBugcrowdDossier(r);
        });
      });

      renderBountySummary(by);
      renderBountyCharts(by);
    };

    if (filter) filter.oninput = render;
    if (surfaceSel) surfaceSel.onchange = render;
    if (levelSel) levelSel.onchange = render;
    if (deviceSel) deviceSel.onchange = render;
    if (osSel) osSel.onchange = render;
    if (sourceSel) sourceSel.onchange = render;
    if (sortSel) sortSel.onchange = render;
    render();
  }

  function sponsorSiteStorageKey(sponsor) {
    return `bbhai:sponsorSite:${String(sponsor || "").trim()}`;
  }

  function sponsorNoteStorageKey(sponsor) {
    return `bbhai:sponsorNote:${String(sponsor || "").trim()}`;
  }

  function loadSponsorSite(sponsor) {
    try {
      return localStorage.getItem(sponsorSiteStorageKey(sponsor)) || "";
    } catch {
      return "";
    }
  }

  function saveSponsorSite(sponsor, site) {
    try {
      const key = sponsorSiteStorageKey(sponsor);
      const val = String(site || "").trim();
      if (!val) localStorage.removeItem(key);
      else localStorage.setItem(key, val);
      return true;
    } catch {
      return false;
    }
  }

  function uniqueStrings(items) {
    const out = [];
    const seen = new Set();
    for (const it of items || []) {
      const s = String(it || "").trim();
      if (!s) continue;
      if (seen.has(s)) continue;
      seen.add(s);
      out.push(s);
    }
    return out;
  }

  function iconCandidatesForSite(site) {
    const s = String(site || "").trim();
    if (!/^https?:\/\//i.test(s)) return [];
    try {
      const u = new URL(s);
      const origin = u.origin;
      return uniqueStrings([
        `${origin}/apple-touch-icon.png`,
        `${origin}/apple-touch-icon-precomposed.png`,
        `${origin}/favicon.ico`,
        `${origin}/favicon.png`,
        `${origin}/favicon-32x32.png`,
        `${origin}/icon.png`,
      ]);
    } catch {
      return [];
    }
  }

  function loadSponsorNote(sponsor) {
    try {
      return localStorage.getItem(sponsorNoteStorageKey(sponsor)) || "";
    } catch {
      return "";
    }
  }

  function saveSponsorNote(sponsor, text) {
    try {
      localStorage.setItem(sponsorNoteStorageKey(sponsor), String(text || ""));
      return true;
    } catch {
      return false;
    }
  }

  function compactKey(s) {
    return normLower(s).replace(/[^a-z0-9]+/g, "");
  }

  function isLikelyArtifactPath(relPath) {
    const p = String(relPath || "");
    return (
      p.startsWith("output/") ||
      p.startsWith("examples/outputs/") ||
      p.startsWith("examples/exports/") ||
      p.startsWith("evidence/")
    );
  }

  function findSponsorArtifacts(sponsor, sponsorRows) {
    if (state.mode !== "import" || !state.fileMap || state.fileMap.size === 0) return [];
    const needles = new Set();
    const sponsorNeedle = compactKey(sponsor);
    if (sponsorNeedle && sponsorNeedle.length >= 4) needles.add(sponsorNeedle);

    for (const r of sponsorRows || []) {
      if (r && r.name) {
        const n = compactKey(r.name);
        if (n && n.length >= 6) needles.add(n);
      }
      if (r && r.detailsPath) {
        const base = String(r.detailsPath).split("/").pop() || "";
        const slug = compactKey(base.replace(/\\.md$/i, ""));
        if (slug && slug.length >= 6) needles.add(slug);
      }
    }

    const hits = [];
    for (const path of state.fileMap.keys()) {
      if (!isLikelyArtifactPath(path)) continue;
      const k = compactKey(path);
      if (!k) continue;
      let match = false;
      for (const n of needles) {
        if (n && k.includes(n)) {
          match = true;
          break;
        }
      }
      if (match) hits.push(path);
      if (hits.length >= 80) break;
    }
    hits.sort();
    return hits;
  }

  async function getCachedDossier(detailsPath) {
    const key = String(detailsPath || "").trim();
    if (!key) return null;
    if (state.cache.dossiers.has(key)) return state.cache.dossiers.get(key) || null;
    const mdText = await loadText(key);
    const parsed = parseBugcrowdDetail(mdText);
    const out = { ...parsed, detailsPath: key, mdText };
    state.cache.dossiers.set(key, out);
    return out;
  }

  function parseIntLoose(text) {
    const m = String(text || "").match(/([0-9][0-9,]*)/);
    if (!m) return null;
    const n = Number(m[1].replace(/,/g, ""));
    return Number.isFinite(n) ? n : null;
  }

  function bestLogoFromDossiers(dossiers) {
    for (const d of dossiers || []) {
      const logo = d && d.logo ? String(d.logo).trim() : "";
      if (logo) return logo;
    }
    return "";
  }

  function bestTaglineFromDossiers(dossiers) {
    for (const d of dossiers || []) {
      const t = d && d.tagline ? String(d.tagline).trim() : "";
      if (t) return t;
    }
    return "";
  }

  async function renderSponsorProfile(sponsor, sponsorRows) {
    const wrap = $id("sponsorProfileWrap");
    if (!wrap) return;
    wrap.classList.remove("muted");

    const token = (state.ui.profileToken || 0) + 1;
    state.ui.profileToken = token;

    const rows = sponsorRows || [];
    const site = loadSponsorSite(sponsor);
    const note = loadSponsorNote(sponsor);

    const total = rows.length;
    const privateCount = rows.filter((r) => r && r.private).length;
    const noted = rows.filter((r) => normLower(loadNote(r.noteKey))).length;
    const maxReward = rows.reduce((best, r) => {
      const a = best && best.rewardMax != null ? best.rewardMax : -1;
      const b = r && r.rewardMax != null ? r.rewardMax : -1;
      return b > a ? r : best;
    }, null);
    const fastest = rows.reduce((best, r) => {
      const a = best && best.validationHours != null ? best.validationHours : 10 ** 12;
      const b = r && r.validationHours != null ? r.validationHours : 10 ** 12;
      return b < a ? r : best;
    }, null);
    const bestLevel = rows.reduce((best, r) => {
      const lvl = levelForRow(r, loadNote(r.noteKey));
      return levelRank(lvl) < levelRank(best) ? lvl : best;
    }, "P4");

    const sponsorTags = [
      `<span class="pilltag neutral">${esc(String(total))} program(s)</span>`,
      privateCount ? `<span class="pilltag warn">${esc(String(privateCount))} private</span>` : "",
      noted ? `<span class="pilltag warn">${esc(String(noted))} noted</span>` : "",
      maxReward && maxReward.rewardMax != null
        ? `<span class="pilltag">max ${esc(formatMoney(maxReward.rewardMax))}</span>`
        : `<span class="pilltag">max n/a</span>`,
      fastest && fastest.validationHours != null
        ? `<span class="pilltag">fastest ${esc(fastest.validation || "n/a")}</span>`
        : `<span class="pilltag">fastest n/a</span>`,
      levelPill(bestLevel),
    ].filter(Boolean);

    wrap.innerHTML = `
      <div class="profile-head">
        <span class="avatar fallback" aria-hidden="true">${esc(String(sponsor || "?").slice(0, 1).toUpperCase())}</span>
        <div>
          <div class="event-title">${esc(sponsor)}</div>
          <div class="profile-meta">${sponsorTags.join(" ")}</div>
          <p class="muted">Loading cached public metadata...</p>
        </div>
      </div>
    `;

    // Fetch cached dossier exports for richer sponsor metadata (logo/tagline/stats).
    const toLoad = rows.filter((r) => r && r.detailsPath).slice(0, 36);
    const dossiers = await Promise.all(
      toLoad.map((r) => getCachedDossier(r.detailsPath).catch(() => null))
    );
    if (state.ui.profileToken !== token) return;

    const logo = bestLogoFromDossiers(dossiers);
    const tagline = bestTaglineFromDossiers(dossiers) || "No public tagline found in cached exports.";
    const iconSrcs = uniqueStrings([...iconCandidatesForSite(site), logo || ""]);

    // Aggregate sponsor stats from cached exports where present.
    const rewardedVulns = dossiers
      .map((d) => parseIntLoose(d && d.stats && d.stats["Rewarded vulnerabilities"]))
      .filter((n) => n != null);
    const hofEntries = dossiers
      .map((d) => parseIntLoose(d && d.community && d.community["Hall of fame entries"]))
      .filter((n) => n != null);

    const sum = (arr) => arr.reduce((a, b) => a + b, 0);
    const statsHtml = `
      <div class="statgrid cols3">
        <div class="statcard">
          <div class="statlabel">Programs</div>
          <div class="statvalue">${esc(String(total))}</div>
        </div>
        <div class="statcard">
          <div class="statlabel">Private</div>
          <div class="statvalue">${esc(String(privateCount))}</div>
        </div>
        <div class="statcard">
          <div class="statlabel">Notes</div>
          <div class="statvalue">${esc(String(noted))}</div>
        </div>
        <div class="statcard">
          <div class="statlabel">Max Reward</div>
          <div class="statvalue">${esc(formatMoney(maxReward && maxReward.rewardMax))}</div>
        </div>
        <div class="statcard">
          <div class="statlabel">Fastest Validation</div>
          <div class="statvalue">${esc((fastest && fastest.validation) || "n/a")}</div>
        </div>
        <div class="statcard">
          <div class="statlabel">Rewarded Vulns (sum)</div>
          <div class="statvalue">${esc(String(rewardedVulns.length ? sum(rewardedVulns) : 0))}</div>
        </div>
      </div>
    `;

    const artifacts = findSponsorArtifacts(sponsor, rows);
    const artifactsHtml =
      artifacts.length === 0
        ? state.mode === "import"
          ? `<p class="muted">No related artifact paths matched. (Path-only heuristic.)</p>`
          : `<p class="muted">Artifact matching is available in Import mode only.</p>`
        : `<div class="table-scroll">${renderTable(
            ["File", "Open"],
            artifacts.slice(0, 60).map((p) => [
              `<code>${esc(p)}</code>`,
              `<a href="#" data-open="${esc(p)}">Open</a>`,
            ]),
            "Artifacts"
          )}</div>`;

    const programCards = rows
      .map((r) => {
        const src =
          r.sourceKey === "bugcrowd_vdp"
            ? "Bugcrowd VDP"
            : r.sourceKey === "bugcrowd"
            ? "Bugcrowd"
            : r.sourceKey || "Board";
        const tier = r.tier || "unknown";
        const noteText = loadNote(r.noteKey);
        const noteBadge = noteText ? `<span class="pilltag warn">note</span>` : "";
        const level = levelForRow(r, noteText);
        const special = specialBadges(r, noteText).slice(0, 2);

        return `
          <div class="program-card">
            <div class="program-title">
              ${
                r.detailsPath
                  ? `<a href="#" data-open-details="${esc(r.detailsPath)}">${esc(r.name)}</a>`
                  : esc(r.name)
              }
            </div>
            <div class="program-sub">
              <span class="muted">${esc(src)}</span>
              <span class="muted"> | </span>
              <span class="muted">${esc(r.industry || "n/a")}</span>
            </div>
            <div class="program-tags">
              ${tagPill(r.surface || "web", cssVarForSurface(r.surface))}
              ${tagPill(r.device, cssVarForDevice(r.device))}
              ${tagPill(r.osGroup, cssVarForOsGroup(r.osGroup))}
              ${bandPill(tier, cssVarForRewardBand(tier))}
              ${levelPill(level)}
              ${r.private ? `<span class="pilltag warn">private</span>` : `<span class="pilltag ok">public</span>`}
              ${noteBadge}
              ${special.map((s) => `<span class="pilltag warn">${esc(s)}</span>`).join(" ")}
            </div>
            <p class="program-sub">
              <strong>Reward:</strong> ${esc(r.rewardText || "n/a")}
              <span class="muted"> | </span>
              <strong>Max:</strong> ${esc(formatMoney(r.rewardMax))}
              <span class="muted"> | </span>
              <strong>Validation:</strong> ${esc(r.validation || "n/a")}
            </p>
            <p class="program-sub">${esc(termsFromRow(r))}</p>
          </div>
        `;
      })
      .join("");

    wrap.innerHTML = `
      <div class="profile-head">
        <div class="avatarstack" aria-hidden="true">
          <span class="avatar fallback">${esc(
            String(sponsor || "?").slice(0, 1).toUpperCase()
          )}</span>
          ${
            iconSrcs.length
              ? `<img class="avatar overlay" data-srcs="${esc(
                  JSON.stringify(iconSrcs)
                )}" alt="" loading="lazy" referrerpolicy="no-referrer" />`
              : ""
          }
        </div>
        <div>
          <div class="event-title">${esc(sponsor)}</div>
          <div class="profile-meta">
            ${sponsorTags.join(" ")}
            ${
              hofEntries.length
                ? `<span class="pilltag neutral">HOF: ${esc(String(sum(hofEntries)))}</span>`
                : ""
            }
          </div>
          <p class="muted">${esc(tagline)}</p>
          <div class="profile-actions">
            ${
              site
                ? `<a class="btn" href="${esc(site)}" target="_blank" rel="noreferrer">Open website</a>`
                : ""
            }
            <button class="btn primary" data-sponsor-save="${esc(sponsor)}">Save</button>
            <button class="btn" data-sponsor-clear="${esc(sponsor)}">Clear</button>
          </div>
        </div>
      </div>

      <div class="toolbar" style="margin-top:12px">
        <input
          data-sponsor-site="${esc(sponsor)}"
          placeholder="Sponsor website (optional), e.g. https://example.com"
          value="${esc(site)}"
          aria-label="Sponsor website"
        />
      </div>

      ${statsHtml}

      <div class="grid2" style="margin-top:12px">
        <div class="panel">
          <h3>Sponsor Notes (Local)</h3>
          <p class="muted">Stored in your browser (localStorage). Use this for sponsor-level updates.</p>
          <textarea class="note" data-sponsor-note="${esc(sponsor)}">${esc(note)}</textarea>
          <div class="statusline">
            <button class="btn primary" data-sponsor-note-save="${esc(sponsor)}">Save note</button>
            <button class="btn" data-sponsor-note-clear="${esc(sponsor)}">Clear note</button>
            <span class="muted" data-sponsor-note-status="${esc(sponsor)}"></span>
          </div>
        </div>
        <div class="panel">
          <h3>Related Artifacts</h3>
          <p class="muted">
            Matches are path-only heuristics. Import mode enables repo-wide matching.
          </p>
          ${artifactsHtml}
        </div>
      </div>

      <h3 style="margin-top:14px">Programs</h3>
      <div class="program-grid">
        ${programCards || `<p class="muted">No programs found.</p>`}
      </div>
    `;

    wireImgFallback(wrap);

    // Website save/clear.
    const siteBox = wrap.querySelector(`[data-sponsor-site="${cssEscape(sponsor)}"]`);
    const saveBtn = wrap.querySelector(`[data-sponsor-save="${cssEscape(sponsor)}"]`);
    const clearBtn = wrap.querySelector(`[data-sponsor-clear="${cssEscape(sponsor)}"]`);
    if (saveBtn && siteBox) {
      saveBtn.onclick = () => {
        const ok = saveSponsorSite(sponsor, siteBox.value || "");
        setBanner(ok ? "ok" : "warn", ok ? "Saved sponsor website (local)." : "Could not save (localStorage blocked).");
        renderSponsorProfile(sponsor, rows);
        if (ok) renderMostWanted(state.loaded.bountyRows || []);
      };
    }
    if (clearBtn && siteBox) {
      clearBtn.onclick = () => {
        siteBox.value = "";
        const ok = saveSponsorSite(sponsor, "");
        setBanner(ok ? "ok" : "warn", ok ? "Cleared sponsor website (local)." : "Could not clear (localStorage blocked).");
        renderSponsorProfile(sponsor, rows);
        if (ok) renderMostWanted(state.loaded.bountyRows || []);
      };
    }

    // Sponsor note save/clear.
    const noteBox = wrap.querySelector(`[data-sponsor-note="${cssEscape(sponsor)}"]`);
    const noteSave = wrap.querySelector(`[data-sponsor-note-save="${cssEscape(sponsor)}"]`);
    const noteClear = wrap.querySelector(`[data-sponsor-note-clear="${cssEscape(sponsor)}"]`);
    const noteStatus = wrap.querySelector(`[data-sponsor-note-status="${cssEscape(sponsor)}"]`);
    if (noteSave && noteBox) {
      noteSave.onclick = () => {
        const ok = saveSponsorNote(sponsor, noteBox.value || "");
        if (noteStatus) noteStatus.textContent = ok ? "Saved." : "Could not save (localStorage blocked).";
      };
    }
    if (noteClear && noteBox) {
      noteClear.onclick = () => {
        noteBox.value = "";
        const ok = saveSponsorNote(sponsor, "");
        if (noteStatus) noteStatus.textContent = ok ? "Cleared." : "Could not clear (localStorage blocked).";
      };
    }

    // Dossier open links.
    const byPath = new Map(rows.filter((r) => r && r.detailsPath).map((r) => [r.detailsPath, r]));
    $all("[data-open-details]", wrap).forEach((a) => {
      a.addEventListener("click", async (e) => {
        e.preventDefault();
        const path = a.getAttribute("data-open-details") || "";
        const r = byPath.get(path);
        if (r) await openBugcrowdDossier(r);
      });
    });

    // Artifact open links.
    $all("[data-open]", wrap).forEach((a) => {
      a.addEventListener("click", async (e) => {
        e.preventDefault();
        const path = a.getAttribute("data-open");
        if (path) await openFileModal(path, path);
      });
    });
  }

  function renderBountyProfiles(allRows) {
    const treeWrap = $id("bountyTreeWrap");
    const countEl = $id("profileCount");
    if (!treeWrap) return;
    treeWrap.classList.remove("muted");

    const filter = $id("profileFilter");
    const surfaceSel = $id("profileSurface");
    const sourceSel = $id("profileSource");

    const all = allRows || [];

    function build() {
      const q = normLower(filter && filter.value);
      const surface = surfaceSel ? surfaceSel.value : "all";
      const src = sourceSel ? sourceSel.value : "all";

      let list = all;
      if (src !== "all") list = list.filter((r) => r.sourceKey === src);
      if (surface !== "all") list = list.filter((r) => (r.surface || "web") === surface);
      if (q) {
        list = list.filter((r) => {
          const joined = `${r.sponsor} ${r.name} ${r.industry} ${r.service}`.toLowerCase();
          return joined.includes(q);
        });
      }

      const surfaceOrder = ["web", "mobile", "api", "desktop", "console", "other"];
      const bySurface = new Map();
      const sponsorMap = new Map();
      for (const r of list) {
        const surf = r.surface || "web";
        if (!bySurface.has(surf)) bySurface.set(surf, new Map());
        const sMap = bySurface.get(surf);
        const sponsor = r.sponsor || "n/a";
        if (!sMap.has(sponsor)) sMap.set(sponsor, []);
        sMap.get(sponsor).push(r);

        if (!sponsorMap.has(sponsor)) sponsorMap.set(sponsor, []);
        sponsorMap.get(sponsor).push(r);
      }

      if (countEl) countEl.textContent = String(sponsorMap.size);

      const selected = state.ui.sponsorKey || "";
      const html = `
        <div class="tree">
          ${surfaceOrder
            .filter((s) => bySurface.has(s))
            .map((surf) => {
              const sponsors = bySurface.get(surf);
              const sponsorEntries = Array.from(sponsors.entries()).map(([name, rows]) => {
                const max = rows.reduce(
                  (m, r) => Math.max(m, r && r.rewardMax != null ? r.rewardMax : -1),
                  -1
                );
                const maxReward = max >= 0 ? max : null;
                const tier = tierFromRewardMax(maxReward);
                const bestLevel = rows.reduce((best, r) => {
                  const lvl = levelForRow(r, loadNote(r.noteKey));
                  return levelRank(lvl) < levelRank(best) ? lvl : best;
                }, "P4");
                const right = `<span class="tree-right"><small>${esc(
                  String(rows.length)
                )} | max ${esc(formatMoney(maxReward))}</small> ${bandPill(
                  tier,
                  cssVarForRewardBand(tier)
                )} ${levelPill(bestLevel)}</span>`;
                const cls = name === selected ? "tree-link selected" : "tree-link";
                return {
                  name,
                  max: maxReward,
                  bestLevel,
                  count: rows.length,
                  html: `<button class="${cls}" data-sponsor="${esc(name)}"><span>${esc(
                    name
                  )}</span>${right}</button>`,
                };
              });

              sponsorEntries.sort(
                (a, b) =>
                  levelRank(a.bestLevel) - levelRank(b.bestLevel) ||
                  (b.max == null ? -1 : b.max) - (a.max == null ? -1 : a.max) ||
                  (b.count || 0) - (a.count || 0) ||
                  a.name.localeCompare(b.name)
              );
              const sponsorItems = sponsorEntries.map((e) => e.html);
              const totalPrograms = Array.from(sponsors.values()).reduce((sum, rows) => sum + rows.length, 0);
              return `
                <details open>
                  <summary>
                    ${tagPill(surf, cssVarForSurface(surf))}
                    <span class="muted">sponsors: ${esc(String(sponsors.size))} | programs: ${esc(
                String(totalPrograms)
              )}</span>
                  </summary>
                  <div class="tree-body">
                    ${sponsorItems.join("") || `<p class="muted">No sponsors found.</p>`}
                  </div>
                </details>
              `;
            })
            .join("")}
        </div>
      `;

      treeWrap.innerHTML = html;

      $all("[data-sponsor]", treeWrap).forEach((btn) => {
        btn.addEventListener("click", () => {
          const sponsor = btn.getAttribute("data-sponsor") || "";
          state.ui.sponsorKey = sponsor;
          build();
        });
      });

      // Keep the profile panel in sync when filters change.
      if (selected && sponsorMap.has(selected)) renderSponsorProfile(selected, sponsorMap.get(selected));
    }

    if (filter) filter.oninput = build;
    if (surfaceSel) surfaceSel.onchange = build;
    if (sourceSel) sourceSel.onchange = build;
    build();
  }

  function renderLeaderboards(allRows) {
    const wrap = $id("leaderboardsWrap");
    if (!wrap) return;
    wrap.classList.remove("muted");

    const rows = allRows || [];
    const byPath = new Map(rows.filter((r) => r && r.detailsPath).map((r) => [r.detailsPath, r]));
    const rowLevel = (r) => levelForRow(r, loadNote(r && r.noteKey));

    function linkForRow(r) {
      if (r && r.detailsPath) {
        return `<a href="#" data-open-details="${esc(r.detailsPath)}">${esc(r.name)}</a>`;
      }
      return esc(r && r.name ? r.name : "n/a");
    }

    function topByReward() {
      return [...rows]
        .filter((r) => r && r.rewardMax != null)
        .sort((a, b) => (b.rewardMax || -1) - (a.rewardMax || -1))
        .slice(0, 10);
    }

    function topByFastestValidation() {
      return [...rows]
        .filter((r) => r && r.validationHours != null)
        .sort((a, b) => (a.validationHours || 10 ** 12) - (b.validationHours || 10 ** 12))
        .slice(0, 10);
    }

    function topSponsors() {
      const m = countBy(rows, (r) => r.sponsor || "n/a");
      return topBuckets(m, 10, "Other");
    }

    const rewardTable = renderTable(
      ["Engagement", "Sponsor", "Level", "Max reward", "Band", "Validation"],
      topByReward().map((r) => [
        linkForRow(r),
        `<strong>${esc(r.sponsor || "n/a")}</strong>`,
        levelPill(rowLevel(r)),
        `<span class="pilltag">${esc(formatMoney(r.rewardMax))}</span>`,
        bandPill(r.tier || "unknown", cssVarForRewardBand(r.tier)),
        `<span class="muted">${esc(r.validation || "n/a")}</span>`,
      ]),
      "Top rewards"
    );

    const fastTable = renderTable(
      ["Engagement", "Sponsor", "Level", "Validation", "Service", "Access"],
      topByFastestValidation().map((r) => [
        linkForRow(r),
        `<strong>${esc(r.sponsor || "n/a")}</strong>`,
        levelPill(rowLevel(r)),
        `<span class="pilltag">${esc(r.validation || "n/a")}</span>`,
        `<span class="muted">${esc(r.service || "n/a")}</span>`,
        `<span class="muted">${esc(r.access || "n/a")}</span>`,
      ]),
      "Fastest validation"
    );

    const sponsorTable = renderTable(
      ["Sponsor", "Programs"],
      topSponsors().map(([name, n]) => [`<strong>${esc(name)}</strong>`, `<span class="pilltag">${esc(String(n))}</span>`]),
      "Top sponsors"
    );

    wrap.innerHTML = `
      <div class="split">
        <div class="panel">
          <h3>Repo Leaderboards (Derived)</h3>
          <p class="muted">
            These are computed from cached board exports and local notes. Validate current rules and rewards on the platform.
          </p>
          <h3>Top Rewards</h3>
          <div class="table-scroll">${rewardTable}</div>
          <h3 style="margin-top:12px">Fastest Validation</h3>
          <div class="table-scroll">${fastTable}</div>
          <h3 style="margin-top:12px">Sponsor Volume</h3>
          <div class="table-scroll">${sponsorTable}</div>
        </div>
        <div class="panel" id="lbBugcrowdWrap">
          <h3>Bugcrowd Public Stats (Cached)</h3>
          <p class="muted">Loading cached engagement exports for public stats (hall of fame, rewarded vulns).</p>
          <div class="muted">If this is slow, reload the page or use Import mode.</div>
        </div>
      </div>
    `;

    $all("[data-open-details]", wrap).forEach((a) => {
      a.addEventListener("click", async (e) => {
        e.preventDefault();
        const path = a.getAttribute("data-open-details") || "";
        const r = byPath.get(path);
        if (r) await openBugcrowdDossier(r);
      });
    });

    // Async enrichment for Bugcrowd bug bounty programs (small set).
    const bc = rows.filter((r) => r && r.sourceKey === "bugcrowd" && r.detailsPath);
    const target = $id("lbBugcrowdWrap");
    if (!target || bc.length === 0) return;
    const token = (state.ui.lbToken || 0) + 1;
    state.ui.lbToken = token;

    Promise.all(
      bc.slice(0, 60).map(async (r) => {
        const d = await getCachedDossier(r.detailsPath).catch(() => null);
        return { row: r, dossier: d };
      })
    )
      .then((items) => {
        if (state.ui.lbToken !== token) return;
        const enriched = items.filter((it) => it && it.row && it.dossier);

        function metric(it, key, path) {
          const v =
            path === "stats"
              ? it.dossier && it.dossier.stats && it.dossier.stats[key]
              : it.dossier && it.dossier.community && it.dossier.community[key];
          return parseIntLoose(v);
        }

        function endpoint(it, key) {
          const v = it.dossier && it.dossier.endpoints && it.dossier.endpoints[key];
          return String(v || "");
        }

        const topRewarded = [...enriched]
          .map((it) => ({ ...it, n: metric(it, "Rewarded vulnerabilities", "stats") || 0 }))
          .sort((a, b) => b.n - a.n)
          .slice(0, 10);
        const topHof = [...enriched]
          .map((it) => ({ ...it, n: metric(it, "Hall of fame entries", "community") || 0 }))
          .sort((a, b) => b.n - a.n)
          .slice(0, 10);
        const topJoined = [...enriched]
          .map((it) => ({ ...it, n: metric(it, "Recently joined users", "community") || 0 }))
          .sort((a, b) => b.n - a.n)
          .slice(0, 10);

        const mk = (title, list, label) => `
          <h3 style="margin-top:12px">${esc(title)}</h3>
          <div class="table-scroll">${renderTable(
            ["Engagement", "Sponsor", label, "HOF JSON"],
            list.map((it) => {
              const hofUrl = endpoint(it, "Hall of fame (JSON)");
              return [
                linkForRow(it.row),
                `<strong>${esc(it.row.sponsor || "n/a")}</strong>`,
                `<span class="pilltag">${esc(String(it.n))}</span>`,
                hofUrl
                  ? `<a href="${esc(hofUrl)}" target="_blank" rel="noreferrer">open</a>`
                  : `<span class="muted">n/a</span>`,
              ];
            }),
            title
          )}</div>
        `;

        target.innerHTML = `
          <h3>Bugcrowd Public Stats (Cached)</h3>
          <p class="muted">
            Derived from cached detail exports under <code>bounty_board/bugcrowd/*.md</code>. Values may be stale.
          </p>
          ${mk("Most Rewarded Vulnerabilities", topRewarded, "Rewarded")}
          ${mk("Most Hall of Fame Entries", topHof, "HOF entries")}
          ${mk("Most Recently Joined Users", topJoined, "Joined")}
        `;

        $all("[data-open-details]", target).forEach((a) => {
          a.addEventListener("click", async (e) => {
            e.preventDefault();
            const path = a.getAttribute("data-open-details") || "";
            const r = byPath.get(path);
            if (r) await openBugcrowdDossier(r);
          });
        });
      })
      .catch((err) => {
        if (state.ui.lbToken !== token) return;
        target.innerHTML = `<p class="muted">${esc(String(err))}</p>`;
      });
  }

  function renderProgramRegistry(registryJson) {
    const programs = (registryJson && registryJson.programs) || [];
    const platformSel = $id("registryPlatform");
    const platforms = Array.from(new Set(programs.map((p) => String(p.platform || "n/a")))).sort();
    for (const p of platforms) {
      const opt = document.createElement("option");
      opt.value = p;
      opt.textContent = p;
      platformSel.appendChild(opt);
    }

    function tierClass(tier) {
      if (tier === "25k+") return "pilltag bad";
      if (tier === "10k+") return "pilltag warn";
      if (tier === "5k+") return "pilltag neutral";
      if (tier === "<5k") return "pilltag ok";
      return "pilltag";
    }

    function row(p) {
      const rewards = p.rewards || {};
      const max = rewards.max != null ? Number(rewards.max) : null;
      const tier = tierFromRewardMax(max);
      const safeHarbor = p.safe_harbor && p.safe_harbor.present;
      const inScopeCount = (p.scope && p.scope.in_scope && p.scope.in_scope.length) || 0;
      const restrictionsCount =
        (p.restrictions && p.restrictions.length) ||
        (p.scope && p.scope.restrictions && p.scope.restrictions.length) ||
        0;
      const policy = p.policy_url
        ? `<a href="${esc(p.policy_url)}" target="_blank" rel="noreferrer">open</a>`
        : "n/a";
      return [
        `<span class="pilltag">${esc(p.id || "n/a")}</span><br/><strong>${esc(
          p.name || "n/a"
        )}</strong>`,
        `<span class="pilltag neutral">${esc(p.platform || "n/a")}</span>`,
        esc(rewards.summary || "n/a"),
        `<span class="${tierClass(tier)}">${esc(tier)}</span>`,
        safeHarbor ? `<span class="pilltag ok">yes</span>` : `<span class="pilltag warn">unknown/no</span>`,
        `<span class="pilltag">${esc(String(inScopeCount))}</span>`,
        `<span class="pilltag">${esc(String(restrictionsCount))}</span>`,
        policy,
      ];
    }

    function render() {
      const q = ($id("registryFilter").value || "").trim().toLowerCase();
      const plat = $id("registryPlatform").value || "all";
      const list = programs
        .filter((p) => (plat === "all" ? true : String(p.platform || "n/a") === plat))
        .filter((p) => {
          if (!q) return true;
          const joined = `${p.id} ${p.name} ${p.platform} ${(p.rewards && p.rewards.summary) || ""}`.toLowerCase();
          return joined.includes(q);
        });
      $id("registryCount").textContent = String(list.length);
      const wrap = $id("registryWrap");
      if (wrap) wrap.classList.remove("muted");
      $id("registryWrap").innerHTML = `<div class="table-scroll">${renderTable(
        [
          "Program",
          "Platform",
          "Rewards",
          "Reward band",
          "Safe harbor",
          "In-scope",
          "Restrictions",
          "Policy",
        ],
        list.map(row),
        "Program registry"
      )}</div>`;
    }

    $id("registryFilter").addEventListener("input", render);
    $id("registryPlatform").addEventListener("change", render);
    render();
  }

  function renderPathList(paths, wrapId, countId, filterId) {
    function render() {
      const q = filterId ? ($id(filterId).value || "").trim().toLowerCase() : "";
      const list = q ? paths.filter((p) => p.toLowerCase().includes(q)) : paths;
      if (countId) $id(countId).textContent = String(list.length);
      const rows = list.map((p) => [
        `<code>${esc(p)}</code>`,
        `<a href="#" data-open="${esc(p)}">Open</a>`,
      ]);
      const wrap = $id(wrapId);
      if (wrap) wrap.classList.remove("muted");
      $id(wrapId).innerHTML = `<div class="table-scroll">${renderTable(
        ["File", "Open"],
        rows,
        "Files"
      )}</div>`;
      $all("[data-open]", $id(wrapId)).forEach((a) => {
        a.addEventListener("click", async (e) => {
          e.preventDefault();
          const path = a.getAttribute("data-open");
          await openFileModal(path, path);
        });
      });
    }
    if (filterId) $id(filterId).addEventListener("input", render);
    render();
  }

  function renderFindings(findingsDbJson) {
    const json = findingsDbJson || { findings: [] };
    const findings = json.findings || [];

    const counts = { critical: 0, high: 0, medium: 0, low: 0, other: 0 };
    for (const f of findings) {
      const sev = normLower(f && f.severity);
      if (sev === "critical") counts.critical += 1;
      else if (sev === "high") counts.high += 1;
      else if (sev === "medium") counts.medium += 1;
      else if (sev === "low") counts.low += 1;
      else counts.other += 1;
    }

    const wrap = $id("findingsWrap");
    if (wrap) wrap.classList.remove("muted");
    $id("findingsWrap").innerHTML = `
      <div class="statusline">
        <span class="pilltag bad">critical: ${esc(String(counts.critical))}</span>
        <span class="pilltag warn">high: ${esc(String(counts.high))}</span>
        <span class="pilltag neutral">medium: ${esc(String(counts.medium))}</span>
        <span class="pilltag ok">low: ${esc(String(counts.low))}</span>
        ${counts.other ? `<span class="pilltag">other: ${esc(String(counts.other))}</span>` : ""}
      </div>
      <details class="modal-raw">
        <summary>Raw JSON</summary>
        <pre><code>${esc(JSON.stringify(json, null, 2))}</code></pre>
      </details>
    `;
  }

  function renderRoadmap(mdText) {
    const text = String(mdText || "");
    const firstPara = text
      .split(/\\r?\\n\\r?\\n/)
      .find((p) => p.trim() && !p.trim().startsWith("#"));
    const preview = (firstPara || "").trim().slice(0, 460) || "Open ROADMAP.md to read.";
    const wrap = $id("roadmapWrap");
    if (wrap) wrap.classList.remove("muted");
    $id("roadmapWrap").innerHTML = `
      <div class="toolbar">
        <a class="btn" href="ROADMAP.md">Open ROADMAP.md</a>
        <a class="btn" href="docs/PROJECT_OUTLINE.md">Open PROJECT_OUTLINE</a>
      </div>
      <p class="muted">${esc(preview)}</p>
    `;
  }

  function wireKnowledgeFilters() {
    const filter = $id("knowledgeFilter");
    const kind = $id("knowledgeType");
    if (!filter || !kind) return;

    const render = () => {
      const q = filter.value.trim().toLowerCase();
      const t = kind.value;
      const sections = state.loaded.knowledge;
      if (!sections) return;

      function take(kindKey, label) {
        if (t !== "all" && t !== kindKey) return [];
        const parsed = sections[kindKey];
        const idxId = parsed.headers.findIndex((h) => h.toLowerCase() === "id");
        const idxTitle = parsed.headers.findIndex((h) => h.toLowerCase() === "title");
        const idxStatus = parsed.headers.findIndex((h) => h.toLowerCase() === "status");
        const idxPage = parsed.headers.findIndex((h) => h.toLowerCase() === "page");
        return parsed.rows
          .filter((cols) => {
            if (!q) return true;
            return cols.join(" ").toLowerCase().includes(q);
          })
          .map((cols) => {
            const id = cols[idxId] || "";
            const title = cols[idxTitle] || "";
            const status = cols[idxStatus] || "";
            const page = cols[idxPage] || "";
            const link = parseMdLinkCell(page);
            const pageHtml = link
              ? `<a href="docs/${esc(link.href)}">${esc(link.text)}</a>`
              : esc(page);
            const statusCls = status === "reviewed" ? "pilltag ok" : "pilltag warn";
            return [
              `<span class="pilltag neutral">${esc(label)}</span>`,
              `<span class="pilltag">${esc(id)}</span>`,
              esc(title),
              `<span class="${statusCls}">${esc(status || "n/a")}</span>`,
              pageHtml,
            ];
          });
      }

      const rows = [
        ...take("cards", "card"),
        ...take("checklists", "checklist"),
        ...take("sources", "source"),
      ];

      $id("knowledgeCount").textContent = String(rows.length);
      const wrap = $id("knowledgeIndexWrap");
      if (wrap) wrap.classList.remove("muted");
      $id("knowledgeIndexWrap").innerHTML = `<div class="table-scroll">${renderTable(
        ["Type", "ID", "Title", "Status", "Page"],
        rows,
        "Knowledge index"
      )}</div>`;
    };

    filter.addEventListener("input", render);
    kind.addEventListener("change", render);
    render();
  }

  function wireHackFilter(hackMd) {
    const input = $id("hackFilter");
    if (!input) return;
    input.addEventListener("input", () => {
      const q = input.value.trim().toLowerCase();
      const parsed = parsePipeTable(hackMd, "## Catalog");
      const headers = parsed.headers;
      const rows = parsed.rows
        .filter((r) => (q ? r.join(" ").toLowerCase().includes(q) : true))
        .map((cols) => cols.map((c) => esc(c)));
      $id("hackCount").textContent = String(rows.length);
      $id("hackTypesTableWrap").innerHTML = `<div class="table-scroll">${renderTable(
        headers,
        rows,
        "Hack types"
      )}</div>`;
    });
  }

  function wireScriptFilter(items) {
    const input = $id("scriptFilter");
    if (!input) return;
    input.addEventListener("input", () => {
      const q = input.value.trim().toLowerCase();
      const list = q
        ? items.filter((it) => `${it.name} ${it.desc}`.toLowerCase().includes(q))
        : items;
      $id("scriptCount").textContent = String(list.length);
      const rows = list.map((it) => [
        `<code>${esc(it.name)}</code>`,
        `<span class="muted">${esc(it.desc)}</span>`,
      ]);
      const wrap = $id("scriptsWrap");
      if (wrap) wrap.classList.remove("muted");
      $id("scriptsWrap").innerHTML = `<div class="table-scroll">${renderTable(
        ["Script", "Purpose"],
        rows,
        "Scripts"
      )}</div>`;
    });
  }

  function renderAll() {
    renderStaticSections();

    if (state.loaded.hackTypesMd) {
      renderHackTypes(state.loaded.hackTypesMd);
      wireHackFilter(state.loaded.hackTypesMd);
    }
    if (state.loaded.knowledgeIndexMd) {
      renderKnowledgeIndex(state.loaded.knowledgeIndexMd);
      wireKnowledgeFilters();
    }
    if (state.loaded.mkdocsYml) {
      renderDocsForum(state.loaded.mkdocsYml);
      wireDocsForum();
    } else {
      renderDocsForum("");
    }
    if (state.loaded.scriptsReadmeMd) {
      renderScripts(state.loaded.scriptsReadmeMd);
      wireScriptFilter(state.loaded.scripts || []);
    }
    if (state.loaded.bugcrowdBoardMd) {
      const rows = parseBugcrowdBoard(state.loaded.bugcrowdBoardMd, "bounty_board/bugcrowd");
      for (const r of rows) r.sourceKey = "bugcrowd";
      state.loaded.bugcrowdRows = rows;
      renderBugcrowdBoard(rows, "bugcrowdWrap", "bugcrowdCount", "bugcrowdFilter", "bugcrowdSort");
    }
    if (state.loaded.bugcrowdVdpMd) {
      const rows = parseBugcrowdBoard(state.loaded.bugcrowdVdpMd, "bounty_board/bugcrowd_vdp");
      for (const r of rows) r.sourceKey = "bugcrowd_vdp";
      state.loaded.bugcrowdVdpRows = rows;
      renderBugcrowdBoard(
        rows,
        "bugcrowdVdpWrap",
        "bugcrowdVdpCount",
        "bugcrowdVdpFilter",
        "bugcrowdVdpSort"
      );
    }
    if (state.loaded.programRegistryJson) {
      renderProgramRegistry(state.loaded.programRegistryJson);
    }
    if (state.loaded.findingsDbJson) {
      renderFindings(state.loaded.findingsDbJson);
    }
    renderWorkflowTracker(state.loaded.workflowTrackerJson || null);
    wireWorkflowTracker();
    if (state.loaded.roadmapMd) {
      renderRoadmap(state.loaded.roadmapMd);
    }

    const bountyRows = [
      ...(state.loaded.bugcrowdRows || []).map((r) => enrichBountyRow(r, "bugcrowd")),
      ...(state.loaded.bugcrowdVdpRows || []).map((r) => enrichBountyRow(r, "bugcrowd_vdp")),
    ];
    state.loaded.bountyRows = bountyRows;
    renderMostWanted(bountyRows);
    renderBountyLens(bountyRows);
    renderBountyProfiles(bountyRows);
    renderLeaderboards(bountyRows);
    renderBountyTimeline({
      bugcrowdFetchedAt: parseFetchedAt(state.loaded.bugcrowdBoardMd),
      bugcrowdVdpFetchedAt: parseFetchedAt(state.loaded.bugcrowdVdpMd),
      registryUpdatedAt: state.loaded.programRegistryJson
        ? new Date(state.loaded.programRegistryJson.updated_at || "")
        : null,
    });

    renderGlance();

    renderPathList(EXAMPLE_ARTIFACTS, "artifactsWrap", "artifactCount", "artifactFilter");
    renderPathList(EXAMPLE_EXPORTS, "exportsWrap", null, null);
  }

  async function loadAll() {
    state.loaded = {};
    state.errors = [];
    setCounters();
    setBanner("neutral", "Loading...");
    renderErrors();

    async function loadOne(key, def) {
      try {
        state.loaded[key] =
          def.kind === "json" ? await loadJson(def.path) : await loadText(def.path);
      } catch (err) {
        state.errors.push({ key, path: def.path, error: String(err) });
      } finally {
        setCounters();
      }
    }

    await loadOne("hackTypesMd", RESOURCES.hackTypes);
    await loadOne("knowledgeIndexMd", RESOURCES.knowledgeIndex);
    await loadOne("mkdocsYml", RESOURCES.mkdocsConfig);
    await loadOne("scriptsReadmeMd", RESOURCES.scriptsReadme);
    await loadOne("bugcrowdBoardMd", RESOURCES.bugcrowdBoard);
    await loadOne("bugcrowdVdpMd", RESOURCES.bugcrowdVdp);
    await loadOne("programRegistryJson", RESOURCES.programRegistry);
    await loadOne("findingsDbJson", RESOURCES.findingsDb);
    await loadOne("workflowTrackerJson", RESOURCES.workflowTracker);
    await loadOne("roadmapMd", RESOURCES.roadmap);

    try {
      renderAll();
    } catch (err) {
      state.errors.push({ key: "render", error: String(err) });
      setCounters();
    }

    if (state.errors.length === 0) setBanner("ok", "Loaded core repo data.");
    else if (Object.keys(state.loaded).length > 0)
      setBanner(
        "warn",
        `Loaded with ${state.errors.length} error(s). Import folder or run a local server.`
      );
    else setBanner("bad", "Could not load repo data. Import folder or run a local server.");

    renderErrors();
  }

  function init() {
    wireNav();
    wireModal();
    wireImport();
    wireReload();
    wireThemeToggle();
    wireClearLocal();
    wireSearch();
    wireViewSelect();
    wireHashView();

    const storedTheme = loadStoredTheme();
    applyTheme(storedTheme || systemTheme(), { persist: false });

    const hashPage = viewForHash(location.hash);
    const stored = loadStoredView();
    setView(hashPage || stored || "overview", { persist: false });
    if (!location.hash && stored && stored !== "overview") gotoView(stored);

    setCounters();
    loadAll().catch((err) => {
      state.errors.push({ key: "init", error: String(err) });
      setCounters();
      setBanner("bad", "Init failed. Import repo folder.");
    });
  }

  document.addEventListener("DOMContentLoaded", init);
})();
