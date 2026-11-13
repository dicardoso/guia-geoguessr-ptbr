"""Países do guia: nome em português e continente (usado no índice, nos links e na navegação)."""

CONTINENTES = {
    "África": {
        "botswana": "Botsuana", "egypt": "Egito", "eswatini": "Essuatíni", "ghana": "Gana",
        "kenya": "Quênia", "lesotho": "Lesoto", "madagascar": "Madagascar", "mali": "Mali",
        "namibia": "Namíbia", "nigeria": "Nigéria", "reunion": "Reunião", "rwanda": "Ruanda",
        "sao-tome-and-principe": "São Tomé e Príncipe", "senegal": "Senegal",
        "south-africa": "África do Sul", "tanzania": "Tanzânia", "tunisia": "Tunísia",
        "uganda": "Uganda",
    },
    "América do Norte e Caribe": {
        "alaska": "Alasca", "bermuda": "Bermudas", "canada": "Canadá", "costa-rica": "Costa Rica",
        "curacao": "Curaçao", "dominican-republic": "República Dominicana",
        "greenland": "Groenlândia", "guatemala": "Guatemala", "martinique": "Martinica",
        "mexico": "México", "panama": "Panamá", "puerto-rico": "Porto Rico",
        "saint-pierre-and-miquelon": "São Pedro e Miquelão",
        "united-states": "Estados Unidos", "us-virgin-islands": "Ilhas Virgens Americanas",
    },
    "América do Sul": {
        "argentina": "Argentina", "bolivia": "Bolívia", "brazil": "Brasil", "chile": "Chile",
        "colombia": "Colômbia", "ecuador": "Equador", "falkland-islands": "Ilhas Malvinas (Falklands)",
        "peru": "Peru", "uruguay": "Uruguai",
    },
    "Ásia": {
        "bangladesh": "Bangladesh", "bhutan": "Butão",
        "british-indian-ocean-territory": "Território Britânico do Oceano Índico",
        "cambodia": "Camboja", "china": "China", "hong-kong": "Hong Kong", "india": "Índia",
        "indonesia": "Indonésia", "iraq": "Iraque", "israel-west-bank": "Israel e Cisjordânia",
        "japan": "Japão", "jordan": "Jordânia", "kazakhstan": "Cazaquistão",
        "kyrgyzstan": "Quirguistão", "laos": "Laos", "lebanon": "Líbano", "macau": "Macau",
        "malaysia": "Malásia", "mongolia": "Mongólia", "nepal": "Nepal", "oman": "Omã",
        "pakistan": "Paquistão", "philippines": "Filipinas", "qatar": "Catar",
        "singapore": "Singapura", "south-korea": "Coreia do Sul", "sri-lanka": "Sri Lanka",
        "taiwan": "Taiwan", "thailand": "Tailândia", "turkey": "Turquia",
        "united-arab-emirates": "Emirados Árabes Unidos", "vietnam": "Vietnã",
    },
    "Europa": {
        "albania": "Albânia", "andorra": "Andorra", "austria": "Áustria", "azores": "Açores",
        "belarus": "Bielorrússia", "belgium": "Bélgica", "bulgaria": "Bulgária", "croatia": "Croácia",
        "cyprus": "Chipre", "czechia": "Tchéquia", "denmark": "Dinamarca", "estonia": "Estônia",
        "faroe-islands": "Ilhas Faroé", "finland": "Finlândia", "france": "França",
        "germany": "Alemanha", "gibraltar": "Gibraltar", "greece": "Grécia", "hungary": "Hungria",
        "iceland": "Islândia", "ireland": "Irlanda", "isle-of-man": "Ilha de Man",
        "italy": "Itália", "jersey": "Jersey", "latvia": "Letônia",
        "liechtenstein": "Liechtenstein", "lithuania": "Lituânia", "luxembourg": "Luxemburgo",
        "madeira": "Madeira", "malta": "Malta", "monaco": "Mônaco", "montenegro": "Montenegro",
        "netherlands": "Países Baixos", "north-macedonia": "Macedônia do Norte",
        "norway": "Noruega", "poland": "Polônia", "portugal": "Portugal", "romania": "Romênia",
        "russia": "Rússia", "san-marino": "San Marino", "serbia": "Sérvia",
        "slovakia": "Eslováquia", "slovenia": "Eslovênia", "spain": "Espanha",
        "svalbard": "Svalbard", "sweden": "Suécia", "switzerland": "Suíça",
        "ukraine": "Ucrânia", "united-kingdom": "Reino Unido",
    },
    "Oceania": {
        "american-samoa": "Samoa Americana", "australia": "Austrália",
        "christmas-island": "Ilha Christmas", "cocos-islands": "Ilhas Cocos", "guam": "Guam",
        "hawaii": "Havaí", "new-zealand": "Nova Zelândia",
        "northern-mariana-islands": "Ilhas Marianas do Norte",
        "pitcairn-islands": "Ilhas Pitcairn",
        "us-minor-outlying-islands": "Ilhas Menores Distantes dos EUA", "vanuatu": "Vanuatu",
    },
    "Antártida": {
        "antarctica": "Antártida",
        "south-georgia-sandwich-islands": "Geórgia do Sul e Ilhas Sandwich do Sul",
    },
}

GERAIS = {
    "beginners-guide": "Guia para iniciantes",
    "maps": "Diretório de mapas",
    "tools": "Ferramentas",
    "spillover-countries": "Países de spillover",
}
NAO_PUBLICAR = {"guide"}  # a lista de países dessa página veio quebrada no scrape; o index substitui

# Outras formas como os países aparecem no texto traduzido (para os links automáticos).
VARIANTES = {
    "EUA": "united-states",
    "Holanda": "netherlands",
    "República Tcheca": "czechia",
    "Belarus": "belarus",
    "Malvinas": "falkland-islands",
    "Ilhas Malvinas": "falkland-islands",
    "Ilhas Falkland": "falkland-islands",
    "Falklands": "falkland-islands",
    "Eswatini": "eswatini",
    "Réunion": "reunion",
    "Türkiye": "turkey",
    "Israel": "israel-west-bank",
    "Cisjordânia": "israel-west-bank",
    "EAU": "united-arab-emirates",
    "Bermuda": "bermuda",
    "Saint-Pierre e Miquelon": "saint-pierre-and-miquelon",
    "Geórgia do Sul": "south-georgia-sandwich-islands",
    "Marianas do Norte": "northern-mariana-islands",
    "Ilhas Virgens dos EUA": "us-virgin-islands",
    "Ilhas Virgens dos Estados Unidos": "us-virgin-islands",
    "Ilhas Menores Distantes dos Estados Unidos": "us-minor-outlying-islands",
    "Faroé": "faroe-islands",
    "Qatar": "qatar",
}

# Contextos em que o nome NÃO se refere ao país: (texto antes, texto depois).
EXCECOES = {
    "México": (("Novo ",), ()),
    "Jersey": (("Nova ", "New "), ()),
    "Irlanda": ((), (" do Norte",)),
    "Madeira": (("rio ", "rios ", "Rio "), ()),
    "Equador": (("linha do ", "Linha do "), ()),
    "Geórgia do Sul": ((), ()),
}
