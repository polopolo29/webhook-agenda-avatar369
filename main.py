# main.py
from flask import Flask, request, jsonify, abort, Response
from twilio.rest import Client
import openai
import os
import threading
import logging
import hmac
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from dateutil import parser as dateparser

# Importar utilidades de calendario
from calendar_utils import get_available_slots, crear_evento_google_calendar

# ─── CARGA DE VARIABLES DE ENTORNO ─────────────────────────────────────────────
load_dotenv()
TWILIO_ACCOUNT_SID     = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN      = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
OPENAI_API_KEY         = os.getenv("OPENAI_API_KEY")
VERIFY_TOKEN           = os.getenv("VERIFY_TOKEN")              # Token para verificar webhooks
WP_WEBHOOK_SECRET      = os.getenv("WP_WEBHOOK_SECRET")           # Secreto HMAC WooCommerce
SUBSCRIBED_USERS       = [u.strip() for u in os.getenv("SUBSCRIBED_USERS", "").split(",") if u.strip()]
EBOOK_LINK             = os.getenv("EBOOK_LINK")
EBOOK_METODO_LINK      = os.getenv("EBOOK_METODO_LINK")
CURSO_LINK             = os.getenv("CURSO_LINK")

# ─── CONFIG CLIENTES Y LOGGING ─────────────────────────────────────────────────
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
openai.api_key = OPENAI_API_KEY
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# ─── ESTADO TEMPORAL PARA SEGUIMIENTO ──────────────────────────────────────────
pending_slots    = {}
paid_users       = set()
scheduled_users  = set()
interested_users = {}

# ─── APP ───────────────────────────────────────────────────────────────────────
app = Flask(__name__)

# ─── UTILIDADES ─────────────────────────────────────────────────────────────────
def parse_fecha_usuario(text: str):
    try:
        return dateparser.parse(text, dayfirst=True)
    except Exception:
        return None


def normalize_phone(phone: str) -> str:
    digits = ''.join(filter(str.isdigit, phone))
    if digits.startswith('52') and len(digits) == 12:
        return f"whatsapp:+{digits}"
    if len(digits) == 10:
        return f"whatsapp:+52{digits}"
    return f"whatsapp:+{digits}"


def validar_wc_signature(payload: bytes, signature: str) -> bool:
    if not WP_WEBHOOK_SECRET:
        return True
    mac = hmac.new(WP_WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, signature)


def send_ebook_method(phone: str):
    msg = (
        "No podemos negarle la salud a nadie, cualquier servicio es un intercambio justo de energía, amor y dedicación. "
        "Te invito nuevamente a agendar ya que cualquier método de medicina convencional es poco probable que devuelva la salud.\n\n"
        "Le comparto con cariño y fe el método científico que usamos:\n"
        f"{EBOOK_METODO_LINK}\n\n"
        "Descárgalo gratis."
    )
    twilio_client.messages.create(
        body=msg,
        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        to=normalize_phone(phone)
    )
    logging.info(f"Ebook 'El Método' enviado a {phone}")


def schedule_followup(phone: str):
    if phone not in paid_users and phone not in scheduled_users:
        send_ebook_method(phone)
    interested_users.pop(phone, None)


def notificar_nuevo_contenido(phone: str, mensaje: str):
    try:
        twilio_client.messages.create(
            body=f"Nuevo contenido publicado:\n{mensaje}",
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            to=normalize_phone(phone)
        )
        logging.info(f"Notificación enviada a {phone}")
    except Exception as e:
        logging.error(f"Error notificando {phone}: {e}")

# ─── RUTAS ──────────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET","HEAD"], strict_slashes=False)
def index():
    return jsonify({"message": "Webhook is alive."}), 200

@app.route("/incoming", methods=["GET","POST"], strict_slashes=False)
def incoming_whatsapp():
    # Verificación GET para Twilio
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return Response(challenge, status=200, mimetype='text/plain')
        return Response('Token inválido', status=403, mimetype='text/plain')

    # POST entrante
    frm = request.form.get("From", "")
    body = request.form.get("Body", "").strip()
    phone = frm.replace("whatsapp:", "")
    text = body.lower()

    # 1) Confirmación slot pendiente
    if phone in pending_slots:
        slot = pending_slots.pop(phone)
        crear_evento_google_calendar(phone, slot, gratuito=False, description=body)
        scheduled_users.add(phone)
        msg = f"Tu cita ha sido agendada para {slot} con padecimiento: {body}. ¡Nos vemos pronto!"
        twilio_client.messages.create(body=msg, from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}", to=frm)
        return "", 200

    # 2) Flujo 'informes'
    if any(k in text for k in ("informes","más información","terapia","consulta","enfermedad")):
        interested_users[phone] = datetime.now()
        msg = (
            "Hola 👋, soy Emilia tu asistente en *Avatarmexchange*.\n"
            "Mira estos videos para entender el método y tratamiento:\n"
            f"• Método: https://www.instagram.com/p/C9fNSX8s6Rp/\n"
            f"• Tratamiento: https://www.instagram.com/p/C8jBPP0osN-/\n"
            f"• Curso: https://www.youtube.com/watch?v=fRWlGnDlGAY\n\n"
            "En 8 min pregunto si los viste para continuar."
        )
        twilio_client.messages.create(body=msg, from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}", to=frm)
        threading.Timer(8*60, lambda: twilio_client.messages.create(
            body="¿Ya viste los videos? Podemos continuar con la reserva.",
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}", to=frm
        )).start()
        threading.Timer(24*3600, lambda: schedule_followup(phone)).start()
        return "", 200

    # 3) Selección de fecha
    fecha = parse_fecha_usuario(text)
    if fecha:
        slot = fecha.strftime("%Y-%m-%d %H:%M")
        pending_slots[phone] = slot
        resp = f"Has seleccionado {slot}. Por favor indícame tu padecimiento."
        twilio_client.messages.create(body=resp, from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}", to=frm)
        return "", 200

    # 4) Guía de compra
    if text in ("sí","si","me gustaría","me gustaria"):
        guia = (
            "Te guío paso a paso:\n"
            "1) Ve a https://avatarmexchange.com\n"
            "2) Añade al carrito\n"
            "3) Aplica cupón '3terapias'\n"
            "4) Elige Mercado Pago u OXXO\n"
            "5) Completa y confirma\n"
        )
        twilio_client.messages.create(body=guia, from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}", to=frm)
        return "", 200

    # 5) Ebook 'El Método'
    if "método" in text or "metodo" in text:
        msg = f"El ebook ‘El Método’ te permite sanar...\n{EBOOK_METODO_LINK}\nResponde 'sí' si quieres guía."
        twilio_client.messages.create(body=msg, from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}", to=frm)
        return "", 200

    # 6) Curso
    if "curso" in text:
        msg = f"El curso 'Medicina de Quinta Dimensión'...\n{CURSO_LINK}\nResponde 'sí' si quieres guía."
        twilio_client.messages.create(body=msg, from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}", to=frm)
        return "", 200

    # 7) Fallback IA
    prompt = f"Eres Emilia, la asistente virtual de AvatarMexchange.\nUsuario: {text}\nEmilia:"
    try:
        ai_resp = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role":"assistant","content":prompt}],
            max_tokens=500,
            temperature=0.7
        )
        respuesta = ai_resp.choices[0].message.content.strip()
    except Exception:
        logging.exception("OpenAI error")
        respuesta = "Lo siento, tuve un error con mi IA."
    twilio_client.messages.create(body=respuesta, from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}", to=frm)
    return "", 200

@app.route("/webhook", methods=["GET","POST","HEAD"], strict_slashes=False)
def webhook_woocommerce():
    # Verificación GET/HEAD para Facebook y Twilio
    if request.method in ("GET","HEAD"):
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return Response(challenge, status=200, mimetype='text/plain')
        return Response('Token inválido', status=403, mimetype='text/plain')

    # POST WooCommerce
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status":"no data"}), 200
    payload = request.data
    signature = request.headers.get("X-WC-Webhook-Signature", "")
    if not validar_wc_signature(payload, signature):
        abort(403)
    billing = data.get("billing", {})
    items   = data.get("line_items", [])
    phone   = billing.get("phone", "")
    name    = billing.get("first_name", "Cliente")
    if not phone:
        return jsonify({"status":"missing phone"}), 200
    to_wh = normalize_phone(phone)
    paid_users.add(phone)
    if any("Terapia" in i.get("name","") for i in items):
        slots = get_available_slots()
        lista = "\n".join(f"🕒 {s}" for s in slots)
        msg = f"Hola {name}, gracias por tu compra de terapia. Horarios:\n{lista}"
    else:
        msg = f"Hola {name}, ¡gracias por tu compra! E-book: {EBOOK_LINK}"
    twilio_client.messages.create(body=msg, from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}", to=to_wh)
    return jsonify({"status":"ok"}), 200

@app.route("/nuevo_contenido", methods=["POST"], strict_slashes=False)
def nuevo_contenido():
    data = request.get_json(force=True)
    if WP_WEBHOOK_SECRET:
        hdr = request.headers.get("X-WP-Webhook-Secret", "")
        if hdr != WP_WEBHOOK_SECRET:
            abort(403)
    titulo = data.get("title")
    enlace = data.get("permalink")
    if not titulo or not enlace:
        return jsonify({"status":"missing data"}), 200
    mensaje = f"{titulo}\n{enlace}"
    for user in SUBSCRIBED_USERS:
        notificar_nuevo_contenido(user, mensaje)
    return jsonify({"status":"enviado","count":len(SUBSCRIBED_USERS)}), 200

# ─── PRODUCCIÓN ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
