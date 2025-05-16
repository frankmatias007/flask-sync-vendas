from flask import Flask, request, jsonify
import psycopg2
import os

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
def home():
    return "Servidor Flask rodando com sucesso!"

@app.route('/sincronizar-venda', methods=['POST'])
def sincronizar_venda():
    dados = request.json
    try:
        conn = get_conexao()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO vendas (id, data_hora, total, forma_pagamento, usuario_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            dados['id'],
            dados['data_hora'],
            dados['total'],
            dados['forma_pagamento'],
            dados['usuario_id']
        ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "sucesso", "mensagem": "Venda sincronizada"}), 201
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
