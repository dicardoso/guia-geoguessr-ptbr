"""Limpa as páginas baixadas (original/) e gera fragmentos simples em conteudo/en/.

Uso: python -I tools/preparar.py original conteudo/en

O que a limpeza faz:
- remove <head>, estilos inline e o logo repetido do Plonk It;
- converte cada bloco de imagem em uma única linha <img src="..." alt="...">;
- remove os <p> duplicados que o scraper gerou logo após cada <li>;
- agrupa <li> consecutivos dentro de <ul>;
- remove o rodapé de copyright (o build adiciona um rodapé próprio com a licença).
"""
import re
import sys
from pathlib import Path

# Páginas que fazem parte do guia. As demais (ranking, doações, regras de
# speedrun etc.) são específicas da comunidade/Discord e quase vazias no scrape.
PAGINAS_EXTRAS = {"guide", "beginners-guide", "maps", "tools", "spillover-countries"}
PAGINAS_IGNORADAS = {
    "changelog", "donate", "feedback", "guide-editor", "highscores", "index",
    "leaderboard", "map", "regional", "rules", "rules-assisted", "rules-solo",
    "speedruns", "submit", "top", "veteran",
}

LOGO = "plonk-it-small.webp"
RE_EL = re.compile(r"^\s*<(h1|h2|h3|p|li)>(.*)</\1>\s*$")
RE_IMG = re.compile(r'<img src="([^"]*)" alt="([^"]*)"')
RE_CAP = re.compile(r"<small[^>]*>(.*?)</small>")


def esc_attr(s: str) -> str:
    return s.replace("&", "&amp;").replace('"', "&quot;")


def ler_elementos(texto: str):
    corpo = texto.split("<body>", 1)[1].split("</body>", 1)[0]
    els = []
    for linha in corpo.splitlines():
        if not linha.strip():
            continue
        m = RE_EL.match(linha)
        if m:
            tag, conteudo = m.groups()
            if tag == "p" and conteudo.strip().startswith("©"):
                continue
            els.append([tag, conteudo.strip()])
            continue
        mi = RE_IMG.search(linha)
        if mi:
            src, alt = mi.groups()
            if LOGO in src:
                continue
            mc = RE_CAP.search(linha)
            els.append(["img", (src, alt, mc.group(1) if mc else "")])
            continue
        raise ValueError(f"linha não reconhecida: {linha[:120]}")
    return els


def limpar(els):
    # <li>pai com filhos concatenados</li><p>texto do pai</p> -> <li>texto do pai</li>
    for i in range(len(els) - 1):
        a, b = els[i], els[i + 1]
        if a[0] == "li" and b[0] == "p" and a[1] != b[1] and a[1].startswith(b[1]):
            a[1] = b[1]
    # remove <p> que repete o <li> anterior
    saida = []
    for el in els:
        if el[0] == "p" and saida and saida[-1][0] == "li" and saida[-1][1] == el[1]:
            continue
        saida.append(el)
    return saida


def renderizar(els) -> str:
    linhas, em_lista = [], False
    for tag, val in els:
        if tag == "li" and not em_lista:
            linhas.append("<ul>")
            em_lista = True
        elif tag != "li" and em_lista:
            linhas.append("</ul>")
            em_lista = False
        if tag == "img":
            src, alt, cap = val
            a = f' alt="{esc_attr(alt)}"' if alt else ""
            c = f' title="{esc_attr(cap)}"' if cap and cap != alt else ""
            linhas.append(f'<img src="{src}"{a}{c}>')
        else:
            linhas.append(f"<{tag}>{val}</{tag}>")
    if em_lista:
        linhas.append("</ul>")
    return "\n".join(linhas) + "\n"


def main(origem: str, destino: str):
    sys.stdout.reconfigure(encoding="utf-8")
    origem, destino = Path(origem), Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    n = 0
    for arq in sorted(origem.glob("*.html")):
        if arq.stem in PAGINAS_IGNORADAS:
            continue
        els = limpar(ler_elementos(arq.read_text(encoding="utf-8")))
        (destino / arq.name).write_text(renderizar(els), encoding="utf-8", newline="\n")
        n += 1
    print(f"{n} páginas geradas em {destino}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
