from flask import Flask, request, jsonify
import openai
import os
import requests
import time
import random
import textwrap
from threading import Thread
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def enviar_mensagem(numero, mensagem):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": mensagem}
    }
    requests.post(url, headers=headers, json=payload)

def dividir_mensagem(texto, max_length=400):
    return textwrap.wrap(texto, width=max_length)

def simular_digitando():
    delay = random.randint(3, 10)
    time.sleep(delay)

def responder(numero_cliente, mensagem_cliente):
    tempo_espera = random.randint(60, 600)
    time.sleep(tempo_espera)

    prompt = f"Responda como se você fosse uma acompanhante chamada Luna, educada, sensual e profissional. A mensagem do cliente foi: '{mensagem_cliente}'"
    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é Luna, uma acompanhante carinhosa e sedutora."},
            {"role": "user", "content": prompt}
        ]
    )
    resposta_texto = resposta.choices[0].message.content
    partes = dividir_mensagem(resposta_texto)

    for parte in partes:
        simular_digitando()
        enviar_mensagem(numero_cliente, parte)
        time.sleep(random.randint(5, 20))

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        entrada = data["entry"][0]["changes"][0]["value"]
        mensagens = entrada.get("messages")
        if mensagens:
            mensagem = mensagens[0]
            texto = mensagem["text"]["body"]
            numero = mensagem["from"]
            Thread(target=responder, args=(numero, texto)).start()
    except Exception as e:
        print("Erro ao processar mensagem:", e)
    return jsonify({"status": "ok"})

@app.route("/webhook", methods=["GET"])
def verificar():
    VERIFY_TOKEN = "luna_verify_token"
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Forbidden", 403

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
