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
};

const pct = (n) => (Number.isFinite(n) ? `${Math.round(n * 100)}%` : "Pending");
const num = (value, fallback = "0") => value == null ? fallback : String(value);
const pill = (text, kind) => `<span class="pill ${tone[kind || text] || "gray"}">${esc(text || "—")}</span>`;
const width = (value, max) => `${max > 0 ? Math.max(3, Math.round((value / max) * 100)) : 0}%`;
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
  const v = metrics.verification || {};
  const lines = [
    ["Dataset", `${num(p.n || rows.length)} / 100 apps`],
    ["Hand check", h.n ? `${h.n} apps · ${pct(h.accuracy)}` : "Pending"],
    ["Blind re-search", v.n_verified ? `${v.n_verified} apps · ${pct(v.overall_agreement_rate)}` : "Pending"],
    ["Generated", metrics.generated || "Not generated"],
  ];
  $("status-lines").innerHTML = lines.map(([label, value]) => `
    <div class="status-line"><b>${esc(label)}</b><span>${esc(value)}</span></div>
  `).join("");
}

function renderDecisionBoard() {
  const p = metrics.patterns || {};
  const actions = p.recommended_next_action || {};
  const total = p.n || rows.length || 1;
  const decisionRows = [
    ["Build Now", actions["Build Now"] || 0],
    ["Needs Outreach", actions["Needs Outreach"] || 0],
    ["Partner-Gated", actions["Partner-Gated"] || 0],
    ["Blocked", actions.Blocked || 0],
  ];
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
  const mcp = p.existing_mcp || {};
  const h = metrics.handcheck || {};
  const data = [
    [p.n || rows.length, "apps in scope"],
    [access["Self-Serve"] || 0, "self-serve paths"],
    [p.build_now || 0, "ready to build"],
    [p.partner_gated || 0, "partner-gated"],
    [mcp.Official || 0, "official MCP"],
    [h.n ? pct(h.accuracy) : "Pending", "hand-check"],
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
  const partner = rows.filter((r) => r.recommended_next_action === "Partner-Gated");
  const topAuth = (p.auth_methods_top || [])[0] || ["API Key / OAuth", 0];
  const examples = (list) => list.slice(0, 5).map((r) => r.app).join(", ") || "none yet";

  const cards = [
    [
      "Self-serve integrations are the first wave.",
      `${access["Self-Serve"] || 0} apps expose a path where a developer can get credentials without a partnership motion. These are the fastest toolkit candidates.`,
    ],
    [
      "Authentication is conventional enough to automate.",
      `${p.build_now || 0} apps are Build Now. The largest auth bucket is ${topAuth[0]} (${topAuth[1]} apps), so agent tools can standardize around familiar credential flows.`,
    ],
    [
      "Outreach should target real APIs with closed doors.",
      `${gatedApi.length} apps have APIs but require review, business verification, or customer status. Partner-gated examples: ${examples(partner)}.`,
    ],
  ];

  $("insights").innerHTML = cards.map(([title, body]) => `
    <article class="insight">
      <h3>${esc(title)}</h3>
      <p>${esc(body)}</p>
    </article>
  `).join("");
  $("generated-note").textContent = `Generated ${metrics.generated || "—"} · avg confidence ${(p.avg_confidence || 0).toFixed ? p.avg_confidence.toFixed(3) : "—"}`;
}

function renderPriorityQueue() {
  const confidence = (r) => Number(r.confidence || 0);
  const short = (r) => `<li><span>${esc(r.app)}</span><small>${esc(r.category)}</small></li>`;
  const build = rows
    .filter((r) => r.recommended_next_action === "Build Now")
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
    ["Build first", build, "Self-serve, broad API, clear docs"],
    ["Escalate", outreach, "Gated access or blocked paths"],
    ["MCP leverage", mcp, "Official MCP already exists"],
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
  const handText = h.n
    ? `${h.n} apps checked by a human; overall two-field accuracy ${pct(h.accuracy)}.`
    : "No hand-check rows have been folded yet. This should be completed before final submission.";
  const blindText = v.n_verified
    ? `${v.n_verified} apps re-researched independently; agreement ${pct(v.overall_agreement_rate)}.`
    : "No blind re-search agreement has been recorded yet.";

  $("verification-grid").innerHTML = `
    <article class="proof">
      <h3>Hand-Checked Accuracy</h3>
      <p>${esc(handText)}</p>
    </article>
    <article class="proof">
      <h3>Blind Re-Search Agreement</h3>
      <p>${esc(blindText)}</p>
    </article>
  `;

  if (!h.n || !v.n_verified) {
    $("verification-warning").innerHTML = `
      <div class="warning">
        This page is honest about unfinished verification: the dataset can be reviewed,
        but the final submission should include filled hand-check and blind re-search metrics.
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
