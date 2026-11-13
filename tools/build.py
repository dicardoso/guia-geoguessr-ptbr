"""Gera o site estático em docs/ a partir das traduções em conteudo/pt/.

Uso: python -I tools/build.py conteudo/pt docs

- Cada conteudo/pt/<pagina>.html vira docs/<pagina>.html: imagens + textos agrupados em
  cards de pista, sumário lateral, links automáticos entre países, navegação
  anterior/próximo e rodapé de licença.
- docs/index.html é gerado com a lista de países por continente e uma busca.
- tools/assets/ (CSS e JS) é copiado para docs/.
- Páginas ainda não traduzidas são ignoradas (aparecem sem link no índice).
"""
import html
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from categorias import CATEGORIAS, classificar  # noqa: E402
from paises import CONTINENTES, EXCECOES, GERAIS, NAO_PUBLICAR, VARIANTES  # noqa: E402

SITE = "Guia de GeoGuessr em Português"
SITE_CURTO = "Guia GeoGuessr PT"
ORIGINAL = "https://www.plonkit.net"
LICENCA = "https://creativecommons.org/licenses/by-nc-sa/4.0/deed.pt-br"
ASSETS = Path(__file__).parent / "assets"
# Link para reportar erros de tradução (ex.: https://github.com/<usuario>/<repo>/issues). Vazio = não mostra.
LINK_ERROS = "https://github.com/dicardoso/guia-geoguessr-ptbr/issues"

# Linhas finais de cada página original (formulário de feedback do Plonk It e aviso de licença).
# São removidas: a licença já está no rodapé e erros de tradução não devem ir para o Plonk It.
RE_BOILERPLATE = re.compile(r"plonkit\.net/feedback|^<p>Todo o conteúdo publicado no Plonk It")

NOME = {s: n for p in CONTINENTES.values() for s, n in p.items()}
CONTINENTE_DE = {s: c for c, p in CONTINENTES.items() for s in p}


# ---------------------------------------------------------------- utilidades
def sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


def slugify(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", sem_acento(html.unescape(s)))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60] or "secao"


def ordenados(paises: dict) -> list:
    return sorted(paises.items(), key=lambda kv: sem_acento(kv[1]))


# ------------------------------------------------- links automáticos de países
_ALVOS = {**{n: s for s, n in NOME.items()}, **VARIANTES}
_RE_PAIS = re.compile(
    r"(?<![\wÀ-ÿ-])(" + "|".join(re.escape(n) for n in sorted(_ALVOS, key=len, reverse=True)) + r")(?![\wÀ-ÿ-])"
)


def linkar_paises(texto: str, pagina_atual: str, prontas: set) -> str:
    """Transforma a 1ª menção de cada país (com página) em link. Não linka a própria página."""
    vistos = set()

    def troca(m):
        nome = m.group(1)
        slug = _ALVOS[nome]
        if slug == pagina_atual or slug not in prontas or slug in vistos:
            return nome
        antes, depois = EXCECOES.get(nome, ((), ()))
        if any(texto[: m.start()].endswith(a) for a in antes) or any(texto[m.end():].startswith(d) for d in depois):
            return nome
        vistos.add(slug)
        return f'<a class="pais" href="{slug}.html">{nome}</a>'

    return _RE_PAIS.sub(troca, texto)


# ------------------------------------------------------------ partes da página
def cabecalho(ativa: str | None) -> str:
    itens = [("index", "Países"), ("busca", "Buscar pistas"), ("quiz", "Quiz")] + list(GERAIS.items())
    links = "".join(
        f'<a href="{p}.html"{" aria-current=page" if p == ativa else ""}>{n}</a>' for p, n in itens
    )
    return (
        '<header class="topo"><div class="interno">'
        f'<a class="marca" href="index.html"><span class="longo">{SITE}</span><span class="curto">{SITE_CURTO}</span></a>'
        f'<nav aria-label="Principal">{links}</nav>'
        '<button id="tema-btn" class="botao-icone" type="button" aria-label="Trocar tema">◐</button>'
        "</div></header>"
    )


def rodape(pagina: str | None) -> str:
    orig = f"{ORIGINAL}/{pagina}" if pagina else ORIGINAL
    return (
        '<footer class="rodape"><div class="interno">'
        f'<p>Tradução não oficial do <a href="{ORIGINAL}">Plonk It Guide</a>, '
        f'conteúdo original © 2021-2026 Plonk It, licenciado sob '
        f'<a href="{LICENCA}">CC BY-NC-SA 4.0</a>. '
        f'<strong>Alterações:</strong> texto traduzido para o português e reorganizado em um novo layout; '
        f'as imagens são carregadas do site original. Esta tradução é distribuída sob a mesma licença. '
        f'<a href="{orig}">Ver esta página no original (inglês)</a>.</p>'
        '<p>Este site não é afiliado ao Plonk It nem endossado por ele. '
        'Erros de tradução são responsabilidade deste projeto, não da equipe do Plonk It.'
        + (f' <a href="{LINK_ERROS}">Reportar um erro de tradução</a>.' if LINK_ERROS else "")
        + "</p></div></footer>"
    )


ZOOM = (
    '<dialog id="zoom" class="zoom" aria-label="Imagem ampliada"><img alt="">'
    '<div class="barra"><button class="ant" type="button" aria-label="Imagem anterior">←</button>'
    '<span class="pos"></span>'
    '<button class="prox" type="button" aria-label="Próxima imagem">→</button>'
    '<a class="orig" target="_blank" rel="noopener">Abrir</a>'
    '<button class="fechar" type="button">Fechar ✕</button></div></dialog>'
)

TEMA_INICIAL = (
    "<script>try{var t=localStorage.getItem('tema');"
    "if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t)}catch(e){}</script>"
)


def documento(titulo: str, ativa: str | None, conteudo: str, pagina: str | None,
              lateral: str = "", descricao: str = "", scripts: tuple = ()) -> str:
    desc = f'<meta name="description" content="{html.escape(descricao)}">\n' if descricao else ""
    flutuantes = '<div class="flutuantes">'
    if lateral:
        flutuantes += '<button id="secoes-btn" type="button" aria-expanded="false">☰ Seções</button>'
    flutuantes += '<button id="topo-btn" type="button" aria-label="Voltar ao topo">↑ Topo</button></div>'
    classe = "layout com-lateral" if lateral else "layout"
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo} · {SITE}</title>
{desc}{TEMA_INICIAL}
<link rel="stylesheet" href="estilo.css">
</head>
<body>
{cabecalho(ativa)}
<div class="{classe}">
{lateral}<main>
{conteudo}
</main>
</div>
{rodape(pagina)}
{flutuantes}
{ZOOM}
<script src="site.js" defer></script>
{"".join(f'<script src="{js}" defer></script>' for js in scripts)}
</body>
</html>
"""


# ------------------------------------------------------ conversão do conteúdo
RE_IMG = re.compile(r'^<img src="([^"]*)"(?: alt="([^"]*)")?(?: title="([^"]*)")?>$')
RE_LARGURA = re.compile(r"/images/resize/(\d+)/")


def largura(src: str) -> int:
    m = RE_LARGURA.search(src)
    return int(m.group(1)) if m else 0


def versao_grande(src: str) -> str:
    w = largura(src)
    return RE_LARGURA.sub("/images/resize/1200/", src, count=1) if 0 < w < 1200 else src


def figura(src: str, alt: str, cap: str, extra: str = "") -> str:
    grande = versao_grande(src)
    attr_grande = f' data-grande="{grande}"' if grande != src else ""
    fig = (f'<figure{extra}><a href="{grande}"><img src="{src}" alt="{alt}" loading="lazy" '
           f'decoding="async"{attr_grande}></a>')
    if cap:
        fig += f"<figcaption>{cap}</figcaption>"
    return fig + "</figure>"


def texto(linha: str, pagina: str, prontas: set) -> str:
    """Aplica realce de OBS. e links de países a uma linha <p>/<li>."""
    m = re.match(r"^<(p|li)>(.*)</\1>$", linha)
    if not m:
        return linha
    tag, t = m.groups()
    t = linkar_paises(t, pagina, prontas)
    obs = re.match(r"^(OBS\.?:|Obs\.?:)\s*", t)
    if tag == "p" and obs:
        return f'<p class="obs"><strong>OBS.:</strong> {t[obs.end():]}</p>'
    return f"<{tag}>{t}</{tag}>"


def converter(fragmento: str, pagina: str, prontas: set, fragmento_en: str = ""):
    """Agrupa o fragmento traduzido em blocos. Retorna (titulo, html, secoes, pistas).

    pistas: registros para a busca/quiz — (id, secao, src_imagem, texto_puro, eh_card_lateral).
    """
    titulo, blocos, secoes, usados, pistas = None, [], [], set(), []
    grupo = None  # {"img": (...), "textos": [...], "puros": [...]}
    prosa: list[str] = []
    prosa_pura: list[str] = []
    viu_secao = False

    def registrar(src, puros, lado):
        ident = f"p{len(pistas) + 1}"
        pistas.append((ident, len(secoes) - 1, src, " ".join(p for p, _ in puros), lado,
                       " ".join(e for _, e in puros)))
        return ident

    def fechar_grupo():
        nonlocal grupo
        if grupo is None:
            return
        src, alt, cap = grupo["img"]
        textos = "\n".join(grupo["textos"])
        w = largura(src)
        if not viu_secao and w >= 1900 and not textos:
            blocos.append(figura(src, alt, cap, ' class="capa"'))
        elif not textos:
            blocos.append(figura(src, alt, cap, ' class="solta"'))
        else:
            lado = (0 < w < 900) or not w
            ident = registrar(src, grupo["puros"], lado)
            blocos.append(f'<div class="pista{" lado" if lado else ""}" id="{ident}">{figura(src, alt, cap)}'
                          f'<div class="texto">\n{textos}\n</div></div>')
        grupo = None

    def fechar_prosa():
        if prosa:
            ident = registrar("", prosa_pura, False)
            blocos.append(f'<div class="prosa" id="{ident}">\n' + "\n".join(prosa) + "\n</div>")
            prosa.clear()
            prosa_pura.clear()

    linhas_en = fragmento_en.splitlines()
    for n_linha, linha in enumerate(fragmento.splitlines()):
        linha_en = linhas_en[n_linha] if n_linha < len(linhas_en) else ""
        linha = linha.strip()
        if not linha:
            continue
        if RE_BOILERPLATE.search(linha):
            continue
        if linha.startswith("<h1>"):
            titulo = re.sub(r"</?h1>", "", linha)
            continue
        if linha.startswith("<h3>"):
            fechar_grupo(); fechar_prosa()
            viu_secao = True
            t = linha[4:-5]
            ident = slugify(t)
            while ident in usados:
                ident += "-2"
            usados.add(ident)
            secoes.append([ident, t, 0])
            blocos.append(f'<h3 id="{ident}">{t}</h3>')
            continue
        m = RE_IMG.match(linha)
        if m:
            fechar_grupo(); fechar_prosa()
            grupo = {"img": (m.group(1), m.group(2) or "", m.group(3) or ""), "textos": [], "puros": []}
            if secoes:
                secoes[-1][2] += 1
            continue
        puro = html.unescape(re.sub(r"<[^>]+>", "", linha)).strip()
        linha = texto(linha, pagina, prontas)
        (grupo["textos"] if grupo is not None else prosa).append(linha)
        puro_en = html.unescape(re.sub(r"<[^>]+>", "", linha_en)).strip()
        (grupo["puros"] if grupo is not None else prosa_pura).append((puro, puro_en))
    fechar_grupo(); fechar_prosa()
    return titulo, "\n".join(blocos), secoes, pistas


def sumario_lateral(secoes) -> str:
    if len(secoes) < 2:
        return ""
    itens = "".join(
        f'<li><a href="#{i}">{t}'
        + (f' <span class="contagem">· {n}</span>' if n else "")
        + "</a></li>"
        for i, t, n in secoes
    )
    return f'<aside class="lateral" aria-label="Seções da página"><nav><h2>Nesta página</h2><ol>{itens}</ol></nav></aside>\n'


def vizinhos(pagina: str, prontas: set) -> str:
    cont = CONTINENTE_DE.get(pagina)
    if not cont:
        return ""
    lista = [s for s, _ in ordenados(CONTINENTES[cont]) if s in prontas]
    i = lista.index(pagina)
    partes = []
    if i > 0:
        partes.append(f'<a class="ant" href="{lista[i-1]}.html"><small>← Anterior</small>{NOME[lista[i-1]]}</a>')
    if i < len(lista) - 1:
        partes.append(f'<a class="prox" href="{lista[i+1]}.html"><small>Próximo →</small>{NOME[lista[i+1]]}</a>')
    return f'<nav class="vizinhos" aria-label="Outros países de {cont}">{"".join(partes)}</nav>' if partes else ""


def pagina_conteudo(pagina: str, fragmento: str, prontas: set, indice: dict, fragmento_en: str = "") -> str:
    titulo, corpo, secoes, pistas = converter(fragmento, pagina, prontas, fragmento_en)
    titulo = titulo or NOME.get(pagina) or GERAIS.get(pagina) or pagina
    cont = CONTINENTE_DE.get(pagina)
    trilha = (f'<div class="trilha"><a href="index.html">Países</a> › {cont}</div>' if cont
              else '<div class="trilha"><a href="index.html">Início</a> › Guias gerais</div>')
    acoes = (f'<div class="acoes"><a class="botao" href="{ORIGINAL}/{pagina}" target="_blank" rel="noopener">'
             f'Ver original em inglês ↗</a></div>')
    conteudo = f"{trilha}\n<h1>{titulo}</h1>\n{acoes}\n{corpo}\n{vizinhos(pagina, prontas)}"
    indice[pagina] = (titulo, [t for _, t, _ in secoes], pistas)
    desc = f"Dicas de GeoGuessr para identificar {titulo}: tradução do Plonk It Guide." if cont else ""
    return documento(titulo, pagina if pagina in GERAIS else None, conteudo, pagina,
                     sumario_lateral(secoes), desc)


def gerar_index(prontas: set) -> str:
    partes = [
        f"<h1>{SITE}</h1>",
        '<div class="intro">',
        "<p>Tradução não oficial do <a href=\"https://www.plonkit.net/guide\">Plonk It Guide</a>, "
        "uma coleção de dicas para identificar países e regiões no GeoGuessr, feita pela "
        "comunidade Plonk It. Este projeto não é afiliado ao Plonk It nem endossado por ele.</p>",
        "<p>Cada página de país tem três partes: <strong>identificando o país</strong>, "
        "<strong>pistas regionais</strong> (estados, províncias, regiões) e "
        "<strong>destaque</strong> (pistas bem específicas). Clique nas imagens para ampliar.</p>",
        "</div>",
        "<h3>Explorar</h3>",
        '<ul class="cartoes destaque">'
        '<li><a href="busca.html"><span class="icone">⌕</span>Buscar nas pistas'
        '<small>Ex.: “poste escada”, “placa amarela”, “bollard vermelho”</small></a></li>'
        '<li><a href="quiz.html"><span class="icone">?</span>Quiz'
        '<small>Veja uma pista e adivinhe o país</small></a></li>'
        "</ul>",
        "<h3>Guias gerais</h3>",
        '<ul class="cartoes">'
        + "".join(f'<li><a href="{p}.html">{n}</a></li>' for p, n in GERAIS.items() if p in prontas)
        + "</ul>",
        '<h3 id="paises">Países e territórios</h3>',
        '<input id="busca" class="busca" type="search" placeholder="Buscar país…" aria-label="Buscar país" autocomplete="off">',
        '<p id="vazio" class="vazio">Nenhum país encontrado.</p>',
    ]
    for cont, paises in CONTINENTES.items():
        itens = []
        for slug, nome in ordenados(paises):
            dn = html.escape(sem_acento(nome))
            if slug in prontas:
                itens.append(f'<li data-nome="{dn}"><a href="{slug}.html">{nome}</a></li>')
            else:
                itens.append(f'<li data-nome="{dn}" class="pendente" title="tradução pendente">{nome}</li>')
        partes.append(f'<section class="continente"><h2>{cont}</h2><ul class="grade">{"".join(itens)}</ul></section>')
    return documento("Início", "index", "\n".join(partes), None,
                     descricao="Tradução em português do Plonk It Guide: dicas de GeoGuessr para cada país.")


# --------------------------------------------------------- busca e quiz (fase 2)
def gerar_indice_json(indice: dict) -> str:
    """Índice compacto de todas as pistas, usado por busca.js e quiz.js.

    pistas: [pagina, secao, id, imagem, texto, categorias(bitmask), quiz(0/1)]
    """
    paginas, pistas = {}, []
    for pagina, (titulo, secoes, regs) in sorted(indice.items()):
        cont = CONTINENTE_DE.get(pagina, "")
        nomes = [n for n, s in _ALVOS.items() if s == pagina]
        paginas[pagina] = [titulo, cont, secoes, nomes]
        for ident, sec, src, txt, lado, txt_en in regs:
            if not txt:
                continue
            quiz = int(bool(cont) and bool(src) and lado)
            pistas.append([pagina, sec, ident, src, txt, classificar(txt_en), quiz])
    dados = {
        "categorias": [[cid, rot] for cid, rot, _ in CATEGORIAS],
        "continentes": list(CONTINENTES),
        "paginas": paginas,
        "pistas": pistas,
    }
    return json.dumps(dados, ensure_ascii=False, separators=(",", ":"))


def gerar_busca() -> str:
    conteudo = """<div class="trilha"><a href="index.html">Início</a> › Explorar</div>
<h1>Buscar nas pistas</h1>
<p class="intro">Procure em todas as pistas do guia de uma vez: “poste escada”, “placa amarela”,
“terra vermelha”, “cirílico”… Combine com os filtros para ver, por exemplo, todos os bollards da Europa.</p>
<div class="busca-form">
  <input id="q" class="busca" type="search" placeholder="O que você está vendo?" aria-label="Termos da busca" autocomplete="off" autofocus>
  <select id="cont" class="seletor" aria-label="Continente"><option value="">Todos os continentes</option></select>
</div>
<div id="cats" class="chips" role="group" aria-label="Categorias"></div>
<p class="aviso-filtro">As categorias são automáticas (por palavras-chave) e podem falhar em alguns casos.</p>
<p id="status" class="status" aria-live="polite">Carregando índice…</p>
<ol id="resultados" class="resultados"></ol>
<button id="mais" class="botao mais" type="button" hidden>Mostrar mais resultados</button>"""
    return documento("Buscar nas pistas", "busca", conteudo, None,
                     descricao="Busque em todas as pistas do guia de GeoGuessr em português.",
                     scripts=("pistas.js", "busca.js"))


def gerar_quiz() -> str:
    conteudo = """<div class="trilha"><a href="index.html">Início</a> › Explorar</div>
<h1>Quiz: de onde é essa pista?</h1>
<div class="quiz-opcoes">
  <label>Continente <select id="qz-cont" class="seletor"><option value="">Todos</option></select></label>
  <label>Dificuldade <select id="qz-dif" class="seletor">
    <option value="facil">Fácil — alternativas de qualquer lugar</option>
    <option value="dificil" selected>Difícil — alternativas do mesmo continente</option>
  </select></label>
</div>
<div class="placar" aria-live="polite">
  <span>Acertos <strong id="qz-acertos">0</strong>/<strong id="qz-total">0</strong></span>
  <span>Sequência <strong id="qz-seq">0</strong></span>
  <span>Recorde <strong id="qz-rec">0</strong></span>
</div>
<div id="qz-carta" class="quiz-carta">
  <p class="status">Carregando pistas…</p>
</div>
<p class="dica-teclado">Atalhos: teclas <kbd>1</kbd>–<kbd>4</kbd> para responder, <kbd>Enter</kbd> para a próxima.</p>"""
    return documento("Quiz", "quiz", conteudo, None,
                     descricao="Quiz de GeoGuessr: veja uma pista e adivinhe o país.",
                     scripts=("pistas.js", "quiz.js"))


# ---------------------------------------------------------------------- main
def main(origem: str, destino: str):
    sys.stdout.reconfigure(encoding="utf-8")
    origem, destino = Path(origem), Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    conhecidas = set(GERAIS) | NAO_PUBLICAR | set(NOME)
    arquivos = {a.stem: a for a in sorted(origem.glob("*.html"))}
    for nome in arquivos:
        if nome not in conhecidas:
            print(f"aviso: {nome} não está em tools/paises.py")
    prontas = {n for n in arquivos if n not in NAO_PUBLICAR}
    indice: dict = {}
    dir_en = origem.parent / "en"  # texto original alinhado, usado para classificar as pistas
    for nome in sorted(prontas):
        en = dir_en / f"{nome}.html"
        saida = pagina_conteudo(nome, arquivos[nome].read_text(encoding="utf-8"), prontas, indice,
                                en.read_text(encoding="utf-8") if en.exists() else "")
        (destino / f"{nome}.html").write_text(saida, encoding="utf-8", newline="\n")
    (destino / "index.html").write_text(gerar_index(prontas), encoding="utf-8", newline="\n")
    (destino / "busca.html").write_text(gerar_busca(), encoding="utf-8", newline="\n")
    (destino / "quiz.html").write_text(gerar_quiz(), encoding="utf-8", newline="\n")
    # Como script (e não .json) para funcionar também abrindo os arquivos direto do disco (file://).
    (destino / "pistas.js").write_text("window.PISTAS=" + gerar_indice_json(indice) + ";\n",
                                       encoding="utf-8", newline="\n")
    for asset in ASSETS.iterdir():
        shutil.copyfile(asset, destino / asset.name)
    (destino / ".nojekyll").write_text("", encoding="utf-8")
    faltando = sorted(conhecidas - prontas - NAO_PUBLICAR)
    print(f"{len(prontas)} páginas geradas em {destino}")
    if faltando:
        print(f"{len(faltando)} ainda sem tradução: {' '.join(faltando)}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
