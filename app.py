import os
import time
import threading
import random
from flask import Flask, request
from openai import OpenAI
from twilio.rest import Client

app = Flask(__name__)

VERIFY_TOKEN = "luna_verify_token"
WHATSAPP_NUMBER_ID = "648517815015194"
ACCESS_TOKEN = os.environ.get("META_TOKEN")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
ALERTA_TELEFONE = os.environ.get("ALERTA_TELEFONE")
ALERTA_EMAIL = os.environ.get("ALERTA_EMAIL")

client = OpenAI(api_key=OPENAI_KEY)

def enviar_mensagem_whatsapp(numero, mensagem):
    import requests
    url = f"https://graph.facebook.com/v19.0/{WHATSAPP_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": mensagem}
    }
    requests.post(url, headers=headers, json=data)

def notificar_garota(mensagem):
    if ALERTA_TELEFONE:
        enviar_mensagem_whatsapp(ALERTA_TELEFONE, f"[Alerta da Luna] {mensagem}")
    if ALERTA_EMAIL:
        print(f"[EMAIL ENVIADO PARA {ALERTA_EMAIL}] - {mensagem}")
        # Para envio real de email, precisa integração (ex: SMTP, SendGrid, etc)

@app.route("/webhook", methods=["GET"])
def verificar():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Erro de verificação", 403

@app.route("/webhook", methods=["POST"])
def receber():
    dados = request.get_json()
    try:
        mensagens = dados["entry"][0]["changes"][0]["value"]["messages"]
        for msg in mensagens:
            telefone = msg["from"]
            texto = msg["text"]["body"]
            threading.Thread(target=responder, args=(telefone, texto)).start()
    except KeyError:
        pass
    return "OK", 200

def responder(telefone, texto):
    print(f"[DEBUG] Iniciando resposta para: {telefone} - Texto: {texto}")
    try:
        delay = random.randint(60, 300)
        print(f"Esperando {delay} segundos antes de responder...")
        time.sleep(delay)
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é uma acompanhante chamada Luna. Seja gentil, provocante e receptiva."},
                {"role": "user", "content": texto}
            ]
        )
        resposta_texto = resposta.choices[0].message.content
        partes = [resposta_texto[i:i+600] for i in range(0, len(resposta_texto), 600)]
        for parte in partes:
            enviar_mensagem_whatsapp(telefone, parte)
            time.sleep(2)
        if "horário" in texto.lower():
            print("[DEBUG] Palavra-chave 'horário' detectada")
            notificar_garota("O cliente perguntou sobre horários:")
        print(f"{texto}")
    except Exception as e:
        print(f"[ERRO] {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
