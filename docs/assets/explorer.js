/* SHAD website - interactive dataset explorer */
(function () {
  "use strict";
  const S = window.SHADSite;
  S.renderNav("explorer");

  const MAX_PLOTS = 30;
  const DEFAULT_ID = "1774026259";
  const NOMINAL_DIMS = ["s3_request_get_operations", "s3_request_get_latency", "cpu_usage_ratio",
    "network_in_bytes", "disk_io_time_seconds", "objects_missing_count"];
  const LEVEL_NAMES = { platform: "Platform", s3: "S3", server: "Server", device: "Device" };

  const $ = (id) => document.getElementById(id);
  const state = {
    catalog: [], metrics: [], byId: {}, entry: null, series: null, xmlEvents: null,
    selected: [], showLabels: true, deviation: false, plots: [], loadToken: 0,
  };

  // ================================================================== bootstrap
  Promise.all([S.loadJSON("catalog"), S.loadJSON("metrics")]).then(([catalog, metrics]) => {
    state.catalog = catalog;
    state.metrics = metrics;
    catalog.forEach((c) => (state.byId[c.id] = c));
    $("f-group").innerHTML += S.GROUPS.map((g) => `<option>${S.esc(g)}</option>`).join("");
    ["q", "f-group", "f-crit", "f-broken"].forEach((id) => $(id).addEventListener("input", renderList));
    renderList();
    $("status").hidden = true;
    $("content").hidden = false;
    const h = parseHash();
    selectSeries(h.id && state.byId[h.id] ? h.id : DEFAULT_ID, h.dims);
    window.addEventListener("hashchange", () => {
      const hh = parseHash();
      if (hh.id && hh.id !== (state.entry && state.entry.id) && state.byId[hh.id]) selectSeries(hh.id, hh.dims);
    });
  }).catch((e) => {
    $("status").innerHTML = `Could not load the catalog: ${S.esc(e.message)}`;
  });

  // ================================================================== hash state
  function parseHash() {
    const p = new URLSearchParams(location.hash.replace(/^#/, ""));
    return { id: p.get("id"), dims: p.get("dims") ? p.get("dims").split(",").filter(Boolean) : null };
  }
  function writeHash() {
    if (!state.entry) return;
    const p = new URLSearchParams();
    p.set("id", state.entry.id);
    if (state.selected.length) p.set("dims", state.selected.join(","));
    history.replaceState(null, "", "#" + p.toString().replace(/%2C/g, ","));
  }

  // ================================================================== sidebar list
  function renderList() {
    const q = $("q").value.trim().toLowerCase();
    const g = $("f-group").value, crit = $("f-crit").value, hideBroken = $("f-broken").checked;
    const terms = q.split(/\s+/).filter(Boolean);
    const rows = state.catalog.filter((c) => {
      if (g && c.group !== g) return false;
      if (crit && c.criticality !== crit) return false;
      if (hideBroken && c.broken_telemetry) return false;
      if (!terms.length) return true;
      const hay = `${c.id} ${c.group} ${c.criticality} ${c.explanation} ${c.cluster || ""} ${c.events.map((e) => e.component).join(" ")}`.toLowerCase();
      return terms.every((t) => hay.includes(t));
    });
    $("count").textContent = `${rows.length} / ${state.catalog.length} series`;
    let html = "";
    S.GROUPS.forEach((grp) => {
      const items = rows.filter((c) => c.group === grp);
      if (!items.length) return;
      html += `<div class="list-group"><span class="badge" style="padding:0;border:none;background:none"><span class="dot" style="background:${S.groupColor(grp)}"></span></span>${S.esc(grp)} · ${items.length}</div>`;
      items.forEach((c) => {
        const col = S.groupColor(c.group);
        const segs = c.segments_min.map(([s, e]) =>
          `<span style="left:${(100 * s / c.minutes).toFixed(2)}%;width:${Math.max(0.8, 100 * (e - s) / c.minutes).toFixed(2)}%;background:${col}"></span>`).join("");
        const meta = c.group === "Nominal" ? `${c.n} pts` : `${c.criticality} · ${c.events.length} ev.`;
        html += `<a class="item ${state.entry && state.entry.id === c.id ? "active" : ""}" data-id="${c.id}" href="#id=${c.id}" title="${S.esc(c.explanation)}">
          <div class="top"><span class="sid">${c.id}${c.broken_telemetry ? ' <span title="broken telemetry" style="color:var(--text-3)">⚠</span>' : ""}</span><span class="meta">${meta}</span></div>
          <div class="mini">${segs}</div></a>`;
      });
    });
    $("list").innerHTML = html || `<p class="muted small" style="padding:14px">No series match these filters.</p>`;
    $("list").querySelectorAll(".item").forEach((a) => a.addEventListener("click", (ev) => {
      ev.preventDefault();
      selectSeries(a.dataset.id, null);
    }));
  }

  // ================================================================== select + load a series
  async function selectSeries(id, dims) {
    const c = state.byId[id];
    if (!c) return;
    state.entry = c;
    const token = ++state.loadToken;
    document.querySelectorAll(".item").forEach((a) => a.classList.toggle("active", a.dataset.id === id));
    const active = document.querySelector(`.item[data-id="${id}"]`);
    if (active) active.scrollIntoView({ block: "nearest" });
    renderHeader(c);
    renderEvents(c, null);
    destroyPlots();
    $("plots").innerHTML = `<div class="status"><div class="spinner"></div>Loading ${S.esc(c.path)}…</div>`;
    $("dim-list").innerHTML = "";
    const ctx = $("heat").getContext("2d");
    ctx.clearRect(0, 0, $("heat").width, $("heat").height);
    try {
      const [csv, xml] = await Promise.all([
        S.fetchRepoFile(c.path),
        S.fetchRepoFile(c.annotation).catch(() => null),
      ]);
      if (token !== state.loadToken) return;
      state.series = parseCSV(csv);
      state.xmlEvents = xml ? parseXMLEvents(xml) : null;
      renderEvents(c, state.xmlEvents);
      const labelled = state.series.labelled;
      let sel = (dims || []).filter((d) => state.series.index[d] !== undefined);
      if (!sel.length) sel = labelled.length ? labelled.slice(0, 12) : NOMINAL_DIMS.slice();
      state.selected = sel;
      renderQuick();
      renderDimList();
      drawHeat();
      renderPlots();
      writeHash();
    } catch (e) {
      if (token !== state.loadToken) return;
      $("plots").innerHTML = `<div class="status">Could not load the data for ${S.esc(c.id)}.<br><span class="small">${S.esc(e.message)}</span><br>
        <span class="small">When browsing locally, serve the repository root (<code>python -m http.server</code>) and open <code>/docs/explorer.html</code>.</span></div>`;
    }
  }

  function renderHeader(c) {
    $("s-id").textContent = c.id;
    const b = [S.badge(c.group, S.groupColor(c.group))];
    if (c.criticality !== "None") b.push(S.badge(`${c.criticality} criticality`));
    if (c.category !== "None") b.push(S.badge(`${c.category} · ${c.type}`));
    if (c.broken_telemetry) b.push(S.badge("broken telemetry", null, "warn"));
    if (c.legacy_names) b.push(`<span class="badge" title="Columns exported with s0-/s1-/s2- prefixes; mapped to store1-/store2-/store3-">legacy column names</span>`);
    $("s-badges").innerHTML = b.join("");
    $("s-expl").textContent = c.explanation;
    const fmtDate = (s) => s.slice(0, 16).replace("T", " ") + " UTC";
    const meta = [
      ["Start", fmtDate(c.start)], ["End", fmtDate(c.end)], ["Length", `${c.n} timestamps`],
      ["Cluster", c.cluster || "–"], ["Anomalous timestamps", `${(100 * c.anomaly_ratio).toFixed(1)}%`],
      ["Labelled dimensions", `${c.labeled_dimensions.length} / 171`], ["Missing values", `${(100 * c.missing_ratio).toFixed(2)}%`],
      ["Sampling gaps (> 90 s)", c.gaps],
    ];
    $("s-meta").innerHTML = meta.map(([k, v]) => `<div>${k}<b>${S.esc(v)}</b></div>`).join("");
    const snippet = `from shad import SHAD\ns = SHAD().load("${c.id}")`;
    $("s-actions").innerHTML = `
      <a class="btn" href="${S.rawUrl(c.path)}" download>${S.ICONS.download} CSV</a>
      <a class="btn" href="${S.rawUrl(c.annotation)}" download>${S.ICONS.download} XML annotation</a>
      <a class="btn" href="${S.repoUrl(c.path)}">${S.ICONS.github} View on GitHub</a>
      <button class="btn" id="copy-snippet" type="button" title="${S.esc(snippet)}">Copy Python snippet</button>`;
    $("copy-snippet").addEventListener("click", async (ev) => {
      try { await navigator.clipboard.writeText(snippet); ev.target.textContent = "Copied!"; }
      catch (e) { ev.target.textContent = snippet.replace("\n", "; "); }
      setTimeout(() => (ev.target.textContent = "Copy Python snippet"), 1600);
    });
  }

  // ================================================================== parsing
  function harmonize(name) {
    return name.replace(/(^|label_)s([0-2])-/, (m, p, k) => `${p}store${+k + 1}-`);
  }
  function parseCSV(text) {
    const lines = text.split(/\r?\n/).filter((l) => l.length);
    const header = lines[0].split(",").map(harmonize);
    const col = {};
    header.forEach((h, i) => (col[h] = i));
    const n = lines.length - 1;
    const D = state.metrics.length;
    const values = state.metrics.map(() => new Float64Array(n));
    const labels = state.metrics.map(() => new Uint8Array(n));
    const glob = new Uint8Array(n);
    const t = new Float64Array(n);
    const vIdx = state.metrics.map((m) => col[m.name]);
    const lIdx = state.metrics.map((m) => col["label_" + m.name]);
    const gIdx = col.label, tIdx = col.metric_timestamp;
    for (let r = 0; r < n; r++) {
      const f = lines[r + 1].split(",");
      const ts = f[tIdx];
      t[r] = Date.UTC(+ts.slice(0, 4), +ts.slice(5, 7) - 1, +ts.slice(8, 10), +ts.slice(11, 13), +ts.slice(14, 16), +ts.slice(17, 19));
      for (let d = 0; d < D; d++) {
        const s = f[vIdx[d]];
        values[d][r] = s === "" || s === undefined ? NaN : +s;
        labels[d][r] = f[lIdx[d]] === "1" ? 1 : 0;
      }
      glob[r] = f[gIdx] === "1" ? 1 : 0;
    }
    const index = {};
    state.metrics.forEach((m, i) => (index[m.name] = i));
    const labelled = state.metrics.filter((m, i) => labels[i].some((v) => v)).map((m) => m.name);
    const hours = Array.from(t, (v) => (v - t[0]) / 3.6e6);
    return { n, t, hours, values, labels, glob, index, labelled };
  }

  const num = (x) => (x === "" || !Number.isFinite(+x) ? null : +x);
  function parseXMLEvents(text) {
    const doc = new DOMParser().parseFromString(text, "application/xml");
    const map = new Map();
    doc.querySelectorAll("dimensions > dimension").forEach((dim) => {
      dim.querySelectorAll(":scope > anomalies > anomaly").forEach((an) => {
        const g = (tag) => (an.querySelector(":scope > " + tag)?.textContent || "").trim();
        const key = [g("offset_minutes"), g("duration_minutes"), g("store"), g("disk"), g("degradation")].join("|");
        if (!map.has(key)) map.set(key, {
          offset: num(g("offset_minutes")),
          duration: num(g("duration_minutes")),
          store: g("store"), disk: g("disk") === "None" ? "" : g("disk"), degradation: g("degradation") === "None" ? "" : g("degradation"), related: new Set(),
        });
        an.querySelectorAll(":scope > related_dimensions > dimension").forEach((d) => map.get(key).related.add(harmonize(d.textContent.trim())));
      });
    });
    return [...map.values()].sort((a, b) => (a.offset ?? 0) - (b.offset ?? 0)).map((e) => ({ ...e, related: [...e.related] }));
  }

  // ================================================================== events table
  function renderEvents(c, xmlEvents) {
    const block = $("events-block");
    if (c.group === "Nominal") { block.hidden = true; return; }
    block.hidden = false;
    const evs = xmlEvents || c.events.map((e) => ({ ...e, related: null }));
    const rows = evs.map((e, i) => {
      const comp = e.store ? `store${e.store}${e.disk ? " / " + e.disk : ""}` : "–";
      const nrel = e.related ? e.related.length : e.n_related;
      return `<tr class="ev-row" data-i="${i}"><td>${i + 1}</td><td><b>${S.esc(comp)}</b></td>
        <td>${e.offset !== null ? S.fmtMinutes(e.offset) : "–"}</td><td>${e.duration !== null ? S.fmtMinutes(e.duration) : "<i>not recovered</i>"}</td>
        <td>${S.esc(e.degradation || "–")}</td><td>${nrel ?? "–"}</td></tr>`;
    }).join("");
    $("events").innerHTML = `<thead><tr><th>#</th><th>Target component</th><th>Onset (from start)</th><th>Duration</th><th>Max degradation</th><th>Affected dimensions</th></tr></thead><tbody>${rows}</tbody>`;
    $("events").querySelectorAll(".ev-row").forEach((tr) => tr.addEventListener("click", () => {
      const e = evs[+tr.dataset.i];
      if (!e.related || !state.series) return;
      state.selected = e.related.filter((d) => state.series.index[d] !== undefined).slice(0, MAX_PLOTS);
      afterSelectionChange();
      $("plots").scrollIntoView({ behavior: "smooth", block: "start" });
    }));
  }

  // ================================================================== heatmap of all dimensions
  const RAMP = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"];
  const hex2rgb = (h) => { const x = h.replace("#", ""); return [parseInt(x.slice(0, 2), 16), parseInt(x.slice(2, 4), 16), parseInt(x.slice(4, 6), 16)]; };
  const LUT = (() => {
    const stops = RAMP.map(hex2rgb), out = [];
    for (let i = 0; i < 256; i++) {
      const p = (i / 255) * (stops.length - 1), k = Math.min(stops.length - 2, Math.floor(p)), f = p - k;
      out.push(stops[k].map((v, j) => Math.round(v + (stops[k + 1][j] - v) * f)));
    }
    return out;
  })();
  function colorOf(name) {
    const c = S.cssVar(name);
    if (c.startsWith("#")) return hex2rgb(c.length === 4 ? "#" + [...c.slice(1)].map((x) => x + x).join("") : c);
    const m = c.match(/[\d.]+/g);
    return m ? m.slice(0, 3).map(Number) : [200, 200, 200];
  }
  function quantile(sorted, q) {
    if (!sorted.length) return NaN;
    const p = (sorted.length - 1) * q, lo = Math.floor(p), hi = Math.ceil(p);
    return sorted[lo] + (sorted[hi] - sorted[lo]) * (p - lo);
  }
  const ROW = 3, TOP = 8;
  function drawHeat() {
    const s = state.series; if (!s) return;
    const cv = $("heat"), D = state.metrics.length, n = s.n;
    cv.width = n; cv.height = TOP + D * ROW;
    cv.style.height = cv.height + "px";
    const ctx = cv.getContext("2d");
    const img = ctx.createImageData(n, cv.height);
    const px = img.data;
    const miss = colorOf("--surface-3"), bg = colorOf("--surface"), anom = colorOf("--anomaly"), glob = colorOf("--anomaly");
    const put = (x, y, rgb, a = 255) => { const o = (y * n + x) * 4; px[o] = rgb[0]; px[o + 1] = rgb[1]; px[o + 2] = rgb[2]; px[o + 3] = a; };
    // top strip: global label
    for (let x = 0; x < n; x++) for (let y = 0; y < TOP - 2; y++) put(x, y, s.glob[x] ? glob : miss);
    for (let x = 0; x < n; x++) for (let y = TOP - 2; y < TOP; y++) put(x, y, bg);
    for (let d = 0; d < D; d++) {
      const v = s.values[d];
      const finite = Array.from(v).filter(Number.isFinite).sort((a, b) => a - b);
      let lo, hi, med, mad;
      if (state.deviation) {
        med = quantile(finite, 0.5);
        mad = quantile(finite.map((x) => Math.abs(x - med)).sort((a, b) => a - b), 0.5) * 1.4826 || (quantile(finite, 0.9) - quantile(finite, 0.1)) / 2.56 || 1;
      } else { lo = quantile(finite, 0.01); hi = quantile(finite, 0.99); }
      for (let x = 0; x < n; x++) {
        let rgb;
        const val = v[x];
        if (!Number.isFinite(val)) rgb = (x + d) % 2 ? miss : bg;
        else if (state.showLabels && s.labels[d][x]) rgb = anom;
        else {
          let t;
          if (state.deviation) t = Math.min(1, Math.abs(val - med) / mad / 6);
          else t = hi > lo ? Math.min(1, Math.max(0, (val - lo) / (hi - lo))) : 0.5;
          rgb = LUT[Math.round(t * 255)];
        }
        for (let k = 0; k < ROW; k++) put(x, TOP + d * ROW + k, rgb);
      }
    }
    ctx.putImageData(img, 0, 0);
    // level labels
    const levels = ["platform", "s3", "server", "device"];
    let start = 0, html = `<div style="top:0;height:${TOP}px;border-right-color:var(--anomaly)">label</div>`;
    levels.forEach((lv) => {
      const k = state.metrics.filter((m) => m.level === lv).length;
      html += `<div style="top:${TOP + start * ROW}px;height:${k * ROW}px">${LEVEL_NAMES[lv]}<br>${k}</div>`;
      start += k;
    });
    $("heat-levels").innerHTML = html;
    $("heat-levels").style.height = cv.height + "px";
    const H = s.hours[n - 1];
    const ticks = [0, 0.25, 0.5, 0.75, 1].map((f) => `${(H * f).toFixed(1).replace(/\.0$/, "")}h`);
    $("heat-x").innerHTML = ticks.map((t) => `<span>${t}</span>`).join("");
  }
  (function bindHeat() {
    const cv = $("heat");
    const locate = (ev) => {
      const s = state.series; if (!s) return null;
      const r = cv.getBoundingClientRect();
      const x = Math.min(s.n - 1, Math.max(0, Math.floor(((ev.clientX - r.left) / r.width) * s.n)));
      const y = Math.floor(((ev.clientY - r.top) / r.height) * cv.height);
      const d = Math.floor((y - TOP) / ROW);
      return { x, d: y < TOP ? -1 : Math.min(state.metrics.length - 1, d) };
    };
    cv.addEventListener("mousemove", (ev) => {
      const p = locate(ev); if (!p) return;
      const s = state.series, time = new Date(s.t[p.x]).toISOString().slice(0, 16).replace("T", " ");
      if (p.d < 0) {
        $("heat-readout").textContent = `${time} UTC · top-level label = ${s.glob[p.x]}`;
        S.tip(null); return;
      }
      const m = state.metrics[p.d];
      const v = s.values[p.d][p.x];
      $("heat-readout").textContent = `${m.name} · ${time} UTC · value ${Number.isFinite(v) ? S.fmtNum(v) : "missing"} · label ${s.labels[p.d][p.x]}`;
      S.tip(`<b>${S.esc(m.name)}</b><br><span class="t-muted">${S.esc(m.description)}</span><br>${time} UTC · ${Number.isFinite(v) ? S.fmtNum(v) + " " + S.esc(m.unit) : "missing"}` +
        (s.labels[p.d][p.x] ? `<br><b style="color:var(--anomaly)">labelled anomalous</b>` : "") + `<br><span class="t-muted">click to ${state.selected.includes(m.name) ? "remove from" : "add to"} the charts</span>`, ev);
    });
    cv.addEventListener("mouseleave", () => { S.tip(null); $("heat-readout").textContent = ""; });
    cv.addEventListener("click", (ev) => {
      const p = locate(ev); if (!p || p.d < 0) return;
      toggleDim(state.metrics[p.d].name);
    });
  })();
  $("t-labels").addEventListener("click", (e) => {
    state.showLabels = !state.showLabels;
    e.currentTarget.classList.toggle("on", state.showLabels);
    e.currentTarget.setAttribute("aria-pressed", state.showLabels);
    drawHeat();
  });
  $("t-norm").addEventListener("click", (e) => {
    state.deviation = !state.deviation;
    e.currentTarget.classList.toggle("on", state.deviation);
    e.currentTarget.setAttribute("aria-pressed", state.deviation);
    drawHeat();
  });

  // ================================================================== dimension selection
  function toggleDim(name) {
    const i = state.selected.indexOf(name);
    if (i >= 0) state.selected.splice(i, 1);
    else {
      if (state.selected.length >= MAX_PLOTS) state.selected.shift();
      state.selected.push(name);
    }
    afterSelectionChange();
  }
  function afterSelectionChange() {
    renderDimList();
    renderQuick();
    renderPlots();
    writeHash();
  }
  function renderQuick() {
    const s = state.series; if (!s) return;
    const byStore = (st) => state.metrics.filter((m) => m.level === "server" && m.store === st).map((m) => m.name);
    const presets = [
      [`Labelled (${s.labelled.length})`, s.labelled.slice(0, MAX_PLOTS), !s.labelled.length],
      ["Platform", state.metrics.filter((m) => m.level === "platform").map((m) => m.name)],
      ["S3", state.metrics.filter((m) => m.level === "s3").map((m) => m.name)],
      ["store1", byStore("store1")], ["store2", byStore("store2")], ["store3", byStore("store3")],
      ["Clear", []],
    ];
    $("quick").innerHTML = presets.map(([l, dims, dis], i) => `<button class="chip" data-i="${i}" ${dis ? "disabled style='opacity:.5'" : ""}>${l}</button>`).join("");
    $("quick").querySelectorAll("button").forEach((b) => b.addEventListener("click", () => {
      state.selected = presets[+b.dataset.i][1].slice(0, MAX_PLOTS);
      afterSelectionChange();
    }));
  }
  function renderDimList() {
    const s = state.series; if (!s) return;
    const q = $("dim-q").value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    const groups = [];
    const push = (title, ms) => { const f = ms.filter((m) => q.every((t) => m.name.toLowerCase().includes(t))); if (f.length) groups.push([title, f]); };
    push("Platform", state.metrics.filter((m) => m.level === "platform"));
    push("S3", state.metrics.filter((m) => m.level === "s3"));
    ["store1", "store2", "store3"].forEach((st) => push(`Server ${st}`, state.metrics.filter((m) => m.level === "server" && m.store === st)));
    ["store1", "store2", "store3"].forEach((st) => push(`Devices ${st}`, state.metrics.filter((m) => m.level === "device" && m.store === st)));
    const lab = new Set(s.labelled), sel = new Set(state.selected);
    $("dim-list").innerHTML = groups.map(([t, ms]) => `<div class="grp">${t}</div>` + ms.map((m) =>
      `<label class="${lab.has(m.name) ? "lab" : ""}" title="${S.esc(m.description)}"><input type="checkbox" value="${m.name}" ${sel.has(m.name) ? "checked" : ""}>${S.esc(m.name)}</label>`).join("")).join("")
      || `<p class="muted small">No dimension matches.</p>`;
    $("dim-list").querySelectorAll("input").forEach((i) => i.addEventListener("change", () => toggleDim(i.value)));
  }
  $("dim-q").addEventListener("input", renderDimList);

  // ================================================================== plots (uPlot)
  function destroyPlots() { state.plots.forEach((p) => p.u.destroy()); state.plots = []; }
  function spans(arr) {
    const out = []; let s = -1;
    for (let i = 0; i < arr.length; i++) {
      if (arr[i] && s < 0) s = i;
      if (!arr[i] && s >= 0) { out.push([s, i]); s = -1; }
    }
    if (s >= 0) out.push([s, arr.length]);
    return out;
  }
  function fmtHours(h) {
    const hh = Math.floor(h), mm = Math.round((h - hh) * 60);
    return mm === 60 ? `${hh + 1}h` : mm ? `${hh}h${String(mm).padStart(2, "0")}` : `${hh}h`;
  }
  let syncing = false;
  function renderPlots() {
    const s = state.series; if (!s) return;
    destroyPlots();
    const wrap = $("plots");
    wrap.innerHTML = "";
    if (!state.selected.length) {
      wrap.innerHTML = `<p class="muted">No dimension selected. Pick some in the list above, click rows of the heatmap, or click an event.</p>`;
      return;
    }
    const line = S.cssVar("--accent"), grid = S.cssVar("--grid"), txt = S.cssVar("--text-2");
    const soft = S.cssVar("--anomaly-soft"), mid = S.cssVar("--anomaly-mid");
    const globSpans = spans(s.glob);
    const hours = s.hours;
    state.selected.forEach((name) => {
      const d = s.index[name]; if (d === undefined) return;
      const m = state.metrics[d];
      const ys = Array.from(s.values[d], (v) => (Number.isFinite(v) ? v : null));
      const dimSpans = spans(s.labels[d]);
      const box = document.createElement("div");
      box.className = "plot";
      box.innerHTML = `<div class="plot-h"><span class="n" title="${S.esc(m.name)}">${dimSpans.length ? '<span class="sw2" style="width:8px;height:8px;background:var(--anomaly);margin-right:6px"></span>' : ""}${S.esc(m.name)}</span>
        <span style="display:flex;gap:8px;align-items:center"><span class="u val"></span><span class="u">${S.esc(m.unit)}</span><button title="Remove" aria-label="Remove ${S.esc(m.name)}">×</button></span></div>
        <div class="desc" title="${S.esc(m.description)}">${S.esc(m.description)}</div>`;
      wrap.appendChild(box);
      box.querySelector("button").addEventListener("click", () => toggleDim(m.name));
      const valEl = box.querySelector(".val");
      const shade = (u) => {
        const ctx = u.ctx, { top, height } = u.bbox;
        const xp = (i) => u.valToPos(hours[Math.min(i, hours.length - 1)], "x", true);
        ctx.save();
        ctx.fillStyle = soft;
        globSpans.forEach(([a, b]) => ctx.fillRect(xp(a), top, Math.max(1, xp(b) - xp(a)), height));
        ctx.fillStyle = mid;
        dimSpans.forEach(([a, b]) => ctx.fillRect(xp(a), top, Math.max(1, xp(b) - xp(a)), height));
        ctx.restore();
      };
      const opts = {
        width: Math.max(260, box.clientWidth - 12), height: 150,
        legend: { show: false },
        cursor: { sync: { key: "shad-x" }, points: { size: 6 }, drag: { x: true, y: false } },
        scales: { x: { time: false } },
        axes: [
          { stroke: txt, grid: { stroke: grid, width: 1 }, ticks: { stroke: grid }, size: 28, font: "11px Inter, system-ui, sans-serif",
            values: (u, vals) => vals.map(fmtHours), incrs: [0.25, 0.5, 1, 2, 3, 4, 6] },
          { stroke: txt, grid: { stroke: grid, width: 1 }, ticks: { stroke: grid }, size: 52, font: "11px Inter, system-ui, sans-serif",
            values: (u, vals) => vals.map((v) => S.fmtCompact(v)) },
        ],
        series: [{}, { stroke: line, width: 1.4, spanGaps: false, points: { show: false } }],
        hooks: {
          drawClear: [shade],
          setCursor: [(u) => {
            const i = u.cursor.idx;
            if (i === null || i === undefined) { valEl.textContent = ""; $("cursor-readout").textContent = ""; return; }
            const v = ys[i];
            valEl.textContent = v === null ? "missing" : S.fmtNum(v);
            valEl.style.color = s.labels[d][i] ? "var(--anomaly)" : "";
            $("cursor-readout").textContent = `${new Date(s.t[i]).toISOString().slice(0, 16).replace("T", " ")} UTC · t = ${fmtHours(hours[i])} · ` +
              (s.glob[i] ? "anomaly ongoing" : "no anomaly");
          }],
          setScale: [(u, key) => {
            if (key !== "x" || syncing) return;
            syncing = true;
            const { min, max } = u.scales.x;
            state.plots.forEach((p) => { if (p.u !== u) p.u.setScale("x", { min, max }); });
            syncing = false;
          }],
        },
      };
      const u = new uPlot(opts, [hours, ys], box);
      state.plots.push({ u, box });
    });
  }
  let rt;
  window.addEventListener("resize", () => {
    clearTimeout(rt);
    rt = setTimeout(() => state.plots.forEach((p) => p.u.setSize({ width: Math.max(260, p.box.clientWidth - 12), height: 150 })), 120);
  });
  document.addEventListener("shad-theme", () => { drawHeat(); renderPlots(); renderList(); });
})();
