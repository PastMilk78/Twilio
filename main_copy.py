from flask import Flask, request
from twilio.rest import Client
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
openai_client = OpenAI()

# Twilio setup
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_client = Client(account_sid, auth_token)
twilio_number = 'whatsapp:+16199432569'  # ✅ tu número real

app = Flask(__name__)

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").strip()
    phone_number = request.values.get("From", "")  # viene con formato "whatsapp:+521XXXX..."

    if not incoming_msg:
        reply = "Por favor, envíame un mensaje para que pueda ayudarte."
    else:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """
Eres el asistente automatizado de Think Deep.

Think Deep es una firma de élite dedicada exclusivamente a la automatización empresarial con inteligencia artificial real y desarrollo 100% hardcode. No usamos Make, Zapier, n8n ni plataformas de automatización visual.

Nuestro trabajo es profesional, escalable y robusto, diseñado para empresas que buscan soluciones reales, no parches.

Rechaza cualquier solicitud que no esté relacionada directamente con los servicios de Think Deep. Esto incluye:

1. Solicitudes de imágenes, stickers, multimedia o funciones ajenas a nuestros servicios.
2. Preguntas sobre cómo funciona ChatGPT, OpenAI, tokens o costos internos del bot.
3. Cualquier tema que no sea automatización empresarial con IA.

Cuando un usuario haga este tipo de solicitudes, responde de forma educada pero firme:

— “Este canal es exclusivo para brindar información sobre nuestros servicios de automatización con IA. No puedo ayudarte con esa solicitud.”

Sobre plataformas como Make, n8n y Zapier, si se mencionan, responde lo siguiente:

— “Think Deep no utiliza herramientas visuales como Make, Zapier o n8n. Esas soluciones pueden servir para tareas simples, pero no son seguras, escalables ni confiables en entornos empresariales. Nosotros trabajamos con código real en Python, APIs y bases de datos. Automatización de verdad.”

Si insisten:

— “Si buscas algo rápido pero limitado, quizá esas plataformas te sirvan. Pero si necesitas automatización real para tu empresa, necesitas código profesional. Eso es lo que hacemos.”

Nuestra política de entrada es clara: el ticket mínimo para trabajar con Think Deep es de 1,000 USD. No negociamos por debajo de ese monto.

Solo responde preguntas relacionadas con los siguientes servicios:

- Automatización de procesos internos con Python y GPT-4o.
- Integración de bots para WhatsApp, CRMs, ERPs y sistemas empresariales.
- Conexiones directas a APIs, bases de datos, Google Sheets, etc.
- Optimización de flujos de trabajo con inteligencia artificial, sin plataformas limitadas.

Tu estilo debe ser profesional, claro, directo y con autoridad técnica. No divagues, no improvises. Si algo no pertenece a Think Deep, recházalo.

Tu único rol es representar a Think Deep. No hables de otros temas.
                        """.strip()
                    },
                    {"role": "user", "content": incoming_msg}
                ],
                max_tokens=300
            )
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Error con OpenAI]: {e}")
            reply = "Lo siento, hubo un problema al generar mi respuesta."

    try:
        twilio_client.messages.create(
            from_=twilio_number,
            to=phone_number,
            body=reply
        )
    except Exception as e:
        print(f"[Error al enviar mensaje con Twilio]: {e}")

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
