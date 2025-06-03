# utils.py

import os
import json
from twilio.rest import Client

USUARIOS_TEMP_FILE = "usuarios_temp.json"
CONVERSIONES_FILE = "conversiones.json"

def enviar_mensaje_whatsapp(numero_destino, mensaje):
    """
    Envía un mensaje a WhatsApp usando Twilio Sandbox.
    - numero_destino: Cadena con código de país y número (p.ej. "5215512345678").
    - mensaje: Texto plano a enviar.
    """
    client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    msg = client.messages.create(
        from_=os.getenv("TWILIO_SANDBOX_NUMBER"),  # p.ej. "whatsapp:+14155238886"
        body=mensaje,
        to=f"whatsapp:+{numero_destino}"
    )
    return msg.sid

def guardar_usuario_temporal(numero):
    """
    Guarda el número de usuario que preguntó por consulta/terapia
    sin realizar compra, para seguimiento a 24h.
    """
    usuarios = []
    if os.path.exists(USUARIOS_TEMP_FILE):
        with open(USUARIOS_TEMP_FILE, "r") as f:
            usuarios = json.load(f)
    if numero not in usuarios:
        usuarios.append(numero)
        with open(USUARIOS_TEMP_FILE, "w") as f:
            json.dump(usuarios, f)

def verificar_conversion(numero):
    """
    Verifica si el usuario ya compró (o agendó) consultando un JSON local.
    """
    if os.path.exists(CONVERSIONES_FILE):
        with open(CONVERSIONES_FILE, "r") as f:
            conversiones = json.load(f)
        return numero in conversiones
    return False

def marcar_conversion(numero):
    """
    Marca que el usuario convirtió (compró o agendó), para no volver a
    enviarle recordatorios.
    """
    conversiones = []
    if os.path.exists(CONVERSIONES_FILE):
        with open(CONVERSIONES_FILE, "r") as f:
            conversiones = json.load(f)
    if numero not in conversiones:
        conversiones.append(numero)
        with open(CONVERSIONES_FILE, "w") as f:
            json.dump(conversiones, f)

