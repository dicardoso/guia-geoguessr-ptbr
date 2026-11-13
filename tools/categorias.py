"""Categorias das pistas usadas nos filtros da busca.

A classificação usa o texto ORIGINAL em inglês (conteudo/en), que é alinhado linha a linha
com a tradução e é menos ambíguo (em português "placa" serve para placa de carro e de trânsito).
Cada pista entra em todas as categorias cujas expressões aparecem no texto (minúsculo).
É aproximada: ajuste as expressões para melhorar os filtros.
"""
import re

CATEGORIAS = [
    # (id, rótulo, expressão em inglês)
    ("placas-carro", "Placas de carro", r"licen[cs]e plates?|number plates?|\bplates?\b"),
    ("sinalizacao", "Sinalização de trânsito",
     r"\bsigns?\b|\bsignage\b|chevrons?|traffic lights?|\bsignpost"),
    ("postes", "Postes", r"\bpoles?\b|\bpylons?\b"),
    ("bollards", "Bollards", r"\bbollards?\b"),
    ("idioma", "Idioma e escrita",
     r"\blanguages?\b|alphabet|\bscripts?\b|\bletters?\b|cyrillic|diacritic|\bwords?\b|spelling|written"),
    ("carro-camera", "Carro e câmera do Google",
     r"\bgen(eration)? ?[1-4]\b|google car|follow car|\bblur\b|snorkel|antenna|roof rack|\brack\b|smallcam|"
     r"shitcam|low-?cam|badcam|trekker|\bcamera\b|car meta|\bcoverage\b"),
    ("estradas", "Estradas e faixas",
     r"road lines?|centre lines?|center lines?|edge lines?|\bdashed\b|guard ?rails?|\bkerbs?\b|\bcurbs?\b|"
     r"asphalt|dirt roads?|unpaved|pavement|road markers?|kilometre markers?|highway|motorway"),
    ("natureza", "Vegetação e paisagem",
     r"vegetation|\btrees?\b|palms?\b|forest|\bsoil\b|mountain|desert|climate|landscape|eucalyptus|"
     r"\bpines?\b|savann?a|crops?\b|fields?\b|\bhills?\b|terrain|\bsnow\b|grass"),
    ("construcoes", "Casas e construções",
     r"\bhouses?\b|\broofs?\b|architecture|buildings?\b|church|mosque|temple|\bwalls?\b|fences?\b"),
]

_COMPILADAS = [(cid, rot, re.compile(exp)) for cid, rot, exp in CATEGORIAS]
_NAO_PLACA = re.compile(r"tectonic plate|plateau")


def classificar(texto_en: str) -> int:
    """Retorna um bitmask com as categorias da pista (bit i = CATEGORIAS[i])."""
    t = texto_en.lower()
    mascara = 0
    for i, (cid, _, exp) in enumerate(_COMPILADAS):
        if exp.search(t):
            if cid == "placas-carro" and _NAO_PLACA.search(t) and not re.search(r"licen[cs]e plate", t):
                continue
            mascara |= 1 << i
    return mascara
