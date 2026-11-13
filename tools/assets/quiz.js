/* Quiz: veja uma pista e adivinhe o país (licença MIT). Usa window.PISTAS (pistas.js). */
(function () {
  "use strict";
  var D = window.PISTAS;
  var $ = function (id) { return document.getElementById(id); };
  var carta = $("qz-carta"), selCont = $("qz-cont"), selDif = $("qz-dif");
  if (!D || !carta) { if (carta) carta.innerHTML = '<p class="status">Não foi possível carregar as pistas.</p>'; return; }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;" }[c]; });
  }
  function aleatorio(lista) { return lista[Math.floor(Math.random() * lista.length)]; }
  function embaralhar(a) {
    for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }
  function ler(chave) { try { return parseInt(localStorage.getItem(chave), 10) || 0; } catch (e) { return 0; } }
  function gravar(chave, v) { try { localStorage.setItem(chave, String(v)); } catch (e) {} }

  var paginas = D.paginas;
  var todas = D.pistas.filter(function (p) { return p[6] === 1; });
  var paisesComPistas = {};
  todas.forEach(function (p) { paisesComPistas[p[0]] = 1; });
  var listaPaises = Object.keys(paisesComPistas);

  D.continentes.forEach(function (c) {
    var o = document.createElement("option"); o.value = c; o.textContent = c; selCont.appendChild(o);
  });
  try {
    var salvo = JSON.parse(localStorage.getItem("quiz-opcoes") || "{}");
    if (salvo.cont) selCont.value = salvo.cont;
    if (salvo.dif) selDif.value = salvo.dif;
  } catch (e) {}

  var acertos = 0, total = 0, seq = 0, rec = ler("quiz-recorde"), recentes = [], atual = null, respondido = false;

  function placar() {
    $("qz-acertos").textContent = acertos; $("qz-total").textContent = total;
    $("qz-seq").textContent = seq; $("qz-rec").textContent = rec;
  }

  function nova() {
    var cont = selCont.value;
    var pool = todas.filter(function (p) { return !cont || paginas[p[0]][1] === cont; });
    if (!pool.length) { carta.innerHTML = '<p class="status">Nenhuma pista para esse filtro.</p>'; return; }
    var p, tentativas = 0;
    do { p = aleatorio(pool); tentativas++; } while (recentes.indexOf(p[2] + p[0]) > -1 && tentativas < 30);
    recentes.push(p[2] + p[0]); if (recentes.length > 60) recentes.shift();

    var certo = p[0], contCerto = paginas[certo][1];
    var candidatos = listaPaises.filter(function (s) {
      return s !== certo && (selDif.value === "facil" || paginas[s][1] === contCerto);
    });
    if (candidatos.length < 3) candidatos = listaPaises.filter(function (s) { return s !== certo; });
    var opcoes = embaralhar(embaralhar(candidatos.slice()).slice(0, 3).concat([certo]));
    atual = { p: p, certo: certo, opcoes: opcoes };
    respondido = false;

    var grande = p[3].replace(/\/images\/resize\/\d+\//, "/images/resize/1200/");
    carta.innerHTML =
      '<figure class="quiz-img"><a href="' + esc(grande) + '" target="_blank" rel="noopener" title="Abrir imagem ampliada">' +
      '<img src="' + esc(p[3]) + '" alt="Pista do quiz"></a></figure>' +
      '<div class="quiz-alternativas">' +
      opcoes.map(function (s, i) {
        return '<button type="button" class="alternativa" data-pais="' + s + '"><kbd>' + (i + 1) + "</kbd> " +
          esc(paginas[s][0]) + "</button>";
      }).join("") + "</div>" +
      '<div id="qz-resposta" class="quiz-resposta" hidden></div>';
    carta.querySelectorAll(".alternativa").forEach(function (b) {
      b.addEventListener("click", function () { responder(b.dataset.pais); });
    });
  }

  function responder(escolha) {
    if (respondido || !atual) return;
    respondido = true; total++;
    var ok = escolha === atual.certo;
    if (ok) { acertos++; seq++; if (seq > rec) { rec = seq; gravar("quiz-recorde", rec); } } else { seq = 0; }
    placar();
    carta.querySelectorAll(".alternativa").forEach(function (b) {
      b.disabled = true;
      if (b.dataset.pais === atual.certo) b.classList.add("certa");
      else if (b.dataset.pais === escolha) b.classList.add("errada");
    });
    var p = atual.p, pg = paginas[atual.certo], secao = pg[2][p[1]] || "";
    var r = $("qz-resposta");
    r.hidden = false;
    r.className = "quiz-resposta " + (ok ? "ok" : "erro");
    r.innerHTML =
      "<p class=\"veredito\">" + (ok ? "✓ Acertou!" : "✗ Era <strong>" + esc(pg[0]) + "</strong>") + "</p>" +
      (secao ? '<p class="onde">' + esc(pg[0]) + " · " + esc(secao) + "</p>" : "") +
      "<p>" + esc(p[4]) + "</p>" +
      '<div class="acoes"><button type="button" id="qz-prox" class="botao primario">Próxima →</button>' +
      '<a class="botao" href="' + atual.certo + ".html#" + p[2] + '" target="_blank" rel="noopener">Ver no guia ↗</a></div>';
    $("qz-prox").addEventListener("click", nova);
    $("qz-prox").focus({ preventScroll: true });
  }

  function salvarOpcoes() {
    try { localStorage.setItem("quiz-opcoes", JSON.stringify({ cont: selCont.value, dif: selDif.value })); } catch (e) {}
  }
  selCont.addEventListener("change", function () { salvarOpcoes(); nova(); });
  selDif.addEventListener("change", function () { salvarOpcoes(); nova(); });

  document.addEventListener("keydown", function (e) {
    if (e.target && /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName)) return;
    if (!respondido && /^[1-4]$/.test(e.key) && atual) {
      var s = atual.opcoes[parseInt(e.key, 10) - 1]; if (s) responder(s);
    } else if (respondido && (e.key === "Enter" || e.key === " ") &&
               !/^(A|BUTTON)$/.test(document.activeElement.tagName)) {
      e.preventDefault(); nova();
    }
  });

  placar();
  nova();
})();
