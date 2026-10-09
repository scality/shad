/* SHAD website - small dependency-free SVG charts */
(function () {
  "use strict";
  const S = window.SHADSite;
  const NS = "http://www.w3.org/2000/svg";

  function el(tag, attrs = {}, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) if (attrs[k] !== undefined && attrs[k] !== null) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function svgFor(container, width, height) {
    container.innerHTML = "";
    const svg = el("svg", { viewBox: `0 0 ${width} ${height}`, width, height, role: "img" });
    svg.style.width = width + "px";
    container.appendChild(svg);
    return svg;
  }
  const widthOf = (c, min = 320) => Math.max(min, Math.floor(c.clientWidth || c.parentNode.clientWidth || 600));

  // deterministic jitter in [-1, 1]
  function jitter(i) { const x = Math.sin(i * 12.9898 + 78.233) * 43758.5453; return (x - Math.floor(x)) * 2 - 1; }

  function niceTicks(min, max, n = 5) {
    const span = max - min || 1;
    const step0 = Math.pow(10, Math.floor(Math.log10(span / n)));
    const err = (span / n) / step0;
    const step = step0 * (err >= 7.5 ? 10 : err >= 3.5 ? 5 : err >= 1.5 ? 2 : 1);
    const out = [];
    for (let v = Math.ceil(min / step) * step; v <= max + 1e-9; v += step) out.push(+v.toFixed(10));
    return out;
  }
  function logTicks(min, max) {
    const out = [];
    for (let p = Math.floor(Math.log10(min)); p <= Math.ceil(Math.log10(max)); p++) {
      for (const m of [1, 2, 5]) { const v = m * Math.pow(10, p); if (v >= min * 0.999 && v <= max * 1.001) out.push(v); }
    }
    return out;
  }

  // ---------------------------------------------------------------- horizontal bars
  function barChart(container, rows, opts = {}) {
    const W = widthOf(container), labelW = opts.labelWidth || 150, rowH = 26, barH = 16, top = 4;
    const H = top + rows.length * rowH + 4;
    const svg = svgFor(container, W, H);
    const max = Math.max(...rows.map((r) => r.value));
    const plotW = W - labelW - 44;
    rows.forEach((r, i) => {
      const y = top + i * rowH;
      el("text", { x: labelW - 10, y: y + rowH / 2 + 4, "text-anchor": "end" }, svg).textContent = r.label;
      const w = Math.max(2, (r.value / max) * plotW);
      // square at baseline, 4px rounded data-end
      const x0 = labelW, yb = y + (rowH - barH) / 2, rr = Math.min(4, w / 2);
      el("path", {
        d: `M${x0},${yb} H${x0 + w - rr} Q${x0 + w},${yb} ${x0 + w},${yb + rr} V${yb + barH - rr} Q${x0 + w},${yb + barH} ${x0 + w - rr},${yb + barH} H${x0} Z`,
        fill: r.color,
      }, svg);
      el("text", { x: x0 + w + 6, y: y + rowH / 2 + 4, class: "lbl-strong" }, svg).textContent = r.value;
      const hit = el("rect", { x: 0, y, width: W, height: rowH, fill: "transparent" }, svg);
      if (opts.tip) {
        hit.addEventListener("mousemove", (ev) => S.tip(opts.tip(r), ev));
        hit.addEventListener("mouseleave", () => S.tip(null));
      }
      if (r.href) { hit.style.cursor = "pointer"; hit.addEventListener("click", () => (location.href = r.href)); }
    });
    el("line", { x1: labelW, x2: labelW, y1: 0, y2: H, stroke: S.cssVar("--border") }, svg);
  }

  // ---------------------------------------------------------------- dot strip plot per group
  // opts.threshold (optional): draws a dashed vertical line at that value (label: opts.thresholdLabel).
  // point.emph (optional): draws the point larger, with a dark outline.
  function stripPlot(container, points, opts) {
    const groups = opts.groups;
    const W = widthOf(container), labelW = opts.labelWidth || 150, rowH = 30, top = 6, axisH = 26;
    const H = top + groups.length * rowH + axisH;
    const svg = svgFor(container, W, H);
    const vals = points.map((p) => p.value).filter((v) => v > 0 || !opts.log);
    let min = opts.min ?? Math.min(...vals), max = opts.max ?? Math.max(...vals);
    const x0 = labelW, x1 = W - 16;
    let sx, ticks;
    if (opts.log) {
      min = Math.max(min, opts.logFloor || 1);
      const lmin = Math.log10(min) - 0.05, lmax = Math.log10(max) + 0.05;
      sx = (v) => x0 + ((Math.log10(Math.max(v, min)) - lmin) / (lmax - lmin)) * (x1 - x0);
      ticks = opts.ticks || logTicks(min, max);
    } else {
      sx = (v) => x0 + ((v - min) / (max - min || 1)) * (x1 - x0);
      ticks = opts.ticks || niceTicks(min, max, 5);
    }
    const gridC = S.cssVar("--grid"), surf = S.cssVar("--surface"), ink = S.cssVar("--text");
    ticks.forEach((t) => {
      const x = sx(t);
      el("line", { x1: x, x2: x, y1: top, y2: H - axisH + 2, class: "gridline" }, svg);
      el("text", { x, y: H - 8, "text-anchor": "middle" }, svg).textContent = opts.tickFormat ? opts.tickFormat(t) : S.fmtCompact(t);
    });
    if (opts.threshold != null) {
      const xt = sx(opts.threshold);
      el("line", { x1: xt, x2: xt, y1: top, y2: H - axisH + 2, stroke: S.cssVar("--text-3"), "stroke-width": 1.2, "stroke-dasharray": "4 3" }, svg);
      if (opts.thresholdLabel) el("text", { x: xt + 5, y: top + 10, fill: S.cssVar("--text-3") }, svg).textContent = opts.thresholdLabel;
    }
    groups.forEach((g, gi) => {
      const yc = top + gi * rowH + rowH / 2;
      el("text", { x: labelW - 10, y: yc + 4, "text-anchor": "end" }, svg).textContent = g;
      if (gi > 0) el("line", { x1: 0, x2: W, y1: top + gi * rowH, y2: top + gi * rowH, stroke: gridC, "stroke-width": 0.6 }, svg);
      const pts = points.filter((p) => p.group === g);
      if (!pts.length) return;
      const sorted = pts.map((p) => p.value).sort((a, b) => a - b);
      const med = sorted[Math.floor((sorted.length - 1) / 2)];
      pts.forEach((p, i) => {
        const r0 = 4;
        const c = el("circle", { cx: sx(p.value), cy: yc + jitter(i + gi * 97) * (rowH / 2 - 7), r: r0, fill: p.color, stroke: p.emph ? ink : surf, "stroke-width": p.emph ? 2 : 1.5, "fill-opacity": 0.9 }, svg);
        c.addEventListener("mousemove", (ev) => { c.setAttribute("r", r0 + 2); S.tip(opts.tip(p), ev); });
        c.addEventListener("mouseleave", () => { c.setAttribute("r", r0); S.tip(null); });
        if (p.href) { c.style.cursor = "pointer"; c.addEventListener("click", () => (location.href = p.href)); }
      });
      const mx = sx(med);
      el("line", { x1: mx, x2: mx, y1: yc - rowH / 2 + 4, y2: yc + rowH / 2 - 4, stroke: ink, "stroke-width": 2, "stroke-linecap": "round" }, svg)
        .appendChild(el("title")).textContent = `median ${S.fmtNum(med)}`;
    });
    if (opts.xLabel) el("text", { x: x1, y: H - axisH - 4, "text-anchor": "end", fill: S.cssVar("--text-3") }, svg).textContent = opts.xLabel;
  }

  // ---------------------------------------------------------------- whole-dataset timeline
  function timeline(container, catalog) {
    const groups = S.GROUPS;
    const W = Math.max(680, widthOf(container)), labelW = 172, rowH = 4, gap = 1, groupGap = 14, top = 20, axisH = 24;
    const anomalous = catalog.filter((c) => c.group !== "Nominal");
    const nominal = catalog.filter((c) => c.group === "Nominal");
    let H = top + axisH;
    H += 18 + groupGap; // nominal summary row
    groups.slice(1).forEach((g) => { H += anomalous.filter((c) => c.group === g).length * (rowH + gap) + groupGap; });
    const svg = svgFor(container, W, H);
    const maxMin = Math.max(...catalog.map((c) => c.minutes));
    const x0 = labelW, x1 = W - 12;
    const sx = (m) => x0 + (m / maxMin) * (x1 - x0);
    const track = S.cssVar("--surface-3"), surf = S.cssVar("--surface");
    // hour grid
    for (let h = 0; h * 60 <= maxMin; h += 3) {
      const x = sx(h * 60);
      el("line", { x1: x, x2: x, y1: top - 4, y2: H - axisH, class: "gridline" }, svg);
      el("text", { x, y: H - 6, "text-anchor": "middle" }, svg).textContent = `${h}h`;
    }
    el("text", { x: x1, y: 11, "text-anchor": "end", fill: S.cssVar("--text-3") }, svg).textContent = "time since the first sample →";

    let y = top;
    // nominal summary
    const nomC = S.typeColor("None");
    el("text", { x: labelW - 10, y: y + 12, "text-anchor": "end" }, svg).textContent = `Nominal (${nominal.length})`;
    el("rect", { x: x0, y: y + 3, width: sx(Math.round(nominal.reduce((a, c) => a + c.minutes, 0) / nominal.length)) - x0, height: 12, rx: 3, fill: track }, svg);
    el("text", { x: x0 + 8, y: y + 13, fill: S.cssVar("--text-2") }, svg).textContent = "83 series without anomaly - the training data of semi-supervised detectors";
    y += 18 + groupGap;

    groups.slice(1).forEach((g) => {
      const rows = anomalous.filter((c) => c.group === g);
      const gh = rows.length * (rowH + gap);
      el("text", { x: labelW - 10, y: y + gh / 2 + 4, "text-anchor": "end" }, svg).textContent = `${g} (${rows.length})`;
      const color = S.groupColor(g);
      rows.forEach((c) => {
        el("rect", { x: x0, y, width: sx(c.minutes) - x0, height: rowH, fill: track }, svg);
        c.segments_min.forEach(([s, e]) => {
          el("rect", { x: sx(s), y, width: Math.max(1.5, sx(e) - sx(s)), height: rowH, fill: color }, svg);
        });
        const hit = el("rect", { x: 0, y: y - 0.5, width: W, height: rowH + gap, fill: "transparent" }, svg);
        hit.style.cursor = "pointer";
        hit.addEventListener("mousemove", (ev) => {
          S.tip(`<b>${c.id}</b> · ${S.esc(c.group)} · ${S.esc(c.criticality)} criticality<br>` +
            `<span class="t-muted">${S.esc(c.explanation)}</span><br>` +
            `${c.segments.length} anomalous period(s), ${(100 * c.anomaly_ratio).toFixed(1)}% of timestamps` +
            (c.broken_telemetry ? `<br><b>Broken telemetry</b>` : ""), ev);
        });
        hit.addEventListener("mouseleave", () => S.tip(null));
        hit.addEventListener("click", () => (location.href = `explorer.html#id=${c.id}`));
        y += rowH + gap;
      });
      y += groupGap;
    });
    void surf;
  }

  // ---------------------------------------------------------------- dimension heatmap
  const BLUES = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"];
  function seqColor(t) {
    if (t <= 0) return null;
    const i = Math.min(BLUES.length - 1, Math.floor(t * (BLUES.length - 1) + 0.5));
    return BLUES[i];
  }
  function heatmap(container, stats, metrics, catalog) {
    const groups = S.GROUPS.slice(1);
    const W = Math.max(640, widthOf(container)), labelW = 150, top = 30, rowH = 20, bottom = 44;
    const n = metrics.length;
    const cw = (W - labelW - 8) / n;
    const H = top + groups.length * rowH + bottom;
    const svg = svgFor(container, W, H);
    const empty = S.cssVar("--surface-2"), border = S.cssVar("--border"), txt = S.cssVar("--text-2");
    const counts = {};
    groups.forEach((g) => (counts[g] = catalog.filter((c) => c.group === g).length));
    // level bands
    const levels = [["platform", "Platform"], ["s3", "S3"], ["server", "Server (x3)"], ["device", "Device (x21)"]];
    let start = 0;
    levels.forEach(([lv, name]) => {
      const k = metrics.filter((m) => m.level === lv).length;
      const xa = labelW + start * cw, xb = labelW + (start + k) * cw;
      el("text", { x: (xa + xb) / 2, y: 12, "text-anchor": "middle", fill: txt }, svg).textContent = `${name} · ${k}`;
      el("line", { x1: xa + 1, x2: xb - 1, y1: 18, y2: 18, stroke: border, "stroke-width": 2 }, svg);
      if (start > 0) el("line", { x1: xa, x2: xa, y1: 20, y2: top + groups.length * rowH, stroke: S.cssVar("--text-3"), "stroke-width": 1 }, svg);
      start += k;
    });
    groups.forEach((g, gi) => {
      const y = top + gi * rowH;
      el("text", { x: labelW - 10, y: y + rowH / 2 + 4, "text-anchor": "end" }, svg).textContent = g;
      const arr = stats.dimension_label_counts[g];
      metrics.forEach((m, j) => {
        const frac = arr[j] / counts[g];
        const c = seqColor(frac) || empty;
        const r = el("rect", { x: labelW + j * cw, y: y + 1, width: Math.max(1, cw - 0.6), height: rowH - 2, fill: c }, svg);
        r.addEventListener("mousemove", (ev) => S.tip(
          `<b>${S.esc(m.name)}</b><br><span class="t-muted">${S.esc(m.description)}</span><br>` +
          `${S.esc(g)}: labelled in <b>${arr[j]}</b> / ${counts[g]} series`, ev));
        r.addEventListener("mouseleave", () => S.tip(null));
      });
    });
    // legend
    const ly = H - 22, lx = labelW;
    el("text", { x: lx, y: ly + 10 }, svg).textContent = "0%";
    for (let i = 0; i < 10; i++) {
      el("rect", { x: lx + 26 + i * 18, y: ly, width: 17, height: 12, fill: i === 0 ? empty : seqColor((i + 0.5) / 10) }, svg);
    }
    el("text", { x: lx + 26 + 10 * 18 + 6, y: ly + 10 }, svg).textContent = "100% of the scenario's series";
  }

  window.SHADCharts = { barChart, stripPlot, timeline, heatmap, el, niceTicks };
})();