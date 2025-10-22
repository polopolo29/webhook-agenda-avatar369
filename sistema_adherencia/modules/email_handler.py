# sistema_adherencia/modules/email_handler.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailHandlerDetallado:
    def __init__(self):
        # --- CONFIGURACIÓN SMTP ---
        # Reemplazar con las credenciales reales de un servidor de correo (ej. Gmail, SendGrid, etc.)
        # NOTA: Para Gmail, puede ser necesario crear una "Contraseña de aplicación".
        self.SMTP_SERVER = "smtp.example.com"
        self.SMTP_PORT = 587
        self.SMTP_USERNAME = "tu_email@example.com"
        self.SMTP_PASSWORD = "tu_contraseña"
        self.SENDER_EMAIL = "tu_email@example.com"

    def generar_detalle_protocolo(self, historial_protocolo):
        """Formatea la sección del protocolo para el email."""
        if not historial_protocolo:
            return "No se ha generado ningún paso del protocolo aún."

        detalle = ""
        for i, paso_texto in enumerate(historial_protocolo):
            detalle += f"--- PASO {i+1} ---\\n{paso_texto}\\n\\n"
        return detalle

    def generar_email_sesion(self, datos_sesion):
        """
        Genera el contenido completo (asunto y cuerpo) del email con TODOS los detalles de la sesión.
        """
        paciente = datos_sesion.get("datos_paciente", {})

        asunto = f"📄 Resumen Sesión Médica AvatarMX - {datetime.now().strftime('%Y-%m-%d')}"

        cuerpo = f"""
Hola {paciente.get("nombre", "Paciente")},

Este es un resumen detallado de tu sesión con el Asistente Médico AvatarMX.

👤 **INFORMACIÓN DEL PACIENTE:**
• **Nombre:** {paciente.get("nombre", "No proporcionado")}
• **Edad:** {paciente.get("edad", "No proporcionado")}
• **Nacionalidad:** {paciente.get("nacionalidad", "No proporcionado")}

🏥 **EVALUACIÓN MÉDICA:**
• **Diagnóstico:** {paciente.get("diagnostico", "No proporcionado")}
• **Síntomas iniciales:** {paciente.get("sintomas_iniciales", "No proporcionado")}
• **Síntomas actuales:** {paciente.get("sintomas_actuales", "No proporcionado")}
• **Medicamentos:** {paciente.get("medicamentos", "No proporcionado")}

📋 **PROTOCOLO APLICADO:**
{self.generar_detalle_protocolo(datos_sesion.get("historial_protocolo", []))}

🔗 **ENLACE PARA CONTINUAR TU SESIÓN:**
Para continuar donde te quedaste, puedes usar el siguiente enlace (funcionalidad a implementar en el frontend):
/continuar-sesion?id={datos_sesion.get("session_id", "N/A")}

---
Este es un correo automático. Por favor, no respondas a este mensaje.
"""
        return asunto, cuerpo

    def enviar_email(self, destinatario, asunto, cuerpo):
        """
        Envía el correo electrónico usando la configuración SMTP.
        """
        if self.SMTP_SERVER == "smtp.example.com":
            print("--- SIMULACIÓN DE ENVÍO DE CORREO ---")
            print(f"Destinatario: {destinatario}")
            print(f"Asunto: {asunto}")
            print("--- CUERPO ---")
            print(cuerpo)
            print("---------------------------------------")
            return True, "Simulación exitosa. Configura tus credenciales SMTP para envío real."

        try:
            message = MIMEMultipart()
            message["From"] = self.SENDER_EMAIL
            message["To"] = destinatario
            message["Subject"] = asunto
            message.attach(MIMEText(cuerpo, "plain"))

            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                server.starttls()
                server.login(self.SMTP_USERNAME, self.SMTP_PASSWORD)
                server.sendmail(self.SENDER_EMAIL, destinatario, message.as_string())

            return True, "Correo enviado exitosamente."
        except Exception as e:
            return False, f"Error al enviar el correo: {e}"

# --- Bloque de prueba ---
if __name__ == '__main__':
    handler = EmailHandlerDetallado()

    # Datos de sesión de ejemplo
    sesion_ejemplo = {
        "session_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "datos_paciente": {
            "nombre": "Elena Morales",
            "edad": "52",
            "nacionalidad": "Española",
            "diagnostico": "Hipertension",
            "sintomas_iniciales": "Dolores de cabeza y mareos",
            "sintomas_actuales": "Presión arterial alta persistente",
            "medicamentos": "Lisinopril",
            "email": "elena.morales@example.com"
        },
        "historial_protocolo": [
            "📖 **PASO 1: CAUSA DEL ORIGEN DE HIPERTENSION...**",
            "🙏 **PASO 2: PROTOCOLO ESPIRITUAL OBLIGATORIO...**"
        ]
    }

    asunto, cuerpo = handler.generar_email_sesion(sesion_ejemplo)

    # Simular el envío
    success, message = handler.enviar_email(sesion_ejemplo["datos_paciente"]["email"], asunto, cuerpo)

    print(f"Resultado del envío: {message}")
    assert success is True
