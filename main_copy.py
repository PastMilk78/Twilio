from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os
from dotenv import load_dotenv

# ─── 1) Carga las variables de entorno desde .env ────────────────────────
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ─── 2) Inicializa Flask ─────────────────────────────────────────────────
app = Flask(__name__)

# ─── 3) Endpoint que Twilio llamará cuando llegue un mensaje ──────────────
@app.route("/bot", methods=["POST"])
def bot():
    # 3.1) Obtiene el mensaje que envió el usuario por WhatsApp
    incoming_msg = request.values.get("Body", "").strip()

    # 3.2) Si el mensaje está vacío, enviamos un texto de “error”
    if not incoming_msg:
        reply = "Por favor, envíame un mensaje para que pueda ayudarte."
    else:
        # 3.3) Llamamos a OpenAI GPT-3.5 para generar una respuesta
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": incoming_msg}],
                max_tokens=150
            )
            # 3.4) Extraemos el texto de la respuesta
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error con OpenAI: {e}")
            reply = "Lo siento, hubo un problema al generar mi respuesta."

    # 3.5) Construimos la respuesta de Twilio en formato TwiML
    twilio_response = MessagingResponse()
    twilio_response.message(reply)
    return str(twilio_response)

# ─── 4) Arrancamos el servidor en el puerto 5000 ───────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
