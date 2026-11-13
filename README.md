# Guia de GeoGuessr em Português

Tradução não oficial para o português do Brasil do [Plonk It Guide](https://www.plonkit.net/guide),
o guia de dicas de GeoGuessr da comunidade Plonk It.
**Este projeto não é afiliado ao Plonk It nem endossado por ele.**

## Licença

- **Conteúdo do guia** (`conteudo/`, `original/`, páginas em `docs/`): o original é
  © 2021-2026 Plonk It, sob [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.pt-br).
  Esta tradução é uma obra derivada distribuída sob a mesma licença: uso **não comercial**,
  com **atribuição** ao Plonk It e **compartilhamento pela mesma licença**.
  Alterações: tradução para o português, limpeza de defeitos de extração e novo layout.
  As imagens não são redistribuídas: são carregadas diretamente de plonkit.net.
- **Código** (`tools/`, `docs/estilo.css`): licença MIT.

Detalhes no arquivo [LICENSE](LICENSE).

## Estrutura

```
original/        páginas como foram baixadas (não editar)
conteudo/en/     texto em inglês limpo, gerado a partir de original/
conteudo/pt/     TRADUÇÃO — é aqui que se corrige e melhora o texto
tools/           scripts e glossário
  build.py         gera o site (layout, cards de pista, links entre países)
  paises.py        nomes dos países, continentes e variantes usadas nos links
  categorias.py    categorias dos filtros da busca (classificadas pelo texto em inglês)
  assets/          estilo.css, site.js, busca.js e quiz.js (copiados para docs/ no build)
docs/            site pronto, gerado pelo build (publicado no GitHub Pages)
```

O build também gera `docs/busca.html` (busca em todas as pistas, com filtros por categoria e
continente), `docs/quiz.html` (adivinhe o país a partir de uma pista) e `docs/pistas.js`, o índice
usado pelos dois. Tudo funciona tanto no GitHub Pages quanto abrindo os arquivos direto do disco.

Para mudar o visual, edite `tools/assets/estilo.css` (não o de `docs/`, que é sobrescrito no build).
O link "Reportar um erro de tradução" do rodapé vem de `LINK_ERROS` em `tools/build.py`
(aponta para as issues do repositório).

## Como editar uma tradução

1. Abra `conteudo/pt/<pagina>.html` e corrija o texto.
   Mantenha **uma linha para cada linha** de `conteudo/en/<pagina>.html` (mesma ordem e mesma tag).
2. Confira e gere o site:

   ```
   python -I tools/verificar.py conteudo/en conteudo/pt
   python -I tools/build.py conteudo/pt docs
   ```

3. Abra `docs/index.html` no navegador para ver o resultado.

Os termos padronizados estão em [tools/glossario.md](tools/glossario.md).

## Atualizar a partir de um novo download do site

Coloque os novos arquivos em `original/` e rode:

```
python -I tools/preparar.py original conteudo/en
python -I tools/verificar.py conteudo/en conteudo/pt
```

O verificador aponta as páginas cujo inglês mudou (número de linhas diferente) e que precisam
ser revisadas.

## Publicação (GitHub Pages)

Repositório: <https://github.com/dicardoso/guia-geoguessr-ptbr>
Site: <https://dicardoso.github.io/guia-geoguessr-ptbr/>

O site é servido da pasta `/docs` da branch `main`
(**Settings → Pages → Build and deployment → Source: Deploy from a branch**, branch `main`, pasta `/docs`).

Sempre que alterar `conteudo/pt/`, rode o build e faça commit da pasta `docs/` também:

```
python -I tools/build.py conteudo/pt docs
git add -A
git commit -m "Descreva a alteração"
git push
```
