/* SHAD website - landing page */
(function () {
  "use strict";
  const S = window.SHADSite, C = window.SHADCharts;
  S.renderNav("home");
  S.renderPaperLinks();
  for (const [id, icon] of [["ic-explore", "explore"], ["ic-book", "book"], ["ic-github", "github"], ["ic-paper", "paper"]]) {
    const e = document.getElementById(id);
    if (e) { e.innerHTML = S.ICONS[icon]; e.style.cssText = "width:16px;height:16px;display:inline-flex"; }
  }
  S.enhanceCode();

  // result tabs
  document.querySelectorAll(".results-tabs button").forEach((b) => b.addEventListener("click", () => {
    document.querySelectorAll(".results-tabs button").forEach((x) => x.setAttribute("aria-selected", x === b));
    document.querySelectorAll(".result-panel").forEach((p) => p.classList.toggle("active", p.id === b.dataset.panel));
  }));

  drawTopology();

  Promise.all([S.loadJSON("catalog"), S.loadJSON("stats"), S.loadJSON("metrics")]).then(([cat, stats, metrics]) => {
    const anomalous = cat.filter((c) => c.group !== "Nominal");
    const UNRECOVERED = new Set(["1773429328", "1773429404", "1773680834", "1773680847", "1773680864", "1773680884", "1773680896", "1773429588", "1773946658", "1773946737"]);
    const nEvents = anomalous.reduce((a, c) => a + c.events.length, 0);
    const tiles = [
      [cat.length, "time series"],
      [metrics.length, "dimensions per series"],
      [Math.round(stats.n_points / 1000) + "k", "timestamps (1 min)"],
      [anomalous.length, "anomalous series"],
      [nEvents, "annotated anomaly events"],
      [S.GROUPS.length, "scenarios (incl. nominal)"],
    ];
    document.getElementById("hero-stats").innerHTML = tiles.map(([v, l]) =>
      `<div class="stat"><div class="v">${v}</div><div class="l">${l}</div></div>`).join("");

    for (const t of ["Disk", "Server", "SNode"]) {
      const n = cat.filter((c) => c.type === t).length;
      const e = document.getElementById("count-" + t);
      if (e) e.innerHTML = `${n} <span class="muted small" style="font-weight:400">series</span>`;
    }
    document.getElementById("family-legend").innerHTML = [["Disk", "Disk failure"], ["Server", "Server failure"], ["SNode", "Storage node failure"], ["None", "No anomaly"]]
      .map(([t, l]) => `<span class="key"><span class="sw" style="background:${S.typeColor(t)}"></span>${l}</span>`).join("");

    const draw = () => {
      C.timeline(document.getElementById("chart-timeline"), cat);

      C.barChart(document.getElementById("chart-groups"), S.GROUPS.map((g) => ({
        label: g, value: cat.filter((c) => c.group === g).length, color: S.groupColor(g),
        href: `docs.html#catalog`,
      })), { tip: (r) => `<b>${r.label}</b>: ${r.value} series` });

      const groups = S.GROUPS.slice(1);
      const segPts = [];
      anomalous.forEach((c) => c.segments_min.forEach(([s, e]) => segPts.push({
        group: c.group, value: Math.round(e - s), color: S.groupColor(c.group), c,
        href: `explorer.html#id=${c.id}`,
      })));
      C.stripPlot(document.getElementById("chart-durations"), segPts, {
        groups, log: true, logFloor: 1,
        ticks: [1, 5, 15, 30, 60, 120, 240, 480],
        tickFormat: (t) => (t >= 60 ? `${t / 60}h` : `${t}m`),
        tip: (p) => `<b>${p.c.id}</b> · ${S.esc(p.group)}<br>anomalous period of <b>${p.value} min</b>`,
      });
      C.stripPlot(document.getElementById("chart-ratio"), anomalous.map((c) => ({
        group: c.group, value: c.anomaly_ratio * 100, color: S.groupColor(c.group), c, href: `explorer.html#id=${c.id}`, emph: UNRECOVERED.has(String(c.id)),
      })), {
        groups, min: 0, tickFormat: (t) => `${t}%`,
        tip: (p) => `<b>${p.c.id}</b> · ${S.esc(p.group)}<br><b>${p.value.toFixed(1)}%</b> of timestamps anomalous` + (p.emph ? `<br><b>Failure not recovered</b> during the run` : ""),
      });
      C.stripPlot(document.getElementById("chart-dims"), anomalous.map((c) => ({
        group: c.group, value: c.labeled_dimensions.length, color: S.groupColor(c.group), c, href: `explorer.html#id=${c.id}`,
      })), {
        groups, log: true, logFloor: 1, min: 3, max: 171, ticks: [4, 8, 16, 47, 94, 171], tickFormat: (t) => String(t),
        tip: (p) => `<b>${p.c.id}</b> · ${S.esc(p.group)}<br><b>${p.value}</b> labelled dimensions`,
      });
      C.heatmap(document.getElementById("chart-heatmap"), stats, metrics, cat);
    };
    draw();
    let t;
    window.addEventListener("resize", () => { clearTimeout(t); t = setTimeout(draw, 150); });
    document.addEventListener("shad-theme", draw);
  }).catch((e) => {
    document.getElementById("hero-stats").innerHTML = `<p class="muted">Could not load the dataset statistics (${S.esc(e.message)}).</p>`;
  });

  // ------------------------------------------------------------------ topology diagram
  function drawTopology() {
    const g = document.getElementById("servers"), lv = document.getElementById("levels");
    if (!g) return;
    const E = C.el;
    [0, 1, 2].forEach((i) => {
      const x = 10 + i * 230, y = 80;
      const grp = E("g", { transform: `translate(${x},${y})` }, g);
      E("rect", { class: "srv", x: 0, y: 0, width: 200, height: 238, rx: 8 }, grp);
      E("text", { class: "t-strong", x: 100, y: 20, "text-anchor": "middle" }, grp).textContent = `Storage server ${i + 1} (store${i + 1})`;
      E("rect", { class: "box", x: 12, y: 32, width: 176, height: 28, rx: 5 }, grp);
      E("text", { x: 100, y: 50, "text-anchor": "middle" }, grp).textContent = "S3 connector";
      E("text", { x: 12, y: 80 }, grp).textContent = "6 storage nodes (Chord DHT)";
      for (let k = 0; k < 6; k++) {
        E("rect", { class: "sn", x: 12 + k * 29.5, y: 88, width: 25, height: 22, rx: 4 }, grp);
        E("text", { x: 12 + k * 29.5 + 12.5, y: 103, "text-anchor": "middle", style: "font-size:9px" }, grp).textContent = `n${k + 1}`;
      }
      E("text", { x: 12, y: 132 }, grp).textContent = "Devices";
      const devs = [["g1disk01", "nvme"], ["g1disk02", "nvme"], ["g2disk01", "nvme"], ["g2disk02", "nvme"], ["ssd01", "ssd"], ["ssd02", "ssd"], ["root", "ssd"]];
      devs.forEach(([d, cls], k) => {
        const dx = 12 + k * 25;
        E("rect", { class: cls, x: dx, y: 140, width: 21, height: 60, rx: 3 }, grp);
        E("text", { x: dx + 14, y: 195, "text-anchor": "start", transform: `rotate(-90 ${dx + 14} 195)`, style: "font-size:9px" }, grp).textContent = d;
      });
      E("text", { x: 12, y: 222, style: "font-size:10px" }, grp).textContent = "4 NVMe data · 2 SSD metadata · 1 OS";
    });
    const levels = [["Platform", "cluster aggregates", 17], ["S3", "connector / application", 13], ["Server", "19 metrics × 3 servers", 57], ["Device", "4 metrics × 7 devices × 3", 84]];
    levels.forEach(([n, d, k], i) => {
      const y = 24 + i * 62;
      E("rect", { class: "lvl", x: 0, y, width: 240, height: 52, rx: 6 }, lv);
      E("text", { class: "lvl-n", x: 14, y: y + 32 }, lv).textContent = k;
      E("text", { class: "t-strong", x: 56, y: y + 22 }, lv).textContent = n;
      E("text", { x: 56, y: y + 38 }, lv).textContent = d;
    });
    E("text", { x: 0, y: 24 + 4 * 62 + 16, style: "font-size:11px" }, lv).textContent = "Sampled every minute, ~18 h per experiment";
  }
})();