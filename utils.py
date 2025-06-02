import openai
import os
from twilio.rest import Client

openai.api_key = os.getenv("OPENAI_API_KEY")

# PERFIL PADRÃO – pode ser dinâmico no futuro
perfil = '''
Nome: Julia
Altura: 1,65m
Peso: 65kg
Cabelo: loiro escuro
Tom de pele: morena clara
Olhos: castanhos
Nacionalidade: brasileira
Serviços: beijo de língua, oral, posições que você gosta, massagem
Preços: 150 euros a hora, 80 euros meia hora
Adicionais: anal = +30 euros, fantasias = +20 euros
Endereço: Avenida das Nações, 2, Vila Mariana, São Paulo-SP
'''

# Função para detectar idioma base na mensagem
def detectar_idioma(texto):
    texto_lower = texto.lower()
    if any(p in texto_lower for p in ["hello", "how", "you", "are", "do", "please"]):
        return "en"
    elif any(p in texto_lower for p in ["hola", "cómo", "quieres", "tienes", "puedo"]):
        return "es"
    else:
        return "pt"

# Função principal de resposta
def gerar_resposta(pergunta):
    idioma = detectar_idioma(pergunta)

    if idioma == "en":
        prompt = f"""
You are Julia, an escort. Answer naturally, seductively, and briefly – like a real WhatsApp conversation. Never send big paragraphs. Be charming, soft, and sexy when needed. Use only short emojis like 💋 or 😉.

Profile:
{perfil}

Client's message:
{pergunta}
"""
    elif idioma == "es":
        prompt = f"""
Eres Julia, una escort. Responde de forma natural, breve y sensual, como si hablaras por WhatsApp. Evita mensajes largos o robóticos. Sé coqueta y directa. Usa emojis suaves como 💋 o 😉

Perfil:
{perfil}

Mensaje del cliente:
{pergunta}
"""
    else:
        prompt = f"""
Você é uma acompanhante chamada Julia. Responda de forma sensual, natural e carinhosa, como se estivesse no WhatsApp. Nada de mensagens longas ou formais. Seja direta, charmosa, envolvente e íntima. Use emojis leves como 💋 ou 😘 com moderação.

Perfil:
{perfil}

Mensagem do cliente:
{pergunta}
"""

    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    texto = resposta['choices'][0]['message']['content'].strip()

    # Limita o texto a no máximo 2 frases
    frases = texto.split(". ")
    texto_final = ". ".join(frases[:2]).strip()
    if not texto_final.endswith("."):
        texto_final += "."

    return texto_final

# Gatilhos para sensibilidade (ajuste conforme casos reais)
def verificar_mensagem_sensivel(mensagem):
    gatilhos = [
        "45 minutos", "meia hora", "desconto", "por menos",
        "tem como fazer", "fazer por", "negociar", "por x", "marcar", "que horas"
    ]
    return any(p in mensagem.lower() for p in gatilhos)

# Alerta via WhatsApp para a garota
def enviar_alerta(numero_cliente, mensagem_cliente):
    client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    alerta = f"Alerta: cliente {numero_cliente} enviou:\n\"{mensagem_cliente}\""
    client.messages.create(
        body=alerta,
        from_=os.getenv("TWILIO_SANDBOX_NUMBER"),
        to=os.getenv("ALERTA_WHATSAPP_NUMBER")
    )
