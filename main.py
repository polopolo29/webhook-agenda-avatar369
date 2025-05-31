# main.py
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import threading
import json

from calendar_utils import get_available_slots
from utils import enviar_mensaje_whatsapp, guardar_usuario_temporal, verificar_conversion

load_dotenv()
app = Flask(__name__)

# Lista de productos considerados "terapias"
PRODUCTOS_TERAPIA = [
    "Terapia Individual",
    "Consulta Avatar369",
    "Terapia Avatar",
    "Sanación Espiritual",
    "Consulta Energética"
]

# --- ENVÍO A LOS 6 DÍAS: promoción del libro "El Método"
def seguimiento_dia6(numero):
    def tarea():
        if not verificar_conversion(numero):
            mensaje = (
                "Hola, espero estés disfrutando de una de las lecturas más interesantes del mundo 📘✨\n\n"
                "Si te ha parecido fascinante, te invito a que adquieras *\"El Método\"*, "
                "la novela que explica la cura y la sanación a todas las enfermedades.\n\n"
                "El conocimiento del libro de la sabiduría aplicado a la salud: "
                "el texto médico más avanzado del siglo XXI."
            )
            enviar_mensaje_whatsapp(numero, mensaje)
            seguimiento_dia7(numero)  # Programamos día 7 también

    threading.Timer(6 * 86400, tarea).start()

# --- ENVÍO AL DÍA 7: promoción del curso
def seguimiento_dia7(numero):
    def tarea():
        if not verificar_conversion(numero):
            mensaje = (
                "📹 Si lo tuyo no es leer, te recomiendo tomes el curso basado en el libro *\"El Método\"*.\n\n"
                "Explicaremos cada técnica de sanación correspondiente a cada enfermedad y regeneración celular contra el envejecimiento, "
                "de forma simple y con videos didácticos hechos para todo público.\n\n"
                "No solo aprenderás a sanar las enfermedades, sino a vivir fuera de su alcance. ¡No dejes pasar esta oportunidad!"
            )
            enviar_mensaje_whatsapp(numero, mensaje)
    threading.Timer(7 * 86400, tarea).start()

# --- ENVÍO A LAS 24 HORAS si preguntaron pero no compraron
def seguimiento_no_conversion(numero):
    def tarea():
        if not verificar_conversion(numero):
            mensaje = (
                "Espero que te decidas a agendar una consulta 🙏.\n\n"
                "Gracias a Dios, todo en este mundo tiene una solución.\n\n"
                "Te comparto nuestro método de sanación, será la forma con la que trabajaremos.\n"
                "No podemos negarle a nadie la salud. Con ese conocimiento podrás recuperarla.\n\n"
                "Descárgalo gratis aquí:\n"
                "https://mega.nz/file/QqUy1QyT#V4ZhLwrePnm7TBjD0ihOXIJlRiI6xagKDru1F3HiBUI"
            )
            enviar_mensaje_whatsapp(numero, mensaje)

    threading.Timer(86400, tarea).start()  # 24h

@app.route("/webhook", methods=["POST"])
def recibir_webhook():
    data = request.get_json()

    try:
        numero = data["billing"]["phone"]
        nombre = data["billing"]["first_name"]
        productos = [item["name"] for item in data["line_items"]]

        es_terapia = any(p in PRODUCTOS_TERAPIA for p in productos)

        if es_terapia:
            horarios = get_available_slots()
            mensaje = f"Hola {nombre}, gracias por agendar tu terapia 🧘‍♀️✨\n\nEstos son los horarios disponibles:\n\n"
            for slot in horarios:
                mensaje += f"🕒 {slot}\n"
            mensaje += "\nResponde con el horario que prefieras para reservar tu espacio. 🙌"
            enviar_mensaje_whatsapp(numero, mensaje)

        else:
            mensaje = (
                f"Hola {nombre}, gracias por tu compra 🛍️✨\n\n"
                "Queremos regalarte un eBook especial: *El libro de la sabiduría* 📘\n\n"
                "Descárgalo aquí:\n"
                "https://mega.nz/file/I7EQBThK#9h_XGs8O0qFZ0rakwjTX38hILssOmS6_U04QX4kbEdg"
            )
            enviar_mensaje_whatsapp(numero, mensaje)
            seguimiento_dia6(numero)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Error en webhook:", e)
        return jsonify({"status": "error", "details": str(e)}), 400

@app.route("/pregunta", methods=["POST"])
def pregunta_sin_compra():
    data = request.get_json()
    numero = data.get("phone")

    if numero:
        guardar_usuario_temporal(numero)
        seguimiento_no_conversion(numero)
        return jsonify({"status": "pregunta registrada"}), 200

    return jsonify({"status": "número faltante"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
