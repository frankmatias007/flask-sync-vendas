import psycopg2
import unicodedata


def get_conexao():
    return psycopg2.connect(
        dbname="loja_acessorios",
        user="postgres",
        password="",  # Substitua pela senha real
        host="localhost",
        port=5432
    )


def testar_vendas():
    conn = get_conexao()
    cur = conn.cursor()
    cur.execute("SELECT id, data_hora, total, forma_pagamento, usuario_id FROM vendas")
    vendas = cur.fetchall()

    colunas = ['id', 'data_hora', 'total', 'forma_pagamento', 'usuario_id']

    for venda in vendas:
        for i, campo in enumerate(venda):
            try:
                valor = campo
                if isinstance(valor, bytes):
                    valor.decode('utf-8')
                elif isinstance(valor, str):
                    unicodedata.normalize('NFKD', valor)
            except Exception as e:
                print(f"❌ Venda ID {venda[0]} → Campo '{colunas[i]}' corrompido: {e}")
                break  # só exibe uma vez por venda
    cur.close()
    conn.close()


if __name__ == "__main__":
    testar_vendas()
