# main.py

from flask import Flask, request, jsonify
import os
import threading
from datetime import datetime
from utils import (
    enviar_mensaje_whatsapp,
    guardar_usuario_temporal,
    verificar_conversion,
    marcar_conversion
)
from calendar_utils import get_available_slots, crear_evento_google_calendar
from chatbot_agent import responder_con_ia

app = Flask(__name__)

PRODUCTOS_TERAPIA = [
    "Tratamiento completo 3 sesiones",
    "Terapia individual"
]

# Diccionario para guardar timers de recordatorio de compra en curso
recordatorios_compra = {}  # clave: número, valor: threading.Timer

def enviar_recordatorio_compra(numero):
    """
    Se llama 1 hora después de haber enviado los videos al usuario sin compra.
    Envía el enlace para comprar la terapia individual.
    """
    mensaje = (
        "¿Viste los videos y estás listo para agendar tu terapia? 🌀\n\n"
        "Puedes reservar tu sesión de 50 minutos aquí (con cupón \"3terapias\" para un descuento especial):\n"
        "https://avatarmexchange.com/product/terapia-online/?currency=mxn\n\n"
        "¡No dudes más, estás a punto de sanar! 🌟"
    )
    enviar_mensaje_whatsapp(numero, mensaje)
    # Eliminamos el timer de la memoria para no repetir
    recordatorios_compra.pop(numero, None)

def seguimiento_dia6(numero):
    """
    A los 6 días de haber enviado el e-book, si no hubo conversión,
    envía invitación a adquirir "El Método".
    """
    def tarea():
        if not verificar_conversion(numero):
            mensaje = (
                "Hola, espero estés disfrutando de \"El libro de la sabiduría\" 📘✨\n\n"
                "Si te ha parecido fascinante, te invito a que adquieras \"El Método\", la novela que explica la cura "
                "y la sanación a todas las enfermedades. El texto médico más avanzado del siglo XXI."
            )
            enviar_mensaje_whatsapp(numero, mensaje)
            seguimiento_dia7(numero)
    threading.Timer(6 * 86400, tarea).start()

def seguimiento_dia7(numero):
    """
    A los 7 días de haber enviado el e-book, si no hubo conversión,
    envía invitación al curso basado en "El Método".
    """
    def tarea():
        if not verificar_conversion(numero):
            mensaje = (
                "📹 Si lo tuyo no es leer, te recomiendo tomes el curso basado en el libro \"El Método\".\n\n"
                "Explicaremos cada técnica de sanación para cada enfermedad y regeneración celular contra el envejecimiento, "
                "con videos didácticos. ¡No dejes pasar esta oportunidad!"
            )
            enviar_mensaje_whatsapp(numero, mensaje)
    threading.Timer(7 * 86400, tarea).start()

def seguimiento_no_conversion(numero):
    """
    A las 24 horas de que el usuario preguntó sin comprar, envía oferta de consulta gratuita
    (viernes y sábado si sacrifica su sustento).
    """
    def tarea():
        if not verificar_conversion(numero):
            mensaje = (
                "Tratamos de que la terapia sea accesible para todos. "
                "Si no tienes posibilidades económicas para pagar la consulta, "
                "solo si al pagar sacrificarías tu sustento, con gusto te ofrecemos "
                "citas gratuitas los viernes y sábados (según disponibilidad).\n\n"
                "Además, mira estos videos para entender mejor el servicio antes de decidir:\n"
                "• Método: https://www.instagram.com/p/C9fNSX8s6Rp/\n"
                "• Tratamiento: https://www.instagram.com/p/C8jBPP0osN-/\n\n"
                "¿Le gustaría tomar gratis una consulta?"
            )
            enviar_mensaje_whatsapp(numero, mensaje)
    threading.Timer(86400, tarea).start()  # 86400 segundos = 24 horas

@app.route("/webhook", methods=["POST"])
def recibir_webhook():
    """
    Webhook que recibe eventos de WooCommerce cuando se crea o paga un pedido.
    Determina si el producto es una terapia o no, y envía el mensaje correspondiente.
    """
    data = request.get_json()
    try:
        numero = data["billing"]["phone"]       # ej. "5512345678"
        nombre = data["billing"]["first_name"]
        productos = [item["name"] for item in data["line_items"]]
        es_terapia = any(p in PRODUCTOS_TERAPIA for p in productos)

        if es_terapia:
            slots = get_available_slots()
            mensaje = (
                f"Hola {nombre}, gracias por agendar tu terapia 🧘‍♀️✨\n\n"
                "Estos son los horarios disponibles:\n"
            )
            for s in slots:
                mensaje += f"🕒 {s}\n"
            mensaje += "\nResponde con el horario que prefieras para reservarlo."
            enviar_mensaje_whatsapp(numero, mensaje)
            marcar_conversion(numero)

        else:
            mensaje = (
                f"Hola {nombre}, gracias por tu compra 🛍️✨\n\n"
                "Te obsequiamos un e-book: 📘 \"El libro de la sabiduría\".\n"
                "Descárgalo aquí:\n"
                "https://mega.nz/file/I7EQBThK#9h_XGs8O0qFZ0rakwjTX38hILssOmS6_U04QX4kbEdg"
            )
            enviar_mensaje_whatsapp(numero, mensaje)
            marcar_conversion(numero)
            seguimiento_dia6(numero)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Error en Webhook:", e)
        return jsonify({"status": "error", "details": str(e)}), 400

@app.route("/incoming", methods=["POST"])
def incoming_whatsapp():
    """
    Endpoint para procesar mensajes entrantes de Twilio Sandbox para WhatsApp.
    Incluye lógica para:
      - Oferta gratuita y agendado de viernes/sábado.
      - Confirmación de horario gratuito.
      - Envío de videos e invitación a compra con recordatorio en 1h.
      - Respuestas mediante IA o reglas para otros casos.
    """
    numero_prefijo = request.form.get("From")    # ej. "whatsapp:+5215512345678"
    numero = numero_prefijo.replace("whatsapp:", "")
    texto = request.form.get("Body").strip().lower()

    # Si existe un timer de recordatorio para este número, lo cancelamos
    if numero in recordatorios_compra:
        recordatorios_compra[numero].cancel()
        recordatorios_compra.pop(numero, None)

    # -- Caso A: Usuario acepta oferta gratuita (“sí”, “me gustaría”) --
    if "sí" in texto or texto == "si" or "me gustaría" in texto:
        slots = get_available_slots()
        disponibles_f_v = [
            s for s in slots
            if datetime.strptime(s, "%Y-%m-%d %H:%M").weekday() in (4, 5)
        ]
        if disponibles_f_v:
            mensaje = "Estos son los horarios gratuitos disponibles (viernes y sábado):\n"
            for s in disponibles_f_v:
                mensaje += f"• {s}\n"
            mensaje += "\nResponde con el horario que elijas para confirmar tu cita gratuita."
            enviar_mensaje_whatsapp(numero, mensaje)
        else:
            mensaje = (
                "En este momento no hay disponibilidad gratuita para viernes o sábado.\n"
                "Te avisaré cuando haya un espacio disponible. ¡Gracias por tu paciencia!"
            )
            enviar_mensaje_whatsapp(numero, mensaje)
        return "", 200

    # -- Caso B: Usuario responde con un horario válido (“YYYY-MM-DD HH:MM”) --
    try:
        elegido = datetime.strptime(texto, "%Y-%m-%d %H:%M")
        crear_evento_google_calendar(numero, texto, gratuito=True)
        enviar_mensaje_whatsapp(numero, f"Tu consulta gratuita ha sido agendada para {texto}. ¡Nos vemos pronto!")
        marcar_conversion(numero)
        return "", 200
    except:
        pass

    # -- Caso C: Usuario pregunta por “consulta” o “terapia” sin haber comprado --
    if "consulta" in texto or "terapia" in texto:
        guardar_usuario_temporal(numero)
        seguimiento_no_conversion(numero)
        # Envío inicial: saludo + videos + programación de recordatorio de compra en 1h
        mensaje = (
            "¿Sufres alguna enfermedad o padecimiento que quieras erradicar? Toma una consulta.\n\n"
            "🌐 Adquiérela aquí (cupón 3terapias):\n"
            "https://avatarmexchange.com/product/tratamiento-completo-3-cesiones/?currency=mxn\n\n"
            "📺 Para que veas el método que te va a devolver la salud, mira este video:\n"
            "https://www.instagram.com/p/C9fNSX8s6Rp/\n\n"
            "🌀 El tratamiento se explica en este otro video:\n"
            "https://www.instagram.com/p/C8jBPP0osN-/\n\n"
            "— O —\n"
            "¿Quizás te gustaría aprender Medicina Cuántica de Quinta Dimensión y tener acceso al contenido premium?\n"
            "https://avatarmexchange.com/product/medicina-de-quinta-dimension/?currency=mxn\n\n"
            "También te recomiendo el libro ‘El Método’ para entender todo en detalle:\n"
            "https://avatarmexchange.com/product/el-metodo-la-cura-y-sanacion-a-toda-enfermedad/"
        )
        enviar_mensaje_whatsapp(numero, mensaje)

        # Programar recordatorio de compra a 1 hora
        t = threading.Timer(3600, enviar_recordatorio_compra, args=[numero])  # 3600 s = 1 h
        t.start()
        recordatorios_compra[numero] = t

        return "", 200

    # -- Caso D: Cualquier otra cosa → IA o reglas --
    respuesta = responder_con_ia(texto, numero)
    enviar_mensaje_whatsapp(numero, respuesta)
    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

