import os
import time
import threading
import random
from flask import Flask, request
from openai import OpenAI
import requests

app = Flask(__name__)

# Variáveis de ambiente
VERIFY_TOKEN = "luna_verify_token"
WHATSAPP_NUMBER_ID = os.environ.get("WHATSAPP_NUMBER_ID", "648517815015194")
ACCESS_TOKEN = os.environ.get("META_TOKEN")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
ALERTA_TELEFONE = os.environ.get("ALERTA_TELEFONE")
ALERTA_EMAIL = os.environ.get("ALERTA_EMAIL")

# Checagem das variáveis de ambiente
def checar_envs():
    variaveis = {
        "ACCESS_TOKEN": ACCESS_TOKEN,
        "OPENAI_KEY": OPENAI_KEY,
        "WHATSAPP_NUMBER_ID": WHATSAPP_NUMBER_ID
    }
    for nome, valor in variaveis.items():
        if not valor:
            print(f"[ERRO] Variável de ambiente {nome} não definida!")

checar_envs()

client = OpenAI(api_key=OPENAI_KEY)

def enviar_mensagem_whatsapp(numero, mensagem):
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
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"[DEBUG] Enviando para WhatsApp: {data} | Status: {resp.status_code} | Resposta: {resp.text}")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar mensagem WhatsApp: {str(e)}")

def notificar_garota(mensagem):
    if ALERTA_TELEFONE:
        enviar_mensagem_whatsapp(ALERTA_TELEFONE, f"[Alerta da Luna] {mensagem}")
    if ALERTA_EMAIL:
        print(f"[EMAIL ENVIADO PARA {ALERTA_EMAIL}] - {mensagem}")

@app.route("/webhook", methods=["GET"])
def verificar():
    print("[DEBUG] GET recebido no webhook para verificação")
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Erro de verificação", 403

@app.route("/webhook", methods=["POST"])
def receber():
    dados = request.get_json()
    print(f"[DEBUG] Webhook recebido: {dados}")
    try:
        mensagens = dados["entry"][0]["changes"][0]["value"].get("messages")
        if not mensagens:
            print("[DEBUG] Nenhuma mensagem encontrada no payload!")
            return "OK", 200
        for msg in mensagens:
            telefone = msg["from"]
            texto = msg["text"]["body"]
            print(f"[DEBUG] Mensagem recebida de {telefone}: {texto}")
            threading.Thread(target=responder, args=(telefone, texto)).start()
    except Exception as e:
        print(f"[ERRO] Falha ao processar webhook: {str(e)}")
    return "OK", 200

def responder(telefone, texto):
    print(f"[DEBUG] Iniciando resposta para: {telefone} - Texto: {texto}")
    try:
        delay = random.randint(60, 300)  # Entre 1 e 5 minutos
        print(f"[DEBUG] Esperando {delay} segundos antes de responder...")
        time.sleep(delay)
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é uma acompanhante chamada Luna. Seja gentil, provocante e receptiva."},
                {"role": "user", "content": texto}
            ]
        )
        resposta_texto = resposta.choices[0].message.content
        print(f"[DEBUG] Resposta da OpenAI: {resposta_texto}")
        partes = [resposta_texto[i:i+600] for i in range(0, len(resposta_texto), 600)]
        for parte in partes:
            enviar_mensagem_whatsapp(telefone, parte)
            time.sleep(2)
        if "horário" in texto.lower():
            print("[DEBUG] Palavra-chave 'horário' detectada, notificando garota...")
            notificar_garota("O cliente perguntou sobre horários.")
        print(f"[DEBUG] Resposta enviada com sucesso para {telefone}")
    except Exception as e:
        print(f"[ERRO] Falha no responder: {str(e)}")

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=porta)
