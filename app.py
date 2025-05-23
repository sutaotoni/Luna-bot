from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from utils import gerar_resposta, verificar_mensagem_sensivel, enviar_alerta
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Dicionário para guardar o modo automático por número
modos = {}

@app.route("/bot", methods=["POST"])
def bot():
    numero = request.values.get("From", "")
    msg = request.values.get("Body", "").strip()

    # Se for a garota, ativa o modo manual para esse número
    if numero == os.getenv("NUMERO_GAROTA"):
        modos[numero] = "manual"
        return "Modo manual ativado."

    # Se a conversa estiver em modo manual, não responder
    if modos.get(numero) == "manual":
        return "Aguardando resposta manual da garota."

    # Verifica se a mensagem é sensível
    if verificar_mensagem_sensivel(msg):
        enviar_alerta(numero, msg)
        return responder("Espera um minutinho que já te respondo, tá bom? 💋")

    # Gera resposta sensual
    resposta = gerar_resposta(msg)
    return responder(resposta)

def responder(texto):
    twilio_response = MessagingResponse()
    twilio_response.message(texto)
    return str(twilio_response)

if __name__ == "__main__":
    app.run(debug=True)
