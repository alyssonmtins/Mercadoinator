"""
Coletor de preços - lojas VipCommerce (Delta Super e Super São Roque)
----------------------------------------------------------------------
Este script é "burro" de propósito: ele só COLETA e GUARDA. Para cada
item e cada loja, abre a busca, extrai TODOS os produtos que aparecerem
e grava no banco SQLite, sem validar nada.

Decidir quais candidatos servem (nota, palavras obrigatórias, preço por
kg/L) é trabalho de outra etapa, que lê o banco depois.
"""

import time
from contextlib import closing
from datetime import datetime
from urllib.parse import quote

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

import db

# Serve para lojas usando o vipcommerce
LOJAS = [
    {"nome": "delta", "base_url": "https://www.loja.deltasuper.com.br"},
    {"nome": "sao_roque", "base_url": "https://www.ecommerce.supersaoroque.com.br"},
]

ITENS = [
    "arroz 5kg",
    "feijao 1kg",
    "acucar 5kg",
    "leite integral 1l",
    "oleo de soja 900ml",
    "sabao em po 1kg",
    "amaciante de roupas 2l",
]


def renderizar_pagina(url: str, navegador) -> str:
    pagina = navegador.new_page()
    try:
        pagina.goto(url, timeout=30000)
        pagina.wait_for_timeout(4000)
        return pagina.content()
    finally:
        pagina.close()


def parsear_preco(texto: str) -> float | None:
    if not texto:
        return None
    precoFormatado = texto.replace("R$", "").replace("\xa0", "").strip()
    precoFormatado = precoFormatado.replace(".", "").replace(",", ".")
    try:
        return float(precoFormatado)
    except ValueError:
        return None


def extrair_produtos(html: str, base_url: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    produtos = []

    for card in soup.find_all("vip-card-produto"):
        nomeDoProduto = card.find(attrs={"data-cy": "produto-descricao"})
        precoAtual = card.find(attrs={"data-cy": "preco"})
        precoAnterior = card.find(attrs={"data-cy": "preco-antigo"})
        linkDoProduto = card.find("a", href=True)

        if not nomeDoProduto or not precoAtual:
            continue

        produtos.append({
            "nome": nomeDoProduto.get_text(strip=True),
            "preco": parsear_preco(precoAtual.get_text(strip=True)),
            "preco_antigo": (
                parsear_preco(precoAnterior.get_text(strip=True))
                if precoAnterior else None
            ),
            "em_promocao": precoAnterior is not None,
            "link": base_url + linkDoProduto["href"] if linkDoProduto else None,
        })

    return produtos


def main():
    coletado_em = datetime.now().isoformat(timespec="seconds")

    with closing(db.conectar()) as conn:
        db.criar_tabelas(conn)

        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True)

            for loja in LOJAS:
                print(f"\n=== {loja['nome']} ===")

                for item in ITENS:
                    url = f"{loja['base_url']}/busca?termo={quote(item)}"

                    try:
                        html = renderizar_pagina(url, navegador)
                    except Exception as erro:
                        print(f"  [ERRO] '{item}': {erro}")
                        continue

                    produtos = extrair_produtos(html, loja["base_url"])
                    db.salvar_busca(conn, coletado_em, loja["nome"], item, produtos)
                    print(f"  {item}: {len(produtos)} candidato(s) gravado(s)")

                    time.sleep(1.5)

            navegador.close()

    print(f"\nConcluído. Dados gravados em {db.CAMINHO_DB}")


if __name__ == "__main__":
    main()
