import requests

url = "https://flask-sync-vendas-2.onrender.com/sincronizar-venda"

dados = {
    "id": 1,
    "data_hora": "2025-05-15 23:45:00",
    "total": 129.90,
    "forma_pagamento": "Cartão",
    "usuario_id": 2
}

resposta = requests.post(url, json=dados)

print("Status:", resposta.status_code)
print("Resposta:", resposta.text)
