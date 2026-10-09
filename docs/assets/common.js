/* SHAD website - shared helpers (no build step, no dependencies) */
(function () {
  "use strict";

  const CONFIG = {
    repo: "scality/shad",
    branch: "main",
    // TODO: replace with the proceedings / arXiv link once available.
    paperUrl: null,
    siteUrl: "https://scality.github.io/shad/",
  };

  const GROUPS = [
    "Nominal",
    "Single Disk", "Simultaneous Disk", "Asynchronous Disk",
    "Single Server", "Asynchronous Server", "Server Degradation",
    "Single SNode", "Simultaneous SNode", "Asynchronous SNode",
  ];
  const FAMILY = { None: "Nominal", Disk: "Disk", Server: "Server", SNode: "Storage node" };
  const FAMILY_VAR = { None: "--nominal", Disk: "--disk", Server: "--server", SNode: "--snode" };
  const GROUP_TYPE = {
    "Nominal": "None", "Single Disk": "Disk", "Simultaneous Disk": "Disk", "Asynchronous Disk": "Disk",
    "Single Server": "Server", "Asynchronous Server": "Server", "Server Degradation": "Server",
    "Single SNode": "SNode", "Simultaneous SNode": "SNode", "Asynchronous SNode": "SNode",
  };

  // ------------------------------------------------------------------ theme
  function applyTheme(t) {
    if (t) document.documentElement.setAttribute("data-theme", t);
    else document.documentElement.removeAttribute("data-theme");
  }
  try { applyTheme(localStorage.getItem("shad-theme")); } catch (e) { /* storage unavailable */ }
  function currentTheme() {
    const t = document.documentElement.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function toggleTheme() {
    const next = currentTheme() === "dark" ? "light" : "dark";
    applyTheme(next);
    try { localStorage.setItem("shad-theme", next); } catch (e) { /* ignore */ }
    document.dispatchEvent(new CustomEvent("shad-theme"));
  }
  const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const typeColor = (type) => cssVar(FAMILY_VAR[type] || "--nominal");
  const groupColor = (group) => typeColor(GROUP_TYPE[group] || "None");

  // ------------------------------------------------------------------ nav
  const ICONS = {
    github: '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>',
    moon: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
    sun: '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    paper: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h5"/></svg>',
    explore: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 12h4l3-8 4 16 3-8h4"/></svg>',
    book: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/></svg>',
    download: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>',
  };
  const LOGO = '<svg class="brand-mark" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="8" fill="var(--accent)"/><path d="M5 20 L10 20 L13 11 L17 24 L20 16 L27 16" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/><circle cx="17" cy="24" r="2.6" fill="#ffb4b3" stroke="#fff" stroke-width="1.2"/></svg>';

  function renderNav(active) {
    const el = document.getElementById("nav");
    if (!el) return;
    const link = (href, label, key, cls = "") =>
      `<a href="${href}" class="${active === key ? "active" : ""} ${cls}">${label}</a>`;
    el.className = "nav";
    el.innerHTML = `<div class="nav-inner">
      <a class="brand" href="index.html">${LOGO}<span>SHAD</span></a>
      <nav class="nav-links" aria-label="Main">
        ${link("index.html", "Overview", "home", "hide-sm")}
        ${link("explorer.html", "Explorer", "explorer")}
        ${link("docs.html", "Docs", "docs")}
        ${link("docs.html#catalog", "Catalog", "catalog", "hide-sm")}
        <a href="https://github.com/${CONFIG.repo}" title="GitHub repository" aria-label="GitHub repository" style="display:inline-flex"><span style="width:18px;height:18px;display:inline-block">${ICONS.github}</span></a>
        <button class="icon-btn" id="theme-btn" title="Toggle dark mode" aria-label="Toggle dark mode"></button>
      </nav></div>`;
    const btn = document.getElementById("theme-btn");
    const paint = () => { btn.innerHTML = currentTheme() === "dark" ? ICONS.sun : ICONS.moon; };
    paint();
    btn.addEventListener("click", () => { toggleTheme(); paint(); });
  }

  // ------------------------------------------------------------------ data access
  function isLocal() {
    const h = location.hostname;
    return location.protocol === "file:" || h === "localhost" || h === "127.0.0.1" || h === "" || h.endsWith(".local");
  }
  function rawBase() {
    return `https://raw.githubusercontent.com/${CONFIG.repo}/${CONFIG.branch}/`;
  }
  function dataBases() {
    const q = new URLSearchParams(location.search).get("data");
    if (q) return [q.endsWith("/") ? q : q + "/"];
    // Served locally from the repository root (python -m http.server): read ../Dataset directly.
    return isLocal() ? ["../", rawBase()] : [rawBase()];
  }
  const encPath = (p) => p.split("/").map(encodeURIComponent).join("/");
  async function fetchRepoFile(path) {
    let lastErr;
    for (const base of dataBases()) {
      try {
        const r = await fetch(base + encPath(path));
        if (r.ok) return await r.text();
        lastErr = new Error(`${r.status} ${r.statusText} for ${base + path}`);
      } catch (e) { lastErr = e; }
    }
    throw lastErr;
  }
  const repoUrl = (path) => `https://github.com/${CONFIG.repo}/blob/${CONFIG.branch}/${encPath(path)}`;
  const rawUrl = (path) => rawBase() + encPath(path);

  const _json = {};
  function loadJSON(name) {
    if (!_json[name]) _json[name] = fetch(`data/${name}.json`).then((r) => {
      if (!r.ok) throw new Error(`Cannot load data/${name}.json`);
      return r.json();
    });
    return _json[name];
  }

  // ------------------------------------------------------------------ tooltip
  let tipEl;
  function tip(html, ev) {
    if (!tipEl) {
      tipEl = document.createElement("div");
      tipEl.className = "tooltip";
      tipEl.setAttribute("role", "tooltip");
      document.body.appendChild(tipEl);
    }
    if (!html) { tipEl.classList.remove("show"); return; }
    tipEl.innerHTML = html;
    tipEl.classList.add("show");
    const pad = 14, w = tipEl.offsetWidth, h = tipEl.offsetHeight;
    let x = ev.clientX + pad, y = ev.clientY + pad;
    if (x + w > window.innerWidth - 8) x = ev.clientX - w - pad;
    if (y + h > window.innerHeight - 8) y = ev.clientY - h - pad;
    tipEl.style.left = Math.max(8, x) + "px";
    tipEl.style.top = Math.max(8, y) + "px";
  }

  // ------------------------------------------------------------------ formatting
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  function fmtNum(v, digits = 3) {
    if (v === null || v === undefined || Number.isNaN(v)) return "–";
    const a = Math.abs(v);
    if (a !== 0 && (a >= 1e6 || a < 1e-3)) return v.toExponential(2);
    if (a >= 1000) return v.toLocaleString("en-US", { maximumFractionDigits: 0 });
    return Number(v.toPrecision(digits)).toString();
  }
  function fmtCompact(v) {
    if (v === null || v === undefined || Number.isNaN(v)) return "–";
    const a = Math.abs(v);
    if (a >= 1e9) return (v / 1e9).toFixed(1).replace(/\.0$/, "") + "G";
    if (a >= 1e6) return (v / 1e6).toFixed(1).replace(/\.0$/, "") + "M";
    if (a >= 1e3) return (v / 1e3).toFixed(1).replace(/\.0$/, "") + "k";
    if (a > 0 && a < 0.01) return v.toExponential(0);
    return Number(v.toPrecision(3)).toString();
  }
  function fmtMinutes(m) {
    if (m === null || m === undefined) return "until end";
    const h = Math.floor(m / 60), mm = Math.round(m % 60);
    if (!h) return `${mm} min`;
    return mm ? `${h}h${String(mm).padStart(2, "0")}` : `${h}h`;
  }

  function badge(text, color, cls = "") {
    const dot = color ? `<span class="dot" style="background:${color}"></span>` : "";
    return `<span class="badge ${cls}">${dot}${esc(text)}</span>`;
  }

  // ------------------------------------------------------------------ tiny python highlighter
  function highlightPython(code) {
    const kw = /\b(from|import|as|for|in|print|def|return|if|else|with|lambda|True|False|None)\b/g;
    return code.split("\n").map((line) => {
      const ci = line.indexOf("#");
      let src = ci >= 0 ? line.slice(0, ci) : line;
      const com = ci >= 0 ? line.slice(ci) : "";
      src = esc(src)
        .replace(/(&quot;[^&]*?&quot;|&#39;[^&]*?&#39;)/g, '<span class="tok-s">$1</span>')
        .replace(kw, '<span class="tok-k">$1</span>');
      return src + (com ? `<span class="tok-c">${esc(com)}</span>` : "");
    }).join("\n");
  }
  function enhanceCode(root = document) {
    root.querySelectorAll("pre[data-lang]").forEach((pre) => {
      const code = pre.textContent.replace(/^\n/, "").replace(/\s+$/, "");
      if (pre.dataset.lang === "python") pre.innerHTML = highlightPython(code);
      else pre.textContent = code;
      const wrap = document.createElement("div");
      wrap.className = "copy-wrap";
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(pre);
      const b = document.createElement("button");
      b.className = "copy-btn"; b.type = "button"; b.textContent = "Copy";
      b.addEventListener("click", async () => {
        try { await navigator.clipboard.writeText(code); b.textContent = "Copied"; }
        catch (e) { b.textContent = "Select & copy"; }
        setTimeout(() => (b.textContent = "Copy"), 1400);
      });
      wrap.appendChild(b);
    });
  }

  function renderPaperLinks() {
    document.querySelectorAll("[data-paper-link]").forEach((a) => {
      if (CONFIG.paperUrl) { a.href = CONFIG.paperUrl; }
      else { a.removeAttribute("href"); a.title = "Link coming soon"; a.style.opacity = 0.6; a.style.cursor = "default"; }
    });
  }

  window.SHADSite = {
    CONFIG, GROUPS, GROUP_TYPE, FAMILY, ICONS,
    cssVar, typeColor, groupColor, currentTheme,
    renderNav, fetchRepoFile, repoUrl, rawUrl, loadJSON,
    tip, esc, fmtNum, fmtCompact, fmtMinutes, badge, enhanceCode, renderPaperLinks,
  };
})();
