"""
Consulta rápida: mostra quantos candidatos cada busca da ÚLTIMA coleta trouxe, e os 3 primeiros de cada uma.
"""

from contextlib import closing

import db

BUSCAS_ULTIMA_COLETA = """
SELECT id, loja, termo_busca, qtd_resultados
FROM buscas
WHERE coletado_em = (SELECT MAX(coletado_em) FROM buscas)
ORDER BY loja, id
"""

PRIMEIROS_CANDIDATOS = """
SELECT posicao, nome, preco, em_promocao
FROM coletas
WHERE busca_id = ?
ORDER BY posicao
LIMIT 3
"""

def main():
    with closing(db.conectar()) as conn:
        for busca in conn.execute(BUSCAS_ULTIMA_COLETA).fetchall():
            print(f"\n[{busca['loja']}] {busca['termo_busca']} "
                  f"-> {busca['qtd_resultados']} candidato(s)")

            for c in conn.execute(PRIMEIROS_CANDIDATOS, (busca["id"],)):
                promo = " (promo)" if c["em_promocao"] else ""
                print(f"   {c['posicao']}. {c['nome']} - R$ {c['preco']:.2f}{promo}")


if __name__ == "__main__":
    main()
