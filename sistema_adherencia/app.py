# sistema_adherencia/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS # Importar CORS
import os

# Importar todos nuestros módulos
from modules.pdf_processor import PDFProcessor
from modules.questionnaire import CuestionarioEstricto
from modules.protocol_manager import ProtocolManager
from modules.persistence import SistemaPersistencia
from modules.email_handler import EmailHandlerDetallado

app = Flask(__name__)
CORS(app) # Habilitar CORS para toda la aplicación

# --- INICIALIZACIÓN SINGLETON ---
print("Iniciando el sistema...")
base_dir = os.path.dirname(os.path.abspath(__file__))
pdf_dir = os.path.join(base_dir, "data", "pdfs")
sessions_dir = os.path.join(base_dir, "sessions")

print(f"Directorio de PDFs: {pdf_dir}")
print(f"Directorio de Sesiones: {sessions_dir}")

pdf_processor = PDFProcessor(pdf_directory=pdf_dir)
protocol_manager = ProtocolManager(pdf_processor)
persistence = SistemaPersistencia(session_dir=sessions_dir)
email_handler = EmailHandlerDetallado()
print("Sistema inicializado y listo.")

# --- RUTAS DE LA API ---

@app.route('/start', methods=['GET'])
def start_session():
    """
    Endpoint para iniciar una nueva conversación.
    Crea una nueva sesión y devuelve la primera pregunta.
    """
    session_data = persistence.nueva_sesion()
    session_id = session_data['session_id']

    cuestionario = CuestionarioEstricto()
    primera_pregunta = cuestionario.obtener_pregunta_actual()

    session_data['progreso_cuestionario'] = cuestionario.progreso
    persistence.guardar_sesion(session_id, session_data)

    return jsonify({
        "session_id": session_id,
        "type": "pregunta",
        "message": primera_pregunta['texto']
    })

@app.route('/interact', methods=['POST'])
def interact():
    """
    Endpoint principal para la interacción.
    Maneja las respuestas del usuario y avanza el flujo.
    """
    data = request.json
    session_id = data.get('session_id')
    user_response = data.get('response')

    if not session_id:
        return jsonify({"error": "session_id es requerido"}), 400

    session_data = persistence.recuperar_sesion(session_id)
    if not session_data:
        return jsonify({"error": "Sesión no encontrada o inválida"}), 404

    if session_data['paso_protocolo_actual'] == 0:
        cuestionario = CuestionarioEstricto()
        cuestionario.progreso = session_data['progreso_cuestionario']
        cuestionario.datos_paciente = session_data['datos_paciente']

        resultado = cuestionario.procesar_respuesta(user_response)

        session_data['progreso_cuestionario'] = cuestionario.progreso
        session_data['datos_paciente'] = cuestionario.datos_paciente
        persistence.guardar_sesion(session_id, session_data)

        if isinstance(resultado, str):
            return jsonify({"session_id": session_id, "type": "pregunta", "message": resultado})

        if resultado is not None:
            return jsonify({"session_id": session_id, "type": "pregunta", "message": resultado['texto']})

        session_data['paso_protocolo_actual'] = 1
        persistence.guardar_sesion(session_id, session_data)

    paso_actual = session_data['paso_protocolo_actual']
    datos_paciente = session_data['datos_paciente']
    diagnostico = datos_paciente.get("diagnostico", "Desconocido")
    nacionalidad = datos_paciente.get("nacionalidad", "Desconocida")

    response_message = ""
    if paso_actual == 1:
        response_message = protocol_manager.generar_paso_1_causa_origen(diagnostico)
    elif paso_actual == 2:
        response_message = protocol_manager.generar_paso_2_protocolo_espiritual()
    elif paso_actual == 3:
        response_message = protocol_manager.generar_paso_3_protocolo_especifico(diagnostico)
    elif paso_actual == 4:
        response_message = protocol_manager.generar_paso_4_dieta_personalizada(diagnostico, nacionalidad)
    elif paso_actual == 5:
        response_message = protocol_manager.generar_paso_5_protocolo_ejercicio(diagnostico)
    elif paso_actual == 6:
        response_message = protocol_manager.generar_paso_6_productos_naturales(diagnostico)

    if paso_actual <= 6:
        session_data['historial_protocolo'].append(response_message)

    session_data['paso_protocolo_actual'] += 1
    persistence.guardar_sesion(session_id, session_data)

    if paso_actual > 6:
        email_destinatario = datos_paciente.get("email")
        if email_destinatario:
            asunto, cuerpo = email_handler.generar_email_sesion(session_data)
            email_handler.enviar_email(email_destinatario, asunto, cuerpo)

        return jsonify({
            "session_id": session_id,
            "type": "final",
            "message": "Hemos completado el protocolo. Se ha enviado un resumen detallado a su correo electrónico. Gracias."
        })

    return jsonify({
        "session_id": session_id,
        "type": "protocolo",
        "message": response_message
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
