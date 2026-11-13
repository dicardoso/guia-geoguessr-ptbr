# Glossário e regras de tradução (EN → PT-BR)

Use estas regras em todas as páginas para manter a tradução consistente.

## Formato dos arquivos

- `conteudo/en/X.html` é a fonte; `conteudo/pt/X.html` é a tradução.
- **Uma linha traduzida para cada linha da fonte**, na mesma ordem e com a mesma tag
  (`<h1>`, `<h3>`, `<p>`, `<li>`, `<ul>`, `</ul>`, `<img>`). Não junte nem divida linhas.
- Linhas `<img ...>`: copie o `src` exatamente igual. Traduza apenas `alt`/`title` se existirem.
- Não adicione `<html>`, `<head>`, estilos ou comentários: o `tools/build.py` monta a página.
- Escape `<` e `>` dentro do texto se aparecerem; `&` pode ficar como está.

## Correção de defeitos do scraper

O site foi baixado com as palavras em **negrito/links removidas sem espaço**, ex.:
`Licence plates in Brazil werewhiteuntil 2018` → as palavras grudaram.
Ao traduzir, **separe as palavras corretamente** (“As placas no Brasil eram brancas até 2018”).
`NOTE:Paraguay uses...` também perdeu o espaço.

## Termos

| Inglês | Português |
|---|---|
| Step 1 - Identifying X | Passo 1 - Identificando X |
| Step 2 - Regional and ... clues | Passo 2 - Pistas regionais e de ... |
| Step 3 - Spotlight | Passo 3 - Destaque |
| NOTE: | OBS.: |
| licence plate / license plate | placa (de carro) |
| front plate / rear plate | placa dianteira / placa traseira |
| road sign | placa de trânsito |
| stop sign / speed sign | placa de pare / placa de velocidade |
| chevron | chevron (placa de curva) |
| bollard | bollard (balizador) na primeira ocorrência da página; depois só “bollard” |
| (utility) pole | poste |
| guardrail | guard-rail |
| road lines / centre line / edge line | faixas da pista / faixa central / faixa lateral |
| dashed / solid | tracejada / contínua |
| coverage | cobertura |
| Generation 3 / Gen 3 / Gen 4 | Geração 3 / Gen 3 / Gen 4 |
| Google car / follow car | carro do Google / carro de acompanhamento (follow car) |
| car meta / meta | meta do carro / meta |
| blur, snorkel, smallcam, rifts, trekker, badcam, shitcam | manter em inglês |
| roof rack | bagageiro de teto (roof rack) |
| spillover | spillover |
| pinpointable / pinpoint | pinpointable / pinpoint |
| NM, NMPZ, Moving, Duels, Battle Royale, Country Streak, 5k, 25k | manter |
| map-generator | map-generator |
| photosphere / unofficial coverage | photosphere / cobertura não oficial |
| region / province / state / county / oblast | região / província / estado / condado / óblast |
| tropical / arid / temperate | tropical / árido / temperado |
| hint | dica |

## Nomes

- Países e territórios: nome usual no Brasil (Brazil → Brasil, Paraguay → Paraguai,
  Eswatini → Essuatíni, Czechia → Tchéquia, Faroe Islands → Ilhas Faroé).
- Estados, cidades e regiões: use a forma consagrada em português quando existir
  (California → Califórnia, New York → Nova York, Bavaria → Baviera, Patagonia → Patagônia);
  caso contrário mantenha o original (Mato Grosso, Shkodër, Saskatchewan).
- Palavras citadas no idioma local (ex.: a palavra albanesa para rua, *rruga*) ficam como estão.
- Nomes de mapas do GeoGuessr, ferramentas, scripts e pessoas: não traduzir.

## Estilo

- Português do Brasil, tom direto e didático (como o original).
- Unidades e números como no original (km/h, mph).
