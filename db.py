import sqlite3
from pathlib import Path

CAMINHO_DB = Path(__file__).parent / "precos.db"
SCHEMA = """
CREATE TABLE IF NOT EXISTS buscas (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    coletado_em    TEXT    NOT NULL,
    loja           TEXT    NOT NULL,
    termo_busca    TEXT    NOT NULL,
    qtd_resultados INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS coletas (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    busca_id     INTEGER NOT NULL REFERENCES buscas(id),
    posicao      INTEGER NOT NULL,
    nome         TEXT    NOT NULL,
    preco        REAL,
    preco_antigo REAL,
    em_promocao  INTEGER NOT NULL DEFAULT 0,
    link         TEXT
);

CREATE INDEX IF NOT EXISTS idx_buscas_loja_termo_data
    ON buscas (loja, termo_busca, coletado_em);
CREATE INDEX IF NOT EXISTS idx_coletas_busca
    ON coletas (busca_id);
"""

def conectar() -> sqlite3.Connection:
    conn = sqlite3.connect(CAMINHO_DB)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabelas(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()

def salvar_busca(
    conn: sqlite3.Connection,
    coletado_em: str,
    loja: str,
    termo_busca: str,
    produtos: list[dict],
) -> int:
    with conn:
        cursor = conn.execute(
            """INSERT INTO buscas (coletado_em, loja, termo_busca, qtd_resultados)
               VALUES (?, ?, ?, ?)""",
            (coletado_em, loja, termo_busca, len(produtos)),
        )
        busca_id = cursor.lastrowid

        conn.executemany(
            """INSERT INTO coletas
                   (busca_id, posicao, nome, preco, preco_antigo, em_promocao, link)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    busca_id,
                    posicao,
                    p["nome"],
                    p["preco"],
                    p["preco_antigo"],
                    int(p["em_promocao"]),
                    p["link"],
                )
                for posicao, p in enumerate(produtos, start=1)
            ],
        )
    return busca_id
