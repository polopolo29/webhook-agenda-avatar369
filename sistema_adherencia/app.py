import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from pdf_processor import PDFProcessor
from questionnaire import CuestionarioEstricto
from protocol import ProtocoloMedico
from email_handler import EmailHandlerDetallado

# 1. App Initialization
app = Flask(__name__)
CORS(app) # Allow cross-origin requests from the WordPress plugin

# 2. Load Knowledge Base on Startup
PDF_DIRECTORY = os.path.join(os.path.dirname(__file__), 'data', 'pdfs')
if not os.path.exists(PDF_DIRECTORY):
    os.makedirs(PDF_DIRECTORY)
pdf_processor = PDFProcessor(PDF_DIRECTORY)
print("✅ Base de conocimiento cargada.")
print(pdf_processor.knowledge_base)


# 3. Session Persistence System
SESSIONS_DIR = os.path.join(os.path.dirname(__file__), 'sessions')
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

class SistemaPersistencia:
    def guardar_sesion(self, session_id, datos):
        """Saves the complete session state to a JSON file."""
        filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
        datos["timestamp_ultima_actividad"] = datetime.now().isoformat()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)

    def recuperar_sesion(self, session_id):
        """Recovers a session from a JSON file."""
        filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None # Return None if no session is found

persistence = SistemaPersistencia()

# 4. Main Chat Endpoint
@app.route('/chat', methods=['POST'])
def handle_chat():
    """
    Handles all incoming chat messages, manages session state,
    and returns the system's response.
    """
    data = request.json
    session_id = data.get('session_id')
    user_message = data.get('message')

    if not session_id:
        # Create a new session if no ID is provided
        session_id = f"session_{int(datetime.now().timestamp())}"
        session_data = {
            "session_id": session_id,
            "datos_paciente": {},
            "progreso_cuestionario": 0,
            "protocolo_actual": None,
            "paso_actual": 0,
            "historial_conversacion": []
        }
    else:
        # Retrieve existing session
        session_data = persistence.recuperar_sesion(session_id)
        if not session_data:
            # Handle case where session ID is provided but not found
            return jsonify({"error": "Session not found"}), 404

    # Conversation logic starts here
    response_text = ""

    # Check if the questionnaire is complete
    cuestionario = CuestionarioEstricto(session_data)

    pregunta_actual = cuestionario.obtener_pregunta_actual()

    if pregunta_actual:
        # If the conversation history is empty, it's the first interaction.
        # Just send the first question.
        if not session_data["historial_conversacion"]:
            response_text = pregunta_actual["texto"]
        else:
            # Process the user's answer to the previous question
            response_text, cuestionario_completado = cuestionario.procesar_respuesta(user_message)
            session_data.update(cuestionario.get_session_data())

            if cuestionario_completado:
                session_data["estado_conversacion"] = "protocolo_inicio" # New state

    elif session_data.get("estado_conversacion") == "protocolo_inicio":
        # The user has acknowledged the end of the questionnaire. Start the protocol.
        session_data["estado_conversacion"] = "protocolo_en_curso"
        protocolo = ProtocoloMedico(pdf_processor, session_data)
        response_text, _ = protocolo.ejecutar_paso()
        session_data.update(protocolo.get_session_data())

    elif session_data.get("estado_conversacion") == "protocolo_en_curso":
        # Execute the next step of the protocol
        protocolo = ProtocoloMedico(pdf_processor, session_data)
        response_text, protocolo_completado = protocolo.ejecutar_paso()
        session_data.update(protocolo.get_session_data())
        if protocolo_completado:
            session_data["estado_conversacion"] = "finalizado"
            # Send the summary email
            email_handler = EmailHandlerDetallado()
            email_handler.enviar_email(session_data)

    else:
        # Fallback for any other state
        response_text = "Por favor, inicie una nueva sesión."

    # Update and save session
    session_data["historial_conversacion"].append({"user": user_message, "bot": response_text})
    persistence.guardar_sesion(session_id, session_data)

    return jsonify({
        "session_id": session_id,
        "response": response_text
    })

# 5. PDF Upload Endpoint
@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'pdf_file' not in request.files:
        return "No file part", 400

    file = request.files['pdf_file']

    if file.filename == '':
        return "No selected file", 400

    if file and file.filename.endswith('.pdf'):
        filename = file.filename # In a real app, you'd secure the filename
        filepath = os.path.join(PDF_DIRECTORY, filename)
        file.save(filepath)

        # Reload the knowledge base
        global pdf_processor
        pdf_processor = PDFProcessor(PDF_DIRECTORY)
        print("✅ Base de conocimiento actualizada.")

        return "File uploaded successfully", 200

    return "Invalid file type", 400

# 6. Health Check Endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200


if __name__ == '__main__':
    # Running in debug mode is not suitable for production
    # Use Gunicorn or another WSGI server for deployment
    app.run(host='0.0.0.0', port=5000, debug=True)
