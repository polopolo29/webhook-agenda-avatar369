import os
from datetime import datetime

class EmailHandlerDetallado:
    def generar_detalle_protocolo(self, protocolo):
        # This is a placeholder. In a real implementation, this would format
        # the specific steps taken from the session data.
        return "Protocolo detallado aplicado durante la sesión."

    def generar_link_unico(self, session_id):
        # In a real app, this would be a proper URL to the chat page.
        return f"http://your-wordpress-site.com/chat?session_id={session_id}"

    def generar_email_sesion(self, sesion):
        """
        Genera el contenido del email con todos los detalles de la sesión.
        """
        # Ensure all keys exist, providing default values if they don't
        paciente = sesion.get("datos_paciente", {})
        nombre = paciente.get("nombre", "N/A")
        edad = paciente.get("edad", "N/A")
        nacionalidad = paciente.get("nacionalidad", "N/A")

        diagnostico = paciente.get("primer_diagnostico", "N/A")
        sintomas_iniciales = paciente.get("sintomas_iniciales", "N/A")
        sintomas_actuales = paciente.get("sintomas_actuales", "N/A")
        medicamentos = paciente.get("medicamentos", "N/A")

        # In a real scenario, these would be populated during the protocol
        dieta_personalizada = "Dieta detallada aquí."
        protocolo_ejercicio = "Protocolo de ejercicio detallado aquí."
        productos_recomendados = "Productos naturales recomendados aquí."
        proxima_sesion = "Fecha recomendada para la próxima sesión."

        asunto = f"📄 Resumen Sesión Médica AvatarMX - {datetime.now().strftime('%Y-%m-%d')}"

        cuerpo_html = f"""
        <html>
        <body>
            <h2>Resumen de tu Sesión Médica</h2>

            <h3>👤 INFORMACIÓN DEL PACIENTE</h3>
            <ul>
                <li><strong>Nombre:</strong> {nombre}</li>
                <li><strong>Edad:</strong> {edad}</li>
                <li><strong>Nacionalidad:</strong> {nacionalidad}</li>
            </ul>

            <h3>🏥 EVALUACIÓN MÉDICA</h3>
            <ul>
                <li><strong>Diagnóstico:</strong> {diagnostico}</li>
                <li><strong>Síntomas iniciales:</strong> {sintomas_iniciales}</li>
                <li><strong>Síntomas actuales:</strong> {sintomas_actuales}</li>
                <li><strong>Medicamentos:</strong> {medicamentos}</li>
            </ul>

            <h3>📋 PROTOCOLO APLICADO</h3>
            <p>{self.generar_detalle_protocolo(sesion.get("protocolo_actual"))}</p>

            <h3>🥗 DIETA RECOMENDADA</h3>
            <p>{dieta_personalizada}</p>

            <h3>💪 EJERCICIO PRESCRITO</h3>
            <p>{protocolo_ejercicio}</p>

            <h3>🌿 PRODUCTOS NATURALES</h3>
            <p>{productos_recomendados}</p>

            <hr>

            <p>
                <strong>🔗 ENLACE PARA CONTINUAR:</strong>
                <a href="{self.generar_link_unico(sesion.get('session_id'))}">Haz clic aquí</a>
            </p>
            <p><strong>⏰ PRÓXIMA SESIÓN RECOMENDADA:</strong> {proxima_sesion}</p>
        </body>
        </html>
        """
        return asunto, cuerpo_html

    def enviar_email(self, sesion):
        """
        Simulates sending the email by saving it as an HTML file.
        """
        asunto, cuerpo_html = self.generar_email_sesion(sesion)

        # Create a directory for emails if it doesn't exist
        emails_dir = os.path.join(os.path.dirname(__file__), 'sent_emails')
        if not os.path.exists(emails_dir):
            os.makedirs(emails_dir)

        # Filename based on session ID and timestamp
        filename = f"{sesion.get('session_id')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
        filepath = os.path.join(emails_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"<h1>{asunto}</h1>\n{cuerpo_html}")
            print(f"✅ Email simulado y guardado en: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error al guardar el email simulado: {e}")
            return False
