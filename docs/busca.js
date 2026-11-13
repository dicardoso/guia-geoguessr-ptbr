/* Busca em todas as pistas do guia (licença MIT). Usa window.PISTAS (pistas.js). */
(function () {
  "use strict";
  var D = window.PISTAS;
  var $ = function (id) { return document.getElementById(id); };
  var q = $("q"), selCont = $("cont"), chips = $("cats"), status = $("status"),
      lista = $("resultados"), mais = $("mais");
  if (!D || !q) { if (status) status.textContent = "Não foi possível carregar o índice de pistas."; return; }

  /* Normalização que preserva o tamanho do texto (para poder destacar no original). */
  var ACENTOS = { "á": "a", "à": "a", "â": "a", "ã": "a", "ä": "a", "å": "a", "é": "e", "è": "e", "ê": "e",
    "ë": "e", "í": "i", "ì": "i", "î": "i", "ï": "i", "ó": "o", "ò": "o", "ô": "o", "õ": "o", "ö": "o",
    "ú": "u", "ù": "u", "û": "u", "ü": "u", "ç": "c", "ñ": "n", "ý": "y", "ÿ": "y", "ø": "o", "ő": "o",
    "ű": "u", "š": "s", "ž": "z", "č": "c", "ć": "c", "đ": "d", "ł": "l", "ń": "n", "ś": "s", "ź": "z",
    "ż": "z", "ř": "r", "ě": "e", "ů": "u", "ğ": "g", "ş": "s", "ı": "i", "ā": "a", "ē": "e", "ī": "i",
    "ō": "o", "ū": "u", "ë": "e", "‘": "'", "’": "'", "“": "\"", "”": "\"" };
  function norm(s) {
    var b = s.toLowerCase(), out = "";
    for (var i = 0; i < b.length; i++) { var c = b[i]; out += ACENTOS[c] || c; }
    return out.length === s.length ? out : s.toLowerCase(); // segurança: nunca desalinhar
  }
  function esc(s) {
    return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;" }[c]; });
  }

  /* Prepara o índice */
  var paginas = D.paginas, cats = D.categorias;
  var itens = D.pistas.map(function (p) {
    var pg = paginas[p[0]];
    return {
      pagina: p[0], secao: pg[2][p[1]] || "", id: p[2], img: p[3], texto: p[4], cats: p[5],
      titulo: pg[0], cont: pg[1], n: norm(p[4]), nomes: norm(pg[0] + " " + pg[3].join(" "))
    };
  });

  /* Filtros */
  D.continentes.forEach(function (c) {
    var o = document.createElement("option"); o.value = c; o.textContent = c; selCont.appendChild(o);
  });
  var catAtiva = "";
  function criarChip(id, rotulo) {
    var b = document.createElement("button");
    b.type = "button"; b.className = "chip"; b.textContent = rotulo; b.dataset.cat = id;
    b.setAttribute("aria-pressed", id === catAtiva ? "true" : "false");
    b.addEventListener("click", function () { catAtiva = (catAtiva === id ? "" : id); atualizarChips(); buscar(); });
    chips.appendChild(b);
  }
  criarChip("", "Todas");
  cats.forEach(function (c) { criarChip(c[0], c[1]); });
  function atualizarChips() {
    chips.querySelectorAll(".chip").forEach(function (b) {
      b.setAttribute("aria-pressed", b.dataset.cat === catAtiva ? "true" : "false");
    });
  }
  function bitDaCategoria(id) {
    for (var i = 0; i < cats.length; i++) if (cats[i][0] === id) return 1 << i;
    return 0;
  }

  /* Termos: palavras soltas e "frases entre aspas" (sem palavras muito comuns) */
  var PARADA = {};
  "de da do das dos em no na nos nas com um uma uns umas os as que para por pelo pela ou se sao tem".split(" ")
    .forEach(function (w) { PARADA[w] = 1; });
  function termos(texto) {
    var t = [], s = norm(texto).replace(/"([^"]+)"/g, function (_, f) { t.push(f.trim()); return " "; });
    s.split(/\s+/).forEach(function (w) { if (w.length >= 2 && !PARADA[w]) t.push(w); });
    return t.filter(Boolean);
  }
  function contar(h, t) { var n = 0, i = h.indexOf(t); while (i > -1 && n < 5) { n++; i = h.indexOf(t, i + t.length); } return n; }

  function trecho(item, ts) {
    var pos = -1;
    ts.forEach(function (t) { var i = item.n.indexOf(t); if (i > -1 && (pos === -1 || i < pos)) pos = i; });
    var ini = 0, fim = Math.min(item.texto.length, 260);
    if (pos > 90) {
      ini = item.texto.lastIndexOf(" ", pos - 70); ini = ini < 0 ? 0 : ini + 1;
      fim = Math.min(item.texto.length, ini + 260);
    }
    var orig = item.texto.slice(ini, fim), n = item.n.slice(ini, fim);
    var marcas = [];
    ts.forEach(function (t) { var i = n.indexOf(t); while (i > -1) { marcas.push([i, i + t.length]); i = n.indexOf(t, i + t.length); } });
    marcas.sort(function (a, b) { return a[0] - b[0]; });
    var html = "", cur = 0;
    marcas.forEach(function (m) {
      if (m[0] < cur) return;
      html += esc(orig.slice(cur, m[0])) + "<mark>" + esc(orig.slice(m[0], m[1])) + "</mark>"; cur = m[1];
    });
    html += esc(orig.slice(cur));
    return (ini > 0 ? "… " : "") + html + (fim < item.texto.length ? " …" : "");
  }

  var achados = [], mostrados = 0, POR_VEZ = 40, termosAtuais = [];
  function buscar() {
    var ts = termos(q.value), cont = selCont.value, bit = bitDaCategoria(catAtiva);
    termosAtuais = ts;
    sincronizarURL();
    if (!ts.length && !bit && !cont) {
      achados = []; lista.innerHTML = ""; mais.hidden = true;
      status.innerHTML = "Digite o que você está vendo ou escolha uma categoria. Exemplos: " +
        ["poste escada", "placa amarela", "terra vermelha", "bollard", "cirílico", "snorkel"].map(function (e) {
          return '<button type="button" class="exemplo">' + e + "</button>";
        }).join(" ");
      status.querySelectorAll(".exemplo").forEach(function (b) {
        b.addEventListener("click", function () { q.value = b.textContent; buscar(); q.focus(); });
      });
      return;
    }
    achados = [];
    for (var i = 0; i < itens.length; i++) {
      var it = itens[i];
      if (cont && it.cont !== cont) continue;
      if (bit && !(it.cats & bit)) continue;
      var pontos = 0, ok = true;
      for (var j = 0; j < ts.length; j++) {
        var c = contar(it.n, ts[j]), nome = it.nomes.indexOf(ts[j]) > -1;
        if (!c && !nome) { ok = false; break; }
        pontos += c + (nome ? 3 : 0);
      }
      if (ok) achados.push({ it: it, pontos: pontos, ordem: i });
    }
    if (ts.length) achados.sort(function (a, b) { return b.pontos - a.pontos || a.ordem - b.ordem; });
    var paises = {};
    achados.forEach(function (a) { paises[a.it.pagina] = 1; });
    var np = Object.keys(paises).length;
    status.textContent = achados.length
      ? achados.length + (achados.length === 1 ? " pista encontrada" : " pistas encontradas") +
        " em " + np + (np === 1 ? " página." : " páginas.")
      : "Nenhuma pista encontrada. Tente menos palavras ou outra forma (ex.: “poste” em vez de “postes de concreto”).";
    lista.innerHTML = ""; mostrados = 0; mostrarMais();
  }

  function mostrarMais() {
    var frag = document.createDocumentFragment();
    achados.slice(mostrados, mostrados + POR_VEZ).forEach(function (a) {
      var it = a.it, li = document.createElement("li");
      li.className = "resultado";
      li.innerHTML =
        '<a href="' + it.pagina + ".html#" + it.id + '">' +
        (it.img ? '<img src="' + esc(it.img) + '" alt="" loading="lazy" decoding="async">' : '<span class="sem-img">¶</span>') +
        '<span class="corpo"><span class="onde"><strong>' + esc(it.titulo) + "</strong>" +
        (it.secao ? " · " + esc(it.secao) : "") + "</span>" +
        '<span class="trecho">' + trecho(it, termosAtuais) + "</span></span></a>";
      frag.appendChild(li);
    });
    lista.appendChild(frag);
    mostrados = Math.min(achados.length, mostrados + POR_VEZ);
    mais.hidden = mostrados >= achados.length;
  }

  function sincronizarURL() {
    try {
      var p = new URLSearchParams();
      if (q.value.trim()) p.set("q", q.value.trim());
      if (catAtiva) p.set("cat", catAtiva);
      if (selCont.value) p.set("cont", selCont.value);
      var s = p.toString();
      history.replaceState(null, "", s ? "?" + s : location.pathname);
    } catch (e) {}
  }

  /* Estado inicial a partir da URL (?q=...&cat=...&cont=...) */
  try {
    var u = new URLSearchParams(location.search);
    if (u.get("q")) q.value = u.get("q");
    if (u.get("cat")) { catAtiva = u.get("cat"); atualizarChips(); }
    if (u.get("cont")) selCont.value = u.get("cont");
  } catch (e) {}

  var timer;
  q.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(buscar, 150); });
  selCont.addEventListener("change", buscar);
  mais.addEventListener("click", mostrarMais);
  buscar();
})();
