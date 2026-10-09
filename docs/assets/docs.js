/* SHAD website - documentation page */
(function () {
  "use strict";
  const S = window.SHADSite;
  S.renderNav("docs");
  S.enhanceCode();
  const $ = (id) => document.getElementById(id);

  // ---------------------------------------------------------------- TOC highlight
  const links = [...document.querySelectorAll("#toc a")];
  const targets = links.map((a) => document.querySelector(a.getAttribute("href"))).filter(Boolean);
  const onScroll = () => {
    let cur = targets[0];
    for (const t of targets) if (t.getBoundingClientRect().top < 120) cur = t;
    links.forEach((a) => a.classList.toggle("on", cur && a.getAttribute("href") === "#" + cur.id));
  };
  document.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // ---------------------------------------------------------------- sortable table helper
  function table(el, columns, rows, sortKey, sortDir = 1) {
    let key = sortKey, dir = sortDir;
    const draw = () => {
      const sorted = rows.slice().sort((a, b) => {
        const va = columns.find((c) => c.key === key).sort(a), vb = columns.find((c) => c.key === key).sort(b);
        return (va > vb ? 1 : va < vb ? -1 : 0) * dir;
      });
      el.innerHTML = `<thead><tr>${columns.map((c) =>
        `<th class="sortable" data-k="${c.key}" aria-sort="${c.key === key ? (dir > 0 ? "ascending" : "descending") : "none"}">${c.label}${c.key === key ? (dir > 0 ? " ↑" : " ↓") : ""}</th>`).join("")}</tr></thead>
        <tbody>${sorted.map((r) => `<tr>${columns.map((c) => `<td class="${c.cls || ""}">${c.html(r)}</td>`).join("")}</tr>`).join("")}</tbody>`;
      el.querySelectorAll("th").forEach((th) => th.addEventListener("click", () => {
        if (key === th.dataset.k) dir = -dir; else { key = th.dataset.k; dir = 1; }
        draw();
      }));
    };
    draw();
    return { update(newRows) { rows = newRows; draw(); } };
  }

  Promise.all([S.loadJSON("catalog"), S.loadJSON("metrics")]).then(([cat, metrics]) => {
    // ---------------------------------------------------- scenario table
    const desc = {
      "Nominal": "Baseline workload only (training data)",
      "Single Disk": "One NVMe data disk detached",
      "Simultaneous Disk": "2–4 disks detached at the same time",
      "Asynchronous Disk": "2–4 disk failures at different times (cascading / rolling / independent)",
      "Single Server": "One server isolated from the cluster (100% packet loss)",
      "Asynchronous Server": "2–3 server isolations at different times",
      "Server Degradation": "Delay and packet loss ramped linearly or in stages on one server",
      "Single SNode": "1–3 storage-node processes killed on one server",
      "Simultaneous SNode": "Storage nodes killed on several servers at the same time",
      "Asynchronous SNode": "Storage-node failures at different times",
    };
    const rows = S.GROUPS.map((g) => {
      const cs = cat.filter((c) => c.group === g);
      return `<tr><td>${S.badge(g, S.groupColor(g))}</td><td>${S.esc(cs[0].type)}</td><td>${S.esc(cs[0].category)}</td><td>${S.esc(cs[0].criticality)}</td>
        <td style="text-align:right">${cs.length}</td><td>${desc[g]}</td></tr>`;
    }).join("");
    $("scenario-table").innerHTML = `<tr><th>Scenario (folder)</th><th>type</th><th>category</th><th>criticality</th><th style="text-align:right">Series</th><th>Description</th></tr>${rows}`;

    // ---------------------------------------------------- metrics table
    const mcols = [
      { key: "i", label: "#", sort: (r) => r.i, html: (r) => r.i + 1 },
      { key: "name", label: "Column", sort: (r) => r.name, html: (r) => `<code>${S.esc(r.name)}</code>`, cls: "" },
      { key: "level", label: "Level", sort: (r) => r.level, html: (r) => S.esc(r.level) },
      { key: "store", label: "Store", sort: (r) => r.store || "", html: (r) => S.esc(r.store || "–") },
      { key: "device", label: "Device", sort: (r) => r.device || "", html: (r) => S.esc(r.device || "–") },
      { key: "unit", label: "Unit", sort: (r) => r.unit, html: (r) => S.esc(r.unit) },
      { key: "description", label: "Description", sort: (r) => r.description, html: (r) => S.esc(r.description) },
    ];
    const mrows = metrics.map((m, i) => ({ ...m, i }));
    const mt = table($("m-table"), mcols, mrows, "i");
    const mfilter = () => {
      const q = $("m-q").value.trim().toLowerCase().split(/\s+/).filter(Boolean), lv = $("m-level").value;
      const f = mrows.filter((m) => (!lv || m.level === lv) && q.every((t) => `${m.name} ${m.description} ${m.unit}`.toLowerCase().includes(t)));
      $("m-count").textContent = `${f.length} / ${mrows.length} dimensions`;
      mt.update(f);
    };
    $("m-q").addEventListener("input", mfilter);
    $("m-level").addEventListener("input", mfilter);
    mfilter();

    // ---------------------------------------------------- catalog table
    $("c-group").innerHTML += S.GROUPS.map((g) => `<option>${S.esc(g)}</option>`).join("");
    const order = Object.fromEntries(S.GROUPS.map((g, i) => [g, i]));
    const crit = { None: 0, Low: 1, Medium: 2, High: 3 };
    const ccols = [
      { key: "id", label: "Id", sort: (r) => r.id, html: (r) => `<a class="mono" href="explorer.html#id=${r.id}">${r.id}</a>`, cls: "" },
      { key: "group", label: "Scenario", sort: (r) => order[r.group] * 1e11 + +r.id, html: (r) => S.badge(r.group, S.groupColor(r.group)) },
      { key: "crit", label: "Criticality", sort: (r) => crit[r.criticality], html: (r) => S.esc(r.criticality) },
      { key: "start", label: "Start (UTC)", sort: (r) => r.start, html: (r) => `<span class="mono" style="white-space:nowrap">${r.start.slice(0, 16).replace("T", " ")}</span>` },
      { key: "n", label: "Length", sort: (r) => r.n, html: (r) => r.n },
      { key: "ratio", label: "Anomalous", sort: (r) => r.anomaly_ratio, html: (r) => `${(100 * r.anomaly_ratio).toFixed(1)}%` },
      { key: "dims", label: "Labelled dims", sort: (r) => r.labeled_dimensions.length, html: (r) => r.labeled_dimensions.length },
      { key: "expl", label: "Description", sort: (r) => r.explanation, html: (r) => S.esc(r.explanation) + (r.broken_telemetry ? " " + S.badge("broken telemetry", null, "warn") : "") },
    ];
    const ct = table($("c-table"), ccols, cat, "group");
    const cfilter = () => {
      const q = $("c-q").value.trim().toLowerCase().split(/\s+/).filter(Boolean), g = $("c-group").value;
      const f = cat.filter((c) => (!g || c.group === g) && q.every((t) =>
        `${c.id} ${c.group} ${c.criticality} ${c.cluster || ""} ${c.explanation}`.toLowerCase().includes(t)));
      $("c-count").textContent = `${f.length} / ${cat.length} series`;
      ct.update(f);
    };
    $("c-q").addEventListener("input", cfilter);
    $("c-group").addEventListener("input", cfilter);
    cfilter();
    if (location.hash) { const t = document.querySelector(location.hash); if (t) t.scrollIntoView(); }
  });
})();
