import openai
import os
from twilio.rest import Client

openai.api_key = os.getenv("OPENAI_API_KEY")

def gerar_resposta(pergunta):
    perfil = '''
    Nome: Julia
    Altura: 1,65m
    Peso: 65kg
    Cabelo: loiro escuro
    Tom de pele: morena clara
    Olhos: castanhos
    Nacionalidade: brasileira
    Serviços: beijo de linga, oral, posicoes que voce gosta, massagem
    Preços: 150 euros a hora, 80 euros meia hora
    Adicionais: anal = +30 euros, fantasias = +20 euros
    Endereço: Avenida das Nações, 2, Vila Mariana, São Paulo-SP
    '''

    prompt = f'Você é uma acompanhante chamada Julia. Use um tom sensual e acolhedor. Essas são suas características: {perfil} Responda à pergunta do cliente: {pergunta}'

    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return resposta['choices'][0]['message']['content']

def verificar_mensagem_sensivel(mensagem):
    gatilhos = ["45 minutos", "meia hora", "desconto", "por menos", "tem como fazer", "fazer por", "negociar", "por x", "marcar", "que horas"]
    return any(p in mensagem.lower() for p in gatilhos)

def enviar_alerta(numero_cliente, mensagem_cliente):
    client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    alerta = f"Alerta: cliente {numero_cliente} enviou:\n"{mensagem_cliente}""
    client.messages.create(
        body=alerta,
        from_=os.getenv("TWILIO_SANDBOX_NUMBER"),
        to=os.getenv("ALERTA_WHATSAPP_NUMBER")
    )
