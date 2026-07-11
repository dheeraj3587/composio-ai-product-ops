"use strict";

const $ = (id) => document.getElementById(id);
const esc = (value) => String(value == null ? "" : value)
  .replace(/&/g, "&amp;")
  .replace(/</g, "&lt;")
  .replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;")
  .replace(/'/g, "&#039;");

const tone = {
  "Self-Serve": "green",
  Gated: "amber",
  Easy: "green",
  Moderate: "blue",
  Hard: "amber",
  Blocked: "red",
  "Build Now": "green",
  "Needs Outreach": "blue",
  "Partner-Gated": "violet",
  Official: "green",
  Community: "blue",
  None: "gray",
  Auto: "gray",
  "Hand-Checked": "green",
  Yes: "green",
  No: "gray",
};

const commandSets = {
  research: [
    "python research.py --batch-submit --fresh-run",
    "python research.py --batch-status",
    "python research.py --batch-collect",
    "python research.py --batch-audit-sources",
    "python research.py --metrics",
    "python research.py --build-report",
  ].join("\n"),
  verify: [
    "python research.py --handcheck-template 18",
    "python research.py --fold-handcheck",
    "python research.py --apply-handcheck",
    "python research.py --accuracy-movement",
    ".venv-browser/bin/python browser_verify.py --sample 12",
  ].join("\n"),
};

let rows = [];
let metrics = {};
let reasoning = {};

const pct = (value) => Number.isFinite(Number(value))
  ? `${Math.round(Number(value) * 100)}%`
  : "Pending";

const pill = (text, kind) => (
  `<span class="pill ${tone[kind || text] || "gray"}">${esc(text || "—")}</span>`
);

function safeUrl(value) {
  try {
    const url = new URL(String(value || ""));
    return ["http:", "https:"].includes(url.protocol) ? url.href : "";
  } catch {
    return "";
  }
}

function compactHost(value) {
  try {
    return new URL(value).hostname.replace(/^www\./, "");
  } catch {
    return "Official docs";
  }
}

function sourcePath(value) {
  try {
    const url = new URL(value);
    return `${url.pathname}${url.search}` || "/";
  } catch {
    return value;
  }
}

function initials(name) {
  const parts = String(name || "")
    .replace(/[^a-zA-Z0-9 ]/g, " ")
    .trim()
    .split(/\s+/)
    .filter(Boolean);
  if (!parts.length) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2);
  return `${parts[0][0]}${parts[1][0]}`;
}

function formatDate(value) {
  if (!value) return "date unavailable";
  const date = new Date(`${value}T00:00:00`);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

async function loadData() {
  if (Array.isArray(window.RESULTS) && window.RESULTS.length) {
    return {
      rows: window.RESULTS,
      metrics: window.METRICS || {},
      reasoning: window.REASONING || {},
    };
  }

  try {
    const [resultData, metricData, reasoningData] = await Promise.all([
      fetch("data/results.json").then((response) => response.json()),
      fetch("data/metrics.json").then((response) => response.json()).catch(() => ({})),
      fetch("data/reasoning.json").then((response) => response.json()).catch(() => ({})),
    ]);
    return {
      rows: resultData || [],
      metrics: metricData || {},
      reasoning: reasoningData || {},
    };
  } catch {
    return { rows: [], metrics: {}, reasoning: {} };
  }
}

function renderHeader() {
  const repo = safeUrl(metrics.repo_url);
  if (repo) {
    $("repo-link").href = repo;
  } else {
    $("repo-link").hidden = true;
  }
}

function renderHero() {
  const patterns = metrics.patterns || {};
  const quality = metrics.quality || {};
  const actions = patterns.recommended_next_action || {};
  const toolkit = patterns.composio_toolkit || {};
  const total = patterns.n || rows.length || 1;
  const buildQueue = rows.filter((row) => (
    row.composio_toolkit === "No" && row.recommended_next_action === "Build Now"
  ));
  const reasoningCount = Object.keys(reasoning).length;

  $("hero-copy").textContent = `${total} requested apps ranked by API surface, authentication, production access, MCP ownership, and buildability.`;
  $("snapshot-copy").textContent = `${quality.source_audited_rows || 0}/${total} rows source-audited`;
  $("generated-note").textContent = `${reasoningCount} reasoning traces · ${formatDate(metrics.generated)}`;
  $("reasoning-count").textContent = `${reasoningCount}/${total}`;
  $("quality-badge").textContent = quality.source_audit_complete ? "Source audit complete" : "Audit incomplete";
  $("decision-title").textContent = `${buildQueue.length} uncovered integrations are ready to build now.`;
  $("decision-summary").textContent = `${toolkit.No || 0} apps have no Composio toolkit. The rest of the queue is separated into access, partnership, and no-build work.`;

  const actionOrder = [
    ["Build Now", "build"],
    ["Needs Outreach", "outreach"],
    ["Partner-Gated", "partner"],
    ["Blocked", "blocked"],
  ];
  $("pulse-chart").innerHTML = actionOrder.map(([label, cssClass]) => {
    const value = Number(actions[label] || 0);
    const height = value ? Math.max(18, Math.round(22 + (value / total) * 55)) : 2;
    return `<span class="pulse-segment ${cssClass}" style="flex:${Math.max(value, 1)};height:${height}px" title="${esc(label)}: ${value}"></span>`;
  }).join("");
  $("pulse-legend").innerHTML = actionOrder.map(([label, cssClass]) => (
    `<span class="legend-item"><i class="${cssClass}"></i>${esc(label)} <b>${actions[label] || 0}</b></span>`
  )).join("");
}

function renderMetrics() {
  const patterns = metrics.patterns || {};
  const access = patterns.access_model || {};
  const toolkit = patterns.composio_toolkit || {};
  const actions = patterns.recommended_next_action || {};
  const handcheck = metrics.handcheck || {};
  const cards = [
    [access["Self-Serve"] || 0, "Self-serve paths", "Credentials available without manual production approval"],
    [patterns.build_now || actions["Build Now"] || 0, "Ready to build", "Usable API surface and a clear implementation path"],
    [actions["Needs Outreach"] || 0, "Needs outreach", "Customer, vendor, or account access is the next move"],
    [toolkit.No || 0, "Toolkit gaps", "Requested apps not currently covered by Composio"],
    [handcheck.n ? pct(handcheck.accuracy) : "—", "First-pass accuracy", `${handcheck.n || 0} priority apps checked against official docs`],
  ];

  $("metrics").innerHTML = cards.map(([value, label, note], index) => `
    <article class="metric-card">
      <div class="metric-top"><span class="metric-label">${esc(label)}</span><span class="metric-index">0${index + 1}</span></div>
      <div>
        <div class="metric-value">${esc(value)}</div>
        <p class="metric-foot">${esc(note)}</p>
      </div>
    </article>
  `).join("");
}

function renderInsights() {
  const patterns = metrics.patterns || {};
  const topAuth = (patterns.auth_methods_top || [])[0] || ["OAuth2", 0];
  const uncovered = rows.filter((row) => row.composio_toolkit === "No");
  const buildable = uncovered.filter((row) => row.recommended_next_action === "Build Now");
  const gated = rows.filter((row) => row.api_type !== "None" && row.access_model?.kind === "Gated");
  const officialMcp = rows.filter((row) => row.existing_mcp === "Official");
  const cards = [
    ["Immediate queue", `${buildable.length} build-ready apps have no Composio toolkit. These are the cleanest engineering opportunities.`],
    ["Access is the real blocker", `${gated.length} apps expose a usable API but require payment, approval, verification, partnership, or an existing customer account.`],
    ["MCP changes the build decision", `${officialMcp.length} vendors already publish an official MCP server. ${topAuth[0]} is the most common auth pattern across the catalog.`],
  ];

  $("insights").innerHTML = cards.map(([title, body]) => `
    <article class="insight-item"><h3>${esc(title)}</h3><p>${esc(body)}</p></article>
  `).join("");
}

function queueItem(record) {
  return `
    <li class="queue-item">
      <span class="app-avatar" aria-hidden="true">${esc(initials(record.app))}</span>
      <span class="queue-name"><b>${esc(record.app)}</b><small>${esc(record.category)}</small></span>
      <span class="queue-score">${Math.round(Number(record.confidence || 0) * 100)}%</span>
    </li>
  `;
}

function renderPriorityQueue() {
  const confidence = (record) => Number(record.confidence || 0);
  const build = rows
    .filter((row) => row.composio_toolkit === "No" && row.recommended_next_action === "Build Now")
    .sort((a, b) => confidence(b) - confidence(a) || a.app.localeCompare(b.app))
    .slice(0, 6);
  const access = rows
    .filter((row) => ["Needs Outreach", "Partner-Gated"].includes(row.recommended_next_action))
    .sort((a, b) => confidence(b) - confidence(a) || a.app.localeCompare(b.app))
    .slice(0, 6);
  const mcp = rows
    .filter((row) => row.existing_mcp === "Official")
    .sort((a, b) => confidence(b) - confidence(a) || a.app.localeCompare(b.app))
    .slice(0, 6);
  const cards = [
    ["Build next", "Uncovered and build-ready", build],
    ["Open access", "Approval or customer access", access],
    ["Use vendor MCP", "Official server already exists", mcp],
  ];

  $("priority-queue").innerHTML = cards.map(([title, subtitle, list]) => `
    <article class="queue-card">
      <header class="queue-card-head">
        <div><h3>${esc(title)}</h3><p>${esc(subtitle)}</p></div>
        <span>${list.length} shown</span>
      </header>
      <ol class="queue-list">${list.map(queueItem).join("")}</ol>
    </article>
  `).join("");
}

function initFilters() {
  const categories = [...new Set(rows.map((row) => row.category).filter(Boolean))].sort();
  const actions = [...new Set(rows.map((row) => row.recommended_next_action).filter(Boolean))].sort();
  const builds = ["Easy", "Moderate", "Hard", "Blocked"];

  categories.forEach((value) => $("f-cat").insertAdjacentHTML(
    "beforeend",
    `<option value="${esc(value)}">${esc(value)}</option>`,
  ));
  actions.forEach((value) => $("f-next").insertAdjacentHTML(
    "beforeend",
    `<option value="${esc(value)}">${esc(value)}</option>`,
  ));
  builds.forEach((value) => $("f-build").insertAdjacentHTML(
    "beforeend",
    `<option value="${esc(value)}">${esc(value)}</option>`,
  ));

  ["q", "f-cat", "f-next", "f-build"].forEach((id) => {
    $(id).addEventListener("input", renderTable);
  });
}

function renderTable() {
  const query = $("q").value.trim().toLowerCase();
  const category = $("f-cat").value;
  const action = $("f-next").value;
  const build = $("f-build").value;
  const actionRank = { "Build Now": 0, "Needs Outreach": 1, "Partner-Gated": 2, Blocked: 3 };

  const visible = rows.filter((row) => {
    if (category && row.category !== category) return false;
    if (action && row.recommended_next_action !== action) return false;
    if (build && row.buildability !== build) return false;
    if (!query) return true;
    return [
      row.app,
      row.category,
      row.one_liner,
      (row.auth_methods || []).join(" "),
      row.main_blocker,
      row.recommended_next_action,
    ].join(" ").toLowerCase().includes(query);
  }).sort((a, b) => (
    (actionRank[a.recommended_next_action] ?? 9) - (actionRank[b.recommended_next_action] ?? 9)
    || Number(b.confidence || 0) - Number(a.confidence || 0)
    || a.app.localeCompare(b.app)
  ));

  $("matrix-count").textContent = `${visible.length} of ${rows.length} apps`;
  $("matrix-body").innerHTML = visible.map((record) => {
    const confidence = Math.round(Number(record.confidence || 0) * 100);
    const auth = (record.auth_methods || []).join(", ") || "—";
    const hasReasoning = Boolean(reasoning[record.slug]);
    return `
      <tr>
        <td>
          <div class="app-cell">
            <span class="app-avatar" aria-hidden="true">${esc(initials(record.app))}</span>
            <span class="app-meta"><b>${esc(record.app)}</b><span>${esc(record.category)}</span></span>
          </div>
        </td>
        <td><span class="truncate" title="${esc(auth)}">${esc(auth)}</span></td>
        <td>${pill(record.access_model?.kind, record.access_model?.kind)}</td>
        <td><span class="truncate" title="${esc(record.api_type)} · ${esc(record.api_breadth)}">${esc(record.api_type)} · ${esc(record.api_breadth)}</span></td>
        <td>${pill(record.existing_mcp, record.existing_mcp)}</td>
        <td>${pill(record.composio_toolkit, record.composio_toolkit)}</td>
        <td>${pill(record.buildability, record.buildability)}</td>
        <td>${pill(record.recommended_next_action, record.recommended_next_action)}</td>
        <td>
          <div class="confidence-cell" aria-label="${confidence}% confidence">
            <span>${confidence}</span>
            <span class="confidence-track"><span class="confidence-fill" style="width:${confidence}%"></span></span>
          </div>
        </td>
        <td><button class="review-button" type="button" data-slug="${esc(record.slug)}" data-testid="reasoning-${esc(record.slug)}">${hasReasoning ? "Reasoning" : "Details"}</button></td>
      </tr>
    `;
  }).join("");
}

function markdownSection(raw, heading) {
  const marker = `## ${heading}`;
  const start = String(raw || "").indexOf(marker);
  if (start < 0) return "";
  const contentStart = start + marker.length;
  const remainder = raw.slice(contentStart).replace(/^\s+/, "");
  const next = remainder.search(/\n##\s+/);
  return (next >= 0 ? remainder.slice(0, next) : remainder).trim();
}

function stripMarkdown(value) {
  return String(value || "")
    .replace(/\*\*/g, "")
    .replace(/^[-*]\s+/gm, "")
    .replace(/`([^`]+)`/g, "$1")
    .trim();
}

function parseResearchTrace(raw) {
  const section = markdownSection(raw, "Research trace");
  const lines = section.split("\n").map((line) => line.trim()).filter(Boolean);
  const queryLine = lines.find((line) => line.startsWith("- queries:")) || "";
  const qualityLine = lines.find((line) => line.startsWith("- evidence quality:")) || "";
  const sources = lines.map((line) => {
    const match = line.match(/^- (https?:\/\/\S+) \| HTTP (\d+) \| ([^|]+) \| topics=(.+)$/);
    if (!match) return null;
    return { url: match[1], status: Number(match[2]), kind: match[3].trim(), topics: match[4].trim() };
  }).filter(Boolean);
  return {
    queries: stripMarkdown(queryLine.replace("- queries:", "")),
    quality: stripMarkdown(qualityLine.replace("- evidence quality:", "")) || "unknown",
    sources,
  };
}

function handcheckFor(record) {
  const handcheck = metrics.handcheck || {};
  const checked = (handcheck.checked || []).find((item) => item.slug === record.slug);
  const misses = (handcheck.misses || []).filter((item) => item.slug === record.slug);
  return { checked, misses };
}

function evidenceMarkup(record) {
  const urls = [];
  [...(record.evidence_urls || []), record.primary_docs_url].forEach((value) => {
    const url = safeUrl(value);
    if (url && !urls.includes(url)) urls.push(url);
  });
  if (!urls.length) return "<p>No valid evidence URL was retained for this record.</p>";
  return `<ul class="evidence-list">${urls.map((url, index) => `
    <li>
      <a href="${esc(url)}" target="_blank" rel="noopener">
        <span class="source-index">0${index + 1}</span>
        <span class="source-copy"><b>${esc(compactHost(url))}</b><small>${esc(sourcePath(url))}</small></span>
        <span class="source-arrow" aria-hidden="true">↗</span>
      </a>
    </li>
  `).join("")}</ul>`;
}

function traceMarkup(trace) {
  if (!trace.sources.length && !trace.queries) {
    return "<p>The original fetch trace is not available in this build.</p>";
  }
  const query = trace.queries
    ? `<div class="trace-query">${esc(trace.queries)}</div>`
    : "";
  const sources = trace.sources.length
    ? `<ul class="trace-list">${trace.sources.map((source) => `
        <li class="trace-item">
          <span class="trace-status ${source.status >= 400 ? "bad" : ""}">HTTP ${source.status}</span>
          <span class="trace-url" title="${esc(source.url)}">${esc(source.url)}</span>
          <span class="trace-kind">${esc(source.kind)}</span>
        </li>
      `).join("")}</ul>`
    : "";
  return `${query}${sources}`;
}

function verificationMarkup(record) {
  const { checked, misses } = handcheckFor(record);
  if (!checked) {
    return `
      <div class="verification-note">
        <p><b>Source-audited, not hand-checked.</b> This row passed schema, citation, identity, and claim-coverage checks but was not part of the 10-app human ground-truth sample.</p>
      </div>
    `;
  }
  if (!misses.length) {
    return `
      <div class="verification-note">
        <p><b>Matched official docs.</b> API type, canonical auth set, production access, and MCP ownership all matched the human adjudication.</p>
      </div>
    `;
  }
  return `
    <div class="verification-note missed">
      <p><b>${misses.length} first-pass mismatch${misses.length === 1 ? "" : "es"}, corrected after review.</b></p>
      <ul class="miss-list">${misses.map((miss) => `
        <li><b>${esc(miss.field)}</b>: ${esc(miss.notes)}</li>
      `).join("")}</ul>
    </div>
  `;
}

function openReasoning(slug, updateUrl = true) {
  const record = rows.find((item) => item.slug === slug);
  if (!record) return;
  const raw = reasoning[slug] || "";
  const modelReasoning = stripMarkdown(markdownSection(raw, "Model reasoning"));
  const trace = parseResearchTrace(raw);
  const metaLine = raw.split("\n").find((line) => line.startsWith("_generated ")) || "";
  const meta = stripMarkdown(metaLine.replace(/^_+|_+$/g, ""));
  const confidence = Math.round(Number(record.confidence || 0) * 100);
  const adjudication = handcheckFor(record);
  const dialog = $("reasoning-dialog");

  $("reasoning-title").textContent = record.app;
  $("reasoning-subtitle").textContent = `${record.category} · ${record.verification_status} · ${meta || `verified ${record.last_verified || "—"}`}`;
  $("reasoning-content").innerHTML = `
    <div class="drawer-summary">
      <div class="drawer-stat"><span>Recommendation</span><b>${esc(record.recommended_next_action)}</b></div>
      <div class="drawer-stat"><span>Production access</span><b>${esc(record.access_model?.kind || "—")}</b></div>
      <div class="drawer-stat"><span>Confidence</span><b>${confidence}%</b></div>
    </div>

    ${adjudication.misses.length ? `
      <div class="adjudication-alert">
        <b>Human correction applied</b>
        <p>${adjudication.misses.length} first-pass field${adjudication.misses.length === 1 ? " was" : "s were"} corrected against official docs. The model paragraph below is preserved verbatim; the decision details are the final adjudicated record.</p>
      </div>
    ` : ""}

    <section class="drawer-section">
      <div class="drawer-section-head"><h3>Model reasoning</h3><span class="pill blue">Verbatim trace</span></div>
      ${modelReasoning
        ? `<div class="model-note"><p>${esc(modelReasoning)}</p></div>`
        : `<div class="empty-reasoning"><p>No model-reasoning paragraph was packaged for this record.</p></div>`}
    </section>

    <section class="drawer-section">
      <div class="drawer-section-head"><h3>Decision details</h3></div>
      <dl class="decision-list">
        <div class="decision-row"><dt>Summary</dt><dd>${esc(record.one_liner)}</dd></div>
        <div class="decision-row"><dt>Authentication</dt><dd>${esc((record.auth_methods || []).join(", ") || "—")}</dd></div>
        <div class="decision-row"><dt>API surface</dt><dd>${esc(record.api_type)} · ${esc(record.api_breadth)}</dd></div>
        <div class="decision-row"><dt>Access rule</dt><dd>${esc(record.access_model?.note || "—")}</dd></div>
        <div class="decision-row"><dt>Existing MCP</dt><dd>${esc(record.existing_mcp)}</dd></div>
        <div class="decision-row"><dt>Composio toolkit</dt><dd>${esc(record.composio_toolkit)}</dd></div>
        <div class="decision-row"><dt>Buildability</dt><dd>${esc(record.buildability)}</dd></div>
        <div class="decision-row"><dt>Main blocker</dt><dd>${esc(record.main_blocker || "None recorded")}</dd></div>
        <div class="decision-row"><dt>Rate limits</dt><dd>${esc(record.rate_limit_note || "Not documented")}</dd></div>
      </dl>
    </section>

    <section class="drawer-section">
      <div class="drawer-section-head"><h3>Verification status</h3>${pill(record.verification_status, record.verification_status)}</div>
      ${verificationMarkup(record)}
    </section>

    <section class="drawer-section">
      <div class="drawer-section-head"><h3>Official evidence</h3><span class="pill gray">${(record.evidence_urls || []).length} cited</span></div>
      ${evidenceMarkup(record)}
    </section>

    <section class="drawer-section">
      <div class="drawer-section-head"><h3>Research trace</h3><span class="pill ${trace.quality === "adequate" ? "green" : "amber"}">${esc(trace.quality)}</span></div>
      ${traceMarkup(trace)}
    </section>
  `;

  if (!dialog.open) dialog.showModal();
  document.body.classList.add("dialog-open");
  if (updateUrl) {
    try {
      const url = new URL(window.location.href);
      url.searchParams.set("app", slug);
      window.history.replaceState({}, "", url);
    } catch {
      // Local file previews can disallow history changes; the drawer still works.
    }
  }
}

function closeReasoningUrl() {
  document.body.classList.remove("dialog-open");
  try {
    const url = new URL(window.location.href);
    if (url.searchParams.has("app")) {
      url.searchParams.delete("app");
      window.history.replaceState({}, "", url);
    }
  } catch {
    // See openReasoning: file:// history is browser-dependent.
  }
}

function renderVerification() {
  const quality = metrics.quality || {};
  const handcheck = metrics.handcheck || {};
  const movement = metrics.accuracy_movement || {};
  const browserUse = metrics.browser_use || {};
  const misses = handcheck.misses || [];
  const checkedPills = (handcheck.checked || []).map((item) => {
    const missed = misses.some((miss) => miss.slug === item.slug);
    return pill(`${item.app}${missed ? " · corrected" : ""}`, missed ? "Hard" : "Self-Serve");
  }).join("");

  const cards = [
    {
      title: "Source quality gate",
      value: quality.source_audit_complete ? `${quality.source_audited_rows}/${rows.length}` : "Open",
      body: "Rows must pass schema, citation, app identity, claim coverage, and first-party source checks.",
      detail: `<span class="pill green">${quality.source_audit_complete ? "Complete" : "Incomplete"}</span>`,
    },
    {
      title: "Human ground truth",
      value: handcheck.n ? pct(handcheck.accuracy) : "Pending",
      body: `${handcheck.n || 0} priority apps checked against official documentation. The score is the uncorrected first-pass result.`,
      detail: checkedPills,
      misses,
    },
    {
      title: "After adjudication",
      value: movement.post_verification_accuracy != null ? pct(movement.post_verification_accuracy) : "Pending",
      body: movement.first_pass_accuracy != null
        ? `${pct(movement.first_pass_accuracy)} first pass to ${pct(movement.post_verification_accuracy)} after applying the same verified truth set. ${(movement.improved_apps || []).length} apps improved; ${(movement.regressed_apps || []).length} regressed.`
        : "Accuracy movement has not been calculated for this run.",
      detail: `<span class="pill green">${(movement.improved_apps || []).length} improved</span><span class="pill gray">${(movement.regressed_apps || []).length} regressed</span>`,
    },
    {
      title: "Browser-read evidence",
      value: quality.browser_evidence_pages || browserUse.n_checked || 0,
      body: quality.browser_evidence_pages
        ? `${quality.browser_evidence_pages} official pages across ${quality.browser_evidence_apps || 0} difficult apps were read in-browser when direct fetching was incomplete.`
        : "No browser-assisted evidence was required for this run.",
      detail: "<span class=\"pill blue\">Evidence acquisition</span>",
    },
  ];

  $("verification-grid").innerHTML = cards.map((card) => `
    <article class="verification-card">
      <div class="verification-card-head"><h3>${esc(card.title)}</h3><span class="verification-value">${esc(card.value)}</span></div>
      <p>${esc(card.body)}</p>
      <div class="verification-detail">${card.detail}</div>
      ${card.misses?.length ? `
        <details>
          <summary>Inspect ${card.misses.length} first-pass mismatch${card.misses.length === 1 ? "" : "es"}</summary>
          <ul class="miss-list">${card.misses.map((miss) => `<li><b>${esc(miss.app)} · ${esc(miss.field)}</b>: ${esc(miss.notes)}</li>`).join("")}</ul>
        </details>
      ` : ""}
    </article>
  `).join("");

  const warnings = [];
  if (!handcheck.n) warnings.push("Independent human accuracy is pending for this run.");
  $("verification-warning").innerHTML = warnings.length
    ? `<div class="warning">${esc(warnings.join(" "))}</div>`
    : "";
}

function renderFooter() {
  const repo = safeUrl(metrics.repo_url);
  const live = safeUrl(metrics.live_url);
  const links = [
    repo ? `<a href="${esc(repo)}" target="_blank" rel="noopener">GitHub repository ↗</a>` : "",
    live ? `<a href="${esc(live)}" target="_blank" rel="noopener">Live report ↗</a>` : "",
  ].filter(Boolean).join("");
  $("footer").innerHTML = `
    <p>Locked 19-field schema · ${rows.length} apps · generated ${esc(formatDate(metrics.generated))}</p>
    <div class="footer-links">${links}</div>
  `;
}

function bindInteractions() {
  $("matrix-body").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-slug]");
    if (button) openReasoning(button.dataset.slug);
  });

  $("reasoning-dialog").addEventListener("close", closeReasoningUrl);
  $("reasoning-dialog").addEventListener("click", (event) => {
    if (event.target === $("reasoning-dialog")) $("reasoning-dialog").close();
  });

  document.querySelectorAll(".command-tab").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".command-tab").forEach((item) => {
        const active = item === button;
        item.classList.toggle("active", active);
        item.setAttribute("aria-selected", String(active));
      });
      $("command-output").textContent = commandSets[button.dataset.command];
    });
  });
}

async function init() {
  const loaded = await loadData();
  rows = loaded.rows || [];
  metrics = loaded.metrics || {};
  reasoning = loaded.reasoning || {};

  if (!rows.length) {
    $("hero-copy").textContent = "No report data is packaged yet. Run python research.py --build-report.";
  }

  renderHeader();
  renderHero();
  renderMetrics();
  renderInsights();
  renderPriorityQueue();
  initFilters();
  renderTable();
  renderVerification();
  renderFooter();
  bindInteractions();

  const requestedSlug = new URLSearchParams(window.location.search).get("app");
  if (requestedSlug && rows.some((row) => row.slug === requestedSlug)) {
    openReasoning(requestedSlug, false);
  }
}

document.addEventListener("DOMContentLoaded", init);
