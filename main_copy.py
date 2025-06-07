from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
from dotenv import load_dotenv
from openai import OpenAI   # <— IMPORTANDO EL CLIENTE V1.X

# ───── 1) Cargar variables de entorno ───────────────────────────────────────
#    Asegúrate de que justo al lado esté tu archivo “.env” con la línea:
#      OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

# ───── 2) Instanciar el cliente de OpenAI (v1.x, p.ej. 1.84.0) ──────────────
openai_client = OpenAI()

# ───── 3) Inicializar la app Flask ─────────────────────────────────────────
app = Flask(__name__)

# ───── 4) Definir el endpoint /bot que Twilio invocará ───────────────────────
@app.route("/bot", methods=["POST"])
def bot():
    # 4.1) Obtener el texto entrante (campo “Body” que Twilio manda)
    incoming_msg = request.values.get("Body", "").strip()

    # 4.2) Si viene vacío, devolvemos un mensaje de “error amigable”
    if not incoming_msg:
        reply = "Por favor, envíame un mensaje para que pueda ayudarte."
    else:
        # 4.3) Llamar a GPT-4o para generar respuesta
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o",                      # <— modelo GPT-4o
                messages=[{"role": "user", "content": incoming_msg}],
                max_tokens=150
            )
            # 4.4) Extraer el texto que generó GPT-4o
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            # Si ocurre un error al llamar a OpenAI, lo mostramos en consola
            print(f"[Error con OpenAI v1.x + gpt-4o]: {e}")
            reply = "Lo siento, hubo un problema al generar mi respuesta."

    # 4.5) Enviar la respuesta de vuelta a WhatsApp usando Twilio
    twilio_resp = MessagingResponse()
    twilio_resp.message(reply)
    return str(twilio_resp)

# ───── 5) Arrancar el servidor Flask en el puerto 5000 ───────────────────────
if __name__ == "__main__":
    # host="0.0.0.0" permite que ngrok o tu VPS accedan desde fuera
    app.run(host="0.0.0.0", port=5000, debug=True)
