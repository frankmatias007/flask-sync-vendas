import os
from datetime import datetime

import psycopg2
import unicodedata
from flask import Flask, request, jsonify

app = Flask(__name__)


def get_conexao():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432")
    )


@app.route('/')
def index():
    return 'Servidor Flask rodando com sucesso!'


@app.route('/sincronizar-venda', methods=['POST'])
def sincronizar_venda():
    try:
        dados = request.get_json(force=True)
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": f"Erro ao decodificar JSON: {str(e)}"}), 400

    try:
        data_convertida = datetime.strptime(dados['data_hora'], '%Y-%m-%d %H:%M:%S')

        conn = get_conexao()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO vendas (id, data_hora, total, forma_pagamento, usuario_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            dados['id'],
            data_convertida,
            dados['total'],
            dados['forma_pagamento'],
            dados['usuario_id']
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "sucesso", "mensagem": "Venda sincronizada com sucesso"}), 201

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


def limpar_valor(valor):
    try:
        if isinstance(valor, bytes):
            try:
                valor = valor.decode('utf-8')
            except UnicodeDecodeError:
                valor = valor.decode('latin-1')

        if isinstance(valor, str):
            valor = ''.join(
                c for c in unicodedata.normalize('NFKD', valor)
                if not unicodedata.combining(c)
            )

        return valor
    except Exception as e:
        print(f"❌ Erro ao limpar valor: {valor} → {e}")
        return None


@app.route('/vendas', methods=['GET'])
def listar_vendas():
    try:
        conn = get_conexao()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, data_hora, total, forma_pagamento, usuario_id
            FROM vendas ORDER BY data_hora DESC
        """)
        vendas = cur.fetchall()

        colunas = ['id', 'data_hora', 'total', 'forma_pagamento', 'usuario_id']
        vendas_json = []

        for venda in vendas:
            try:
                registro = {}
                for i, campo in enumerate(venda):
                    valor_limpo = limpar_valor(campo)
                    if valor_limpo is None:
                        raise ValueError(f"Campo inválido: {campo}")
                    registro[colunas[i]] = valor_limpo

                vendas_json.append(registro)
            except Exception as e:
                print(f"⚠️ Venda ignorada por erro de campo: {e}")
                continue

        cur.close()
        conn.close()
        return jsonify(vendas_json)

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
