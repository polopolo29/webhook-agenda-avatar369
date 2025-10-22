
class CuestionarioEstricto:
    preguntas = [
        {"numero": 1, "texto": "¿Cuál es su nombre?", "campo": "nombre", "obligatoria": True},
        {"numero": 2, "texto": "¿Cuál es su edad?", "campo": "edad", "validacion": "rango_1_120"},
        {"numero": 3, "texto": "¿Cuál es su estatura y peso?", "campo": "estatura_peso"},
        {"numero": 4, "texto": "¿Cuál es su nacionalidad?", "campo": "nacionalidad"},
        {"numero": 5, "texto": "¿Cuáles fueron los síntomas la primera vez que tuvo malestar?", "campo": "sintomas_iniciales"},
        {"numero": 6, "texto": "¿Cuál fue su primer diagnóstico y cuánto tiempo tiene con él?", "campo": "primer_diagnostico"},
        {"numero": 7, "texto": "¿Cuáles son sus síntomas actualmente?", "campo": "sintomas_actuales"},
        {"numero": 8, "texto": "¿Actualmente está consumiendo medicamentos?", "campo": "consume_medicamentos", "tipo": "booleano"},
        {"numero": 9, "texto": "¿Qué medicamentos?", "campo": "medicamentos", "condicion": ("consume_medicamentos", True)},
        {"numero": 10, "texto": "En su dieta cotidiana, ¿consume cerdo, trigo, arroz, aceite vegetal, alcohol, tabaco, azúcar o café?", "campo": "dieta_actual"},
    ]

    def __init__(self, session_data):
        self.datos_paciente = session_data.get("datos_paciente", {})
        self.progreso = session_data.get("progreso_cuestionario", 0)

    def obtener_pregunta_actual(self):
        """
        Returns the current question based on the progress, skipping conditional questions.
        """
        if self.progreso >= len(self.preguntas):
            return None # Questionnaire complete

        pregunta = self.preguntas[self.progreso]

        # Skip conditional questions if the condition is not met
        if "condicion" in pregunta:
            campo_condicion, valor_esperado = pregunta["condicion"]
            if self.datos_paciente.get(campo_condicion) != valor_esperado:
                self.progreso += 1
                return self.obtener_pregunta_actual() # Recursively find the next valid question

        return pregunta

    def procesar_respuesta(self, respuesta):
        """
        Processes the user's response, validates it, saves it, and returns the next question.
        """
        pregunta_actual = self.obtener_pregunta_actual()

        if not pregunta_actual:
            return "Cuestionario completado. Ahora comenzaremos con el protocolo.", True

        # Basic validation: ensure mandatory questions are answered
        if pregunta_actual.get("obligatoria") and (not respuesta or not respuesta.strip()):
            return f"Por favor, responda la pregunta para continuar: {pregunta_actual['texto']}", False

        # Save the answer
        campo = pregunta_actual["campo"]
        if pregunta_actual.get("tipo") == "booleano":
            # Simple "si" or "no" check
            respuesta_bool = "si" in respuesta.lower()
            self.datos_paciente[campo] = respuesta_bool
        else:
            self.datos_paciente[campo] = respuesta.strip()

        # Advance to the next question
        self.progreso += 1

        siguiente_pregunta = self.obtener_pregunta_actual()

        if not siguiente_pregunta:
            return "Ha completado el cuestionario. Por favor, responda 'sí' para comenzar con el protocolo de 6 pasos.", True

        return siguiente_pregunta["texto"], False

    def get_session_data(self):
        """Returns the updated session data to be saved."""
        return {
            "datos_paciente": self.datos_paciente,
            "progreso_cuestionario": self.progreso,
        }
