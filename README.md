# Luna-Bot (Bot Sensual com IA para WhatsApp)

## Como usar

1. Crie uma conta no [Twilio](https://twilio.com)
2. Ative o sandbox do WhatsApp
3. Configure seu `.env` com os dados da OpenAI e Twilio
4. Faça deploy no [Render](https://render.com)

## Rotas

- `/bot` – recebe mensagens do WhatsApp, responde com IA, e alerta a garota em caso de negociação.

## Alerta

O bot envia mensagens de alerta para um número alternativo de WhatsApp sempre que um cliente tentar negociar valores ou marcar horários.
