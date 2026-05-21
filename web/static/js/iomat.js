/* IOMAT UI — theme/density toggles, atalhos globais, command palette simples */
(function () {
  "use strict";

  var STORE_THEME = "iomat-theme";
  var STORE_DENSITY = "iomat-density";

  function applyTheme(t) {
    document.documentElement.setAttribute("data-theme", t);
    var icon = document.querySelector("[data-theme-icon]");
    if (icon) icon.textContent = t === "dark" ? "◑" : "◐";
  }
  function getTheme() {
    return localStorage.getItem(STORE_THEME) ||
      (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  function toggleTheme() {
    var t = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    localStorage.setItem(STORE_THEME, t);
    applyTheme(t);
  }

  function applyDensity(d) { document.documentElement.setAttribute("data-density", d); }
  function toggleDensity() {
    var d = document.documentElement.getAttribute("data-density") === "compact" ? "comfortable" : "compact";
    localStorage.setItem(STORE_DENSITY, d);
    applyDensity(d);
  }

  // aplica o quanto antes para evitar flash
  applyTheme(getTheme());
  applyDensity(localStorage.getItem(STORE_DENSITY) || "comfortable");

  document.addEventListener("click", function (ev) {
    var el = ev.target.closest("[data-action]");
    if (!el) return;
    var a = el.getAttribute("data-action");
    if (a === "toggle-theme")   { ev.preventDefault(); toggleTheme(); }
    if (a === "toggle-density") { ev.preventDefault(); toggleDensity(); }
  });

  // Atalhos globais. G seguido de P/B/D/R navega; Cmd/Ctrl+K abre palette.
  var pendingG = false, pendingTimer = null;
  function nav(url) { window.location.href = url; }

  document.addEventListener("keydown", function (ev) {
    // ignorar se usuario esta digitando em input/textarea/select
    var tag = (ev.target.tagName || "").toLowerCase();
    var typing = ev.target.isContentEditable || tag === "input" || tag === "textarea" || tag === "select";

    // Cmd/Ctrl + K -> palette
    if ((ev.metaKey || ev.ctrlKey) && (ev.key === "k" || ev.key === "K")) {
      ev.preventDefault();
      openPalette();
      return;
    }

    if (typing) return;

    if (pendingG) {
      var routes = window.IOMAT_ROUTES || {};
      if (ev.key === "p" || ev.key === "P") { ev.preventDefault(); pendingG = false; if (routes.painel)     nav(routes.painel); return; }
      if (ev.key === "b" || ev.key === "B") { ev.preventDefault(); pendingG = false; if (routes.buscas)     nav(routes.buscas); return; }
      if (ev.key === "d" || ev.key === "D") { ev.preventDefault(); pendingG = false; if (routes.documentos) nav(routes.documentos); return; }
      if (ev.key === "r" || ev.key === "R") { ev.preventDefault(); pendingG = false; if (routes.revisao)    nav(routes.revisao); return; }
      if (ev.key === "v" || ev.key === "V") { ev.preventDefault(); pendingG = false; if (routes.validacao)  nav(routes.validacao); return; }
      pendingG = false;
    }
    if (ev.key === "g" || ev.key === "G") {
      pendingG = true;
      clearTimeout(pendingTimer);
      pendingTimer = setTimeout(function(){ pendingG = false; }, 900);
    }
  });

  // Command palette minimalista
  function openPalette() {
    if (document.getElementById("iomat-palette")) return;
    var overlay = document.createElement("div");
    overlay.id = "iomat-palette";
    overlay.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.35);z-index:9999;display:flex;align-items:flex-start;justify-content:center;padding-top:12vh;";
    overlay.innerHTML = [
      '<div style="width:min(560px,92vw);background:var(--t-surface);border:1px solid var(--t-rule);border-radius:8px;overflow:hidden;font-family:var(--sans);">',
      '  <input id="iomat-palette-input" placeholder="Buscar tela... (P painel, B buscas, D documentos, R revisao)" style="width:100%;border:0;padding:14px 16px;background:var(--t-surface);color:var(--t-ink);font-size:13px;outline:none;border-bottom:1px solid var(--t-rule);" />',
      '  <div id="iomat-palette-list"></div>',
      '</div>'
    ].join("");
    document.body.appendChild(overlay);
    var routes = window.IOMAT_ROUTES || {};
    var items = [
      { k: "Painel",     u: routes.painel },
      { k: "Buscas",     u: routes.buscas },
      { k: "Nova busca", u: routes.buscas_nova },
      { k: "Documentos", u: routes.documentos },
      { k: "Fila de revisao", u: routes.revisao },
      { k: "Validacao",  u: routes.validacao },
      { k: "Perfil",     u: routes.perfil }
    ].filter(function(x){ return !!x.u; });

    function render(q) {
      var list = document.getElementById("iomat-palette-list");
      list.innerHTML = "";
      items.filter(function (x) { return !q || x.k.toLowerCase().indexOf(q.toLowerCase()) >= 0; })
        .forEach(function (x, i) {
          var row = document.createElement("a");
          row.href = x.u;
          row.textContent = x.k;
          row.style.cssText = "display:block;padding:10px 16px;color:var(--t-ink-2);text-decoration:none;font-size:12px;border-top:1px solid var(--t-rule);";
          row.addEventListener("mouseenter", function(){ row.style.background = "var(--t-surface-2)"; });
          row.addEventListener("mouseleave", function(){ row.style.background = ""; });
          list.appendChild(row);
        });
    }
    render("");
    var input = document.getElementById("iomat-palette-input");
    input.focus();
    input.addEventListener("input", function () { render(input.value); });

    function close(){ overlay.remove(); document.removeEventListener("keydown", esc); }
    function esc(ev){ if (ev.key === "Escape") { ev.preventDefault(); close(); } }
    overlay.addEventListener("click", function (ev) { if (ev.target === overlay) close(); });
    document.addEventListener("keydown", esc);
  }
})();
