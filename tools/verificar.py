"""Confere se as traduções em conteudo/pt batem linha a linha com conteudo/en.

Uso: python -I tools/verificar.py conteudo/en conteudo/pt [pagina1 pagina2 ...]
Sem nomes de página, verifica todas. Retorna código 1 se houver problemas.
"""
import re
import sys
from pathlib import Path

RE_TAG = re.compile(r"^<(/?[a-z0-9]+)")
RE_SRC = re.compile(r'src="([^"]*)"')
# Palavras que, se aparecerem muitas vezes, indicam trecho não traduzido.
RE_EN = re.compile(r"\b(the|and|with|which|are|is|this|in the|you)\b", re.I)


def checar(en: Path, pt: Path) -> list[str]:
    if not pt.exists():
        return ["arquivo de tradução não existe"]
    le = en.read_text(encoding="utf-8").splitlines()
    lp = pt.read_text(encoding="utf-8").splitlines()
    erros = []
    if len(le) != len(lp):
        erros.append(f"número de linhas diferente: en={len(le)} pt={len(lp)}")
    for i, (a, b) in enumerate(zip(le, lp), 1):
        ta, tb = RE_TAG.match(a), RE_TAG.match(b)
        if not ta or not tb or ta.group(1) != tb.group(1):
            erros.append(f"linha {i}: tag diferente\n    en: {a[:90]}\n    pt: {b[:90]}")
            break  # o resto provavelmente está desalinhado
        if ta.group(1) == "img" and RE_SRC.search(a).group(1) != (RE_SRC.search(b) or [None, None])[1]:
            erros.append(f"linha {i}: src da imagem alterado")
        elif ta.group(1) != "img" and len(RE_EN.findall(b)) >= 4:
            erros.append(f"linha {i}: parece não traduzida: {b[:90]}")
    return erros


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    en_dir, pt_dir = Path(sys.argv[1]), Path(sys.argv[2])
    nomes = sys.argv[3:] or [p.stem for p in sorted(en_dir.glob("*.html"))]
    ruins = 0
    for nome in nomes:
        erros = checar(en_dir / f"{nome}.html", pt_dir / f"{nome}.html")
        if erros:
            ruins += 1
            print(f"✗ {nome}")
            for e in erros[:10]:
                print("   ", e)
    print(f"{len(nomes) - ruins}/{len(nomes)} páginas OK")
    sys.exit(1 if ruins else 0)


if __name__ == "__main__":
    main()
