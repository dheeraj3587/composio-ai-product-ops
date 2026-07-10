"use strict";

const $ = (id) => document.getElementById(id);
const esc = (value) => String(value == null ? "" : value)
  .replace(/&/g, "&amp;")
  .replace(/</g, "&lt;")
  .replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;");

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

const pct = (n) => (Number.isFinite(n) ? `${Math.round(n * 100)}%` : "Pending");
const num = (value, fallback = "0") => value == null ? fallback : String(value);
const pill = (text, kind) => `<span class="pill ${tone[kind || text] || "gray"}">${esc(text || "—")}</span>`;
// zero stays zero — a 3% sliver for a 0-count bar would misreport the data
const width = (value, max) => `${value > 0 && max > 0 ? Math.max(3, Math.round((value / max) * 100)) : 0}%`;
const docsHints = ["docs", "developer", "api", "reference", "learn", "help", "github", "postman"];
const weakerHints = ["blog", "moldstud", "apitracker", "aeroleads", "vohrtech", "grokipedia"];

let rows = [];
let metrics = {};

async function loadData() {
  if (Array.isArray(window.RESULTS) && window.RESULTS.length) {
    return { rows: window.RESULTS, metrics: window.METRICS || {} };
  }
  try {
    const [resultData, metricData] = await Promise.all([
      fetch("data/results.json").then((res) => res.json()),
      fetch("data/metrics.json").then((res) => res.json()).catch(() => ({})),
    ]);
    return { rows: resultData || [], metrics: metricData || {} };
  } catch {
    return { rows: [], metrics: {} };
  }
}

function renderStatus() {
  const p = metrics.patterns || {};
  const h = metrics.handcheck || {};
  const q = metrics.quality || {};
  const lines = [
    ["Source audit", q.source_audit_complete ? `${q.source_audited_rows} / ${p.n || rows.length}` : "Incomplete"],
    ["Human checked", h.n ? `${h.n} apps` : "Pending"],
    ["Accuracy", h.n ? pct(h.accuracy) : "Pending"],
  ];
  $("status-lines").innerHTML = lines.map(([label, value]) => `
    <div class="status-line"><b>${esc(label)}</b><span>${esc(value)}</span></div>
  `).join("");
}

function renderHeroFacts() {
  const p = metrics.patterns || {};
  const h = metrics.handcheck || {};
  const mcp = p.existing_mcp || {};
  const q = metrics.quality || {};
  const facts = [
    [p.n || rows.length, "apps researched"],
    [q.source_audited_rows || "-", "source-audited rows"],
    [mcp.Official || 0, "vendor MCP servers"],
  ];
  $("hero-facts").innerHTML = facts.map(([value, label]) => `
    <span><b>${esc(value)}</b>${esc(label)}</span>
  `).join("");
}

function renderDecisionBoard() {
  const p = metrics.patterns || {};
  const actions = p.recommended_next_action || {};
  const total = p.n || rows.length || 1;
  const buildQueue = rows.filter((row) =>
    row.composio_toolkit === "No" && row.recommended_next_action === "Build Now"
  );
  const decisionRows = [
    ["Build queue", buildQueue.length],
    ["Needs Outreach", actions["Needs Outreach"] || 0],
    ["Partner-Gated", actions["Partner-Gated"] || 0],
    ["Blocked", actions.Blocked || 0],
  ];
  $("page-title").textContent = `${buildQueue.length} toolkit gaps are ready to build.`;
  $("hero-copy").textContent = `${num(p.n || rows.length)} requested apps ranked by API surface, auth, access, and buildability. This queue excludes apps Composio already covers.`;
  $("decision-title").textContent = `${buildQueue.length} buildable apps have no Composio toolkit yet.`;
  $("decision-summary").textContent = "Build this queue first. Route the rest into outreach, partnership, or no-build decisions.";
  $("decision-list").innerHTML = decisionRows.map(([label, value]) => `
    <div class="decision-row">
      <span>${esc(label)}</span>
      <div class="meter"><div class="meter-fill" style="width:${width(value, total)}"></div></div>
      <b>${esc(value)}</b>
    </div>
  `).join("");
}

function evidenceScore(url) {
  const u = String(url || "").toLowerCase();
  const docs = docsHints.some((hint) => u.includes(hint)) ? 1 : 0;
  const exact = u.includes("/api") || u.includes("api.") || u.includes("developer") || u.includes("docs.") ? 1 : 0;
  const auth = u.includes("auth") ? 1 : 0;
  const officialish = weakerHints.some((hint) => u.includes(hint)) ? 0 : 1;
  return docs * 1000 + exact * 200 + auth * 40 + officialish * 20 - Math.min(u.length, 220) / 220;
}

function bestEvidence(record) {
  const urls = [];
  for (const value of [...(record.evidence_urls || []), record.primary_docs_url]) {
    if (typeof value === "string" && value.startsWith("http") && !urls.includes(value)) urls.push(value);
  }
  return urls.sort((a, b) => evidenceScore(b) - evidenceScore(a))[0] || "";
}

function compactHost(url) {
  try {
    const host = new URL(url).hostname.replace(/^www\./, "");
    if (host.includes("github.com")) return "github";
    if (host.includes("postman.com")) return "postman";
    if (host.includes("developer")) return "developer docs";
    if (host.includes("docs")) return "docs";
    if (host.includes("api")) return "api docs";
    return host.split(".").slice(0, 2).join(".");
  } catch {
    return "docs";
  }
}

function renderMetrics() {
  const p = metrics.patterns || {};
  const access = p.access_model || {};
  const toolkit = p.composio_toolkit || {};
  const h = metrics.handcheck || {};
  const actions = p.recommended_next_action || {};
  const data = [
    [access["Self-Serve"] || 0, "self-serve paths"],
    [p.build_now || 0, "ready to build"],
    [actions["Needs Outreach"] || 0, "needs outreach"],
    [toolkit.No || 0, "Composio gaps"],
    [h.n ? pct(h.accuracy) : "Pending", "human check"],
  ];
  $("metrics").innerHTML = data.map(([value, label]) => `
    <article class="metric">
      <div class="value">${esc(value)}</div>
      <div class="label">${esc(label)}</div>
    </article>
  `).join("");
}

function renderInsights() {
  const p = metrics.patterns || {};
  const access = p.access_model || {};
  const gatedApi = rows.filter((r) => r.api_type !== "None" && r.access_model?.kind === "Gated");
  const noToolkit = rows.filter((r) => r.composio_toolkit === "No");
  const whitespace = noToolkit.filter((r) => r.recommended_next_action === "Build Now");
  const topAuth = (p.auth_methods_top || [])[0] || ["API Key / OAuth", 0];

  const cards = [
    [
      "Immediate build queue",
      `${whitespace.length} self-serve, Build Now apps have no Composio toolkit. Start here.`,
    ],
    [
      "Access queue",
      `${gatedApi.length} apps have usable APIs but need approval, verification, or customer access.`,
    ],
    [
      "Standard connector patterns",
      `${topAuth[0]} is the largest auth bucket (${topAuth[1]} apps). Most build work uses familiar credential flows.`,
    ],
  ];

  $("insights").innerHTML = cards.map(([title, body]) => `
    <article class="insight">
      <h3>${esc(title)}</h3>
      <p>${esc(body)}</p>
    </article>
  `).join("");
  const conf = Number(p.avg_confidence);
  $("generated-note").textContent = `Generated ${metrics.generated || "—"} · avg confidence ${Number.isFinite(conf) ? conf.toFixed(3) : "—"}`;
}

function renderPriorityQueue() {
  const confidence = (r) => Number(r.confidence || 0);
  const short = (r) => `<li><span>${esc(r.app)}</span><small>${esc(r.category)}</small></li>`;
  const build = rows
    .filter((r) => r.composio_toolkit === "No" && r.recommended_next_action === "Build Now")
    .sort((a, b) => confidence(b) - confidence(a) || a.app.localeCompare(b.app))
    .slice(0, 6);
  const outreach = rows
    .filter((r) => ["Needs Outreach", "Partner-Gated", "Blocked"].includes(r.recommended_next_action))
    .sort((a, b) => {
      const order = { "Needs Outreach": 0, "Partner-Gated": 1, Blocked: 2 };
      return order[a.recommended_next_action] - order[b.recommended_next_action] || a.category.localeCompare(b.category);
    })
    .slice(0, 6);
  const mcp = rows
    .filter((r) => r.existing_mcp === "Official")
    .sort((a, b) => a.category.localeCompare(b.category) || a.app.localeCompare(b.app))
    .slice(0, 6);
  const cards = [
    ["Build next", build, "Self-serve gaps"],
    ["Open access", outreach, "Approval or partner work"],
    ["Existing MCP", mcp, "Vendor server available"],
  ];
  $("priority-queue").innerHTML = cards.map(([title, list, subtitle]) => `
    <article class="queue-card">
      <h3>${esc(title)} <span class="subtle" style="font-weight:400; letter-spacing:0; text-transform:none">· ${esc(subtitle)}</span></h3>
      <ol>${list.map(short).join("") || "<li><span>None</span><small>—</small></li>"}</ol>
    </article>
  `).join("");
}

function bars(items, colorMap = {}) {
  const entries = Object.entries(items || {}).sort((a, b) => b[1] - a[1]);
  const max = Math.max(1, ...entries.map(([, value]) => value));
  return entries.map(([name, value]) => `
    <div class="bar">
      <div class="bar-name" title="${esc(name)}">${esc(name)}</div>
      <div class="track"><div class="fill ${colorMap[name] || "blue"}" style="width:${width(value, max)}"></div></div>
      <div class="bar-value">${esc(value)}</div>
    </div>
  `).join("");
}

function renderCharts() {
  const p = metrics.patterns || {};
  const cat = p.access_by_category || {};
  const categoryBars = Object.entries(cat).map(([name, counts]) => {
    const self = counts["Self-Serve"] || 0;
    const gated = counts.Gated || 0;
    const total = Math.max(1, self + gated);
    return `
      <div class="bar">
        <div class="bar-name" title="${esc(name)}">${esc(name)}</div>
        <div class="track" aria-label="${esc(name)} access split">
          <div class="fill green" style="width:${width(self, total)}; float:left"></div>
          <div class="fill amber" style="width:${width(gated, total)}; float:left"></div>
        </div>
        <div class="bar-value">${self}/${gated}</div>
      </div>
    `;
  }).join("");
  $("category-bars").innerHTML = categoryBars || "<p class=\"subtle\">No category data yet.</p>";

  $("action-bars").innerHTML = [
    "<p class=\"chart-title\" style=\"margin-top:0\">Recommended next action</p>",
    bars(p.recommended_next_action, {
      "Build Now": "green",
      "Needs Outreach": "blue",
      "Partner-Gated": "violet",
      Blocked: "red",
    }),
    "<p class=\"chart-title\" style=\"margin-top:22px\">API type</p>",
    bars(p.api_type, { REST: "green", GraphQL: "blue", SDK: "violet", None: "red" }),
  ].join("");
}

function initFilters() {
  const cats = [...new Set(rows.map((r) => r.category))].sort();
  const actions = [...new Set(rows.map((r) => r.recommended_next_action))].sort();
  const builds = ["Easy", "Moderate", "Hard", "Blocked"];

  for (const value of cats) $("f-cat").insertAdjacentHTML("beforeend", `<option>${esc(value)}</option>`);
  for (const value of actions) $("f-next").insertAdjacentHTML("beforeend", `<option>${esc(value)}</option>`);
  for (const value of builds) $("f-build").insertAdjacentHTML("beforeend", `<option>${esc(value)}</option>`);

  ["q", "f-cat", "f-next", "f-build"].forEach((id) => $(id).addEventListener("input", renderTable));
}

function renderTable() {
  const query = $("q").value.trim().toLowerCase();
  const category = $("f-cat").value;
  const action = $("f-next").value;
  const build = $("f-build").value;

  let visible = rows.filter((r) => {
    if (category && r.category !== category) return false;
    if (action && r.recommended_next_action !== action) return false;
    if (build && r.buildability !== build) return false;
    if (!query) return true;
    return [
      r.app,
      r.category,
      r.one_liner,
      (r.auth_methods || []).join(" "),
      r.main_blocker,
      r.recommended_next_action,
    ].join(" ").toLowerCase().includes(query);
  });

  visible = visible.sort((a, b) => a.category.localeCompare(b.category) || a.app.localeCompare(b.app));
  $("matrix-count").textContent = `${visible.length} of ${rows.length} shown`;
  $("matrix-body").innerHTML = visible.map((r) => {
    const evidence = bestEvidence(r);
    const evidenceLink = evidence
      ? `<a href="${esc(evidence)}" target="_blank" rel="noopener">${esc(compactHost(evidence))}</a><span class="subtle"> · ${(r.evidence_urls || []).length}</span>`
      : "<span class=\"subtle\">missing</span>";
    return `
      <tr title="${esc(r.main_blocker || r.one_liner || "")}">
        <td><div class="app-name">${esc(r.app)}</div><div class="subtle">${esc(r.one_liner || "")}</div></td>
        <td>${esc(r.category)}</td>
        <td>${esc((r.auth_methods || []).join(", ") || "—")}</td>
        <td>${pill(r.access_model?.kind, r.access_model?.kind)}</td>
        <td>${esc(r.api_type)} <span class="subtle">· ${esc(r.api_breadth)}</span></td>
        <td>${pill(r.existing_mcp, r.existing_mcp)}</td>
        <td>${pill(r.composio_toolkit, r.composio_toolkit)}</td>
        <td>${pill(r.buildability, r.buildability)}</td>
        <td>${pill(r.recommended_next_action, r.recommended_next_action)}</td>
        <td>${esc(r.confidence)}</td>
        <td>${evidenceLink}</td>
      </tr>
    `;
  }).join("");
}

function renderVerification() {
  const h = metrics.handcheck || {};
  const v = metrics.verification || {};
  const am = metrics.accuracy_movement || {};
  const unresolved = metrics.unresolved_failures || [];
  const q = metrics.quality || {};
  const handText = h.n
    ? `${h.n} official-doc checks: API ${pct(h.api_type_accuracy)}, auth ${pct(h.auth_accuracy)}, access ${pct(h.access_accuracy)}${h.mcp_accuracy != null ? `, MCP ${pct(h.mcp_accuracy)}` : ""}. Overall ${pct(h.accuracy)}; ${(h.misses || []).length} mismatches shown below.`
    : "Independent human adjudication is pending for this fresh run. The legacy score was not carried forward because its access rubric was different.";
  const blindText = v.n_verified
    ? `${v.n_verified} fresh-source re-checks; agreement ${pct(v.overall_agreement_rate)}. This measures reproducibility, not accuracy.`
    : "No blind re-search agreement has been recorded yet.";
  const bu = metrics.browser_use || {};
  const browserDisagreements = bu.n_disagreements != null
    ? bu.n_disagreements
    : bu.n_corrections_found;
  const browserAccepted = bu.n_adjudicated_corrections;
  const browserText = bu.n_checked
    ? (browserAccepted != null
      ? `${bu.n_checked} live-doc checks produced ${browserDisagreements} disagreements; ${browserAccepted} became accepted corrections after human adjudication.`
      : `${bu.n_checked} live-doc checks produced ${browserDisagreements} disagreements. This legacy snapshot did not store field-level adjudication state.`)
    : (q.browser_evidence_pages
      ? `${q.browser_evidence_pages} official pages across ${q.browser_evidence_apps} difficult apps were read in-browser when direct fetching was incomplete. This is evidence acquisition, not an accuracy score.`
      : "No browser-assisted evidence is recorded for this run.");
  const moveText = (am.first_pass_accuracy != null)
    ? `Measured sample: ${pct(am.first_pass_accuracy)} first pass to ${pct(am.post_verification_accuracy)} after review. ${(am.improved_apps || []).length} improved; ${(am.regressed_apps || []).length} regressed.`
    : "";

  const missBy = {};
  (h.misses || []).forEach((m) => {
    const f = String(m.field || "").replace("_methods", "").replace("_model", "");
    (missBy[m.slug] = missBy[m.slug] || []).push(f);
  });
  const missList = (h.misses || []).map((m) => {
    const had = Array.isArray(m.current) ? m.current.join(", ") : (m.current == null ? "—" : m.current);
    const should = Array.isArray(m.truth) ? m.truth.join(", ") : (m.truth == null ? "—" : m.truth);
    return `<li><b>${esc(m.app)}</b> — ${esc(m.field)}: had '${esc(had)}', should be '${esc(should)}'</li>`;
  }).join("");
  const checkedList = (h.checked || []).map((c) => {
    const miss = missBy[c.slug];
    return `<span class="pill ${miss ? "amber" : "green"}">${esc(c.app)}${miss ? " · " + esc(miss.join("/")) : ""}</span>`;
  }).join(" ");
  const handCard = `<article class="proof"><h3>Hand-Checked Accuracy (ground truth)</h3><p>${esc(handText)}</p>`
    + (missList ? `<p class="subtle" style="margin:10px 0 4px">The ${(h.misses || []).length} misses (shown, not hidden):</p><ul style="margin:0 0 6px 18px; padding:0">${missList}</ul>` : "")
    + (checkedList ? `<p class="subtle" style="margin:10px 0 6px">All ${(h.checked || []).length} hand-checked apps (amber = a field we got wrong):</p><div style="display:flex; flex-wrap:wrap; gap:6px">${checkedList}</div>` : "")
    + (h.note ? `<p class="subtle" style="margin:10px 0 0">${esc(h.note)}</p>` : "")
    + `</article>`;
  const cards = [
    `<article class="proof"><h3>Source Quality Gate</h3><p>${q.source_audit_complete
      ? `${q.source_audited_rows} of ${rows.length} rows passed schema, citation, app-identity, and first-party claim-coverage checks.`
      : "The full source-quality audit is incomplete."}</p></article>`,
    handCard,
    `<article class="proof"><h3>Blind Re-Search Agreement</h3><p>${esc(blindText)}</p></article>`,
    `<article class="proof"><h3>Browser-Use Verification (live docs)</h3><p>${esc(browserText)}</p></article>`,
  ];
  if (moveText) {
    cards.push(`<article class="proof"><h3>Accuracy Movement</h3><p>${esc(moveText)}</p>`
      + (am.note ? `<p class="subtle" style="margin:10px 0 0">${esc(am.note)}</p>` : "")
      + `</article>`);
  }
  $("verification-grid").innerHTML = cards.join("");

  const warnings = [];
  if (!h.n) {
    warnings.push("Independent accuracy is still pending. The 100/100 source-audit pass must not be presented as a human accuracy score.");
  } else if (!v.n_verified) {
    warnings.push("Blind re-search agreement is pending; the human accuracy score above is the current ground-truth metric.");
  }
  if (unresolved.length) {
    warnings.push(`Unresolved pipeline failures: ${unresolved.map((f) => `${f.slug} (${f.phase})`).join(", ")}. These apps were not guessed.`);
  }
  if (warnings.length) {
    $("verification-warning").innerHTML = `
      <div class="warning">
        ${esc(warnings.join(" "))}
      </div>
    `;
  } else {
    $("verification-warning").innerHTML = "";
  }
}

function renderFooter() {
  const repo = metrics.repo_url;
  const live = metrics.live_url;
  const links = [
    repo ? `<a href="${esc(repo)}">source repo</a>` : "source repo pending",
    live ? `<a href="${esc(live)}">live page</a>` : "live link pending",
  ].join(" · ");
  $("footer").innerHTML = `Locked 19-field schema · ${links} · generated ${esc(metrics.generated || "—")}.`;
}

async function init() {
  const loaded = await loadData();
  rows = loaded.rows || [];
  metrics = loaded.metrics || {};

  if (!rows.length) {
    $("hero-copy").textContent = "No report data is baked yet. Run python research.py --build-report to populate the page.";
  }

  renderStatus();
  renderHeroFacts();
  renderDecisionBoard();
  renderMetrics();
  renderInsights();
  renderPriorityQueue();
  renderCharts();
  initFilters();
  renderTable();
  renderVerification();
  renderFooter();
}

document.addEventListener("DOMContentLoaded", init);
