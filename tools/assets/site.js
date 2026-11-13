/* Guia de GeoGuessr em Português — comportamento do site (licença MIT) */
(function () {
  "use strict";
  var raiz = document.documentElement;

  /* ---------- Tema claro / escuro / automático ---------- */
  var temas = ["auto", "light", "dark"];
  var icones = { auto: "◐", light: "☀", dark: "☾" };
  var nomes = { auto: "automático", light: "claro", dark: "escuro" };
  function temaAtual() { return raiz.getAttribute("data-theme") || "auto"; }
  function aplicarTema(t) {
    if (t === "auto") raiz.removeAttribute("data-theme"); else raiz.setAttribute("data-theme", t);
    try { localStorage.setItem("tema", t); } catch (e) {}
    var b = document.getElementById("tema-btn");
    if (b) { b.textContent = icones[t]; b.title = "Tema: " + nomes[t] + " (clique para trocar)"; }
  }
  var temaBtn = document.getElementById("tema-btn");
  if (temaBtn) {
    aplicarTema(temaAtual());
    temaBtn.addEventListener("click", function () {
      aplicarTema(temas[(temas.indexOf(temaAtual()) + 1) % temas.length]);
    });
  }

  /* ---------- Zoom de imagens ---------- */
  var imagens = Array.prototype.slice.call(document.querySelectorAll("main figure img"));
  var dlg = document.getElementById("zoom");
  if (dlg && imagens.length && typeof dlg.showModal === "function") {
    var zImg = dlg.querySelector("img"), zPos = dlg.querySelector(".pos"),
        zOrig = dlg.querySelector(".orig"), atual = 0;
    function mostrar(i) {
      atual = (i + imagens.length) % imagens.length;
      var src = imagens[atual].getAttribute("data-grande") || imagens[atual].src;
      zImg.src = src; zImg.alt = imagens[atual].alt || "";
      zOrig.href = src;
      zPos.textContent = (atual + 1) + " / " + imagens.length;
    }
    imagens.forEach(function (img, i) {
      var link = img.closest("a");
      (link || img).addEventListener("click", function (ev) {
        ev.preventDefault(); mostrar(i); dlg.showModal();
      });
    });
    dlg.querySelector(".ant").addEventListener("click", function (e) { e.stopPropagation(); mostrar(atual - 1); });
    dlg.querySelector(".prox").addEventListener("click", function (e) { e.stopPropagation(); mostrar(atual + 1); });
    dlg.querySelector(".fechar").addEventListener("click", function () { dlg.close(); });
    zOrig.addEventListener("click", function (e) { e.stopPropagation(); });
    dlg.addEventListener("click", function (e) { if (e.target === dlg || e.target === zImg) dlg.close(); });
    dlg.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") mostrar(atual - 1);
      if (e.key === "ArrowRight") mostrar(atual + 1);
    });
    dlg.addEventListener("close", function () { zImg.removeAttribute("src"); });
  }

  /* ---------- Sumário: seção ativa + painel no celular ---------- */
  var lateral = document.querySelector(".lateral");
  var linksSumario = lateral ? lateral.querySelectorAll("a[href^='#']") : [];
  if (linksSumario.length && "IntersectionObserver" in window) {
    var porId = {};
    linksSumario.forEach(function (a) { porId[a.getAttribute("href").slice(1)] = a; });
    var titulos = Array.prototype.slice.call(document.querySelectorAll("main h3[id]"));
    function marcar() {
      var ativo = titulos[0];
      titulos.forEach(function (h) { if (h.getBoundingClientRect().top < 140) ativo = h; });
      linksSumario.forEach(function (a) { a.classList.remove("ativo"); });
      if (ativo && porId[ativo.id]) porId[ativo.id].classList.add("ativo");
    }
    var agendado = false;
    window.addEventListener("scroll", function () {
      if (agendado) return; agendado = true;
      requestAnimationFrame(function () { agendado = false; marcar(); });
    }, { passive: true });
    marcar();
  }
  var secoesBtn = document.getElementById("secoes-btn");
  if (secoesBtn && lateral) {
    secoesBtn.addEventListener("click", function (e) {
      e.stopPropagation(); lateral.classList.toggle("aberto");
      secoesBtn.setAttribute("aria-expanded", lateral.classList.contains("aberto"));
    });
    lateral.addEventListener("click", function (e) {
      if (e.target.closest("a")) lateral.classList.remove("aberto");
    });
    document.addEventListener("click", function (e) {
      if (!lateral.contains(e.target)) lateral.classList.remove("aberto");
    });
  }

  /* ---------- Voltar ao topo ---------- */
  var topoBtn = document.getElementById("topo-btn");
  if (topoBtn) {
    window.addEventListener("scroll", function () {
      topoBtn.classList.toggle("visivel", window.scrollY > 900);
    }, { passive: true });
    topoBtn.addEventListener("click", function () { window.scrollTo({ top: 0 }); });
  }

  /* ---------- Busca de países no índice ---------- */
  var busca = document.getElementById("busca");
  if (busca) {
    var norm = function (s) { return s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); };
    var vazio = document.getElementById("vazio");
    busca.addEventListener("input", function () {
      var q = norm(busca.value.trim()), algum = false;
      document.querySelectorAll(".continente").forEach(function (sec) {
        var visiveis = 0;
        sec.querySelectorAll("li[data-nome]").forEach(function (li) {
          var ok = li.getAttribute("data-nome").indexOf(q) > -1;
          li.hidden = !ok; if (ok) visiveis++;
        });
        sec.hidden = visiveis === 0; if (visiveis) algum = true;
      });
      if (vazio) vazio.style.display = algum ? "none" : "block";
    });
  }
})();
