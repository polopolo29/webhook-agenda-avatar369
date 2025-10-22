# sistema_adherencia/modules/questionnaire.py

class CuestionarioEstricto:
    """
    Gestiona el flujo estricto del cuestionario, una pregunta a la vez.
    """
    def __init__(self):
        self.preguntas = [
            {"numero": 1, "texto": "¿Cuál es su nombre completo?", "campo": "nombre", "obligatoria": True},
            {"numero": 2, "texto": "¿Cuál es su edad?", "campo": "edad", "obligatoria": True, "validacion": "numero"},
            {"numero": 3, "texto": "¿Cuál es su nacionalidad? (Ej: Mexicana, Española, etc.)", "campo": "nacionalidad", "obligatoria": True},
            {"numero": 4, "texto": "¿Cuál es el diagnóstico médico principal que le han dado?", "campo": "diagnostico", "obligatoria": True},
            {"numero": 5, "texto": "Describa brevemente sus síntomas iniciales.", "campo": "sintomas_iniciales", "obligatoria": True},
            {"numero": 6, "texto": "Describa sus síntomas actuales.", "campo": "sintomas_actuales", "obligatoria": True},
            {"numero": 7, "texto": "Por favor, liste los medicamentos que está tomando actualmente. Si no toma ninguno, escriba 'Ninguno'.", "campo": "medicamentos", "obligatoria": True},
            {"numero": 8, "texto": "Describa su dieta actual de un día típico.", "campo": "dieta_actual", "obligatoria": True},
            {"numero": 9, "texto": "¿Cuál es su nivel de condición física? (Ej: Sedentario, Ligero, Moderado, Activo)", "campo": "condicion_fisica", "obligatoria": True},
            {"numero": 10, "texto": "¿Cuál es su correo electrónico para enviarle el resumen de la sesión?", "campo": "email", "obligatoria": True, "validacion": "email"}
        ]
        self.datos_paciente = {}
        self.progreso = 0  # Índice de la pregunta actual

    def obtener_pregunta_actual(self):
        """Devuelve la pregunta actual o None si el cuestionario ha terminado."""
        if self.progreso < len(self.preguntas):
            return self.preguntas[self.progreso]
        return None

    def procesar_respuesta(self, respuesta):
        """
        Procesa la respuesta del usuario, la valida y avanza a la siguiente pregunta.
        Devuelve la siguiente pregunta o un mensaje de error.
        """
        pregunta_actual = self.obtener_pregunta_actual()
        if not pregunta_actual:
            return None # Cuestionario ya completado

        # Validación simple
        if pregunta_actual["obligatoria"] and (not respuesta or not respuesta.strip()):
            return f"Por favor, responde la pregunta para continuar. {pregunta_actual['texto']}"

        # Guardar la respuesta
        campo = pregunta_actual["campo"]
        self.datos_paciente[campo] = respuesta.strip()

        # Avanzar a la siguiente pregunta
        self.progreso += 1

        return self.obtener_pregunta_actual()

    def esta_completo(self):
        """Verifica si el cuestionario ha sido completado."""
        return self.progreso >= len(self.preguntas)

# Ejemplo de uso
if __name__ == '__main__':
    cuestionario = CuestionarioEstricto()

    # Simular una conversación
    pregunta = cuestionario.obtener_pregunta_actual()
    print(f"Asistente: {pregunta['texto']}")

    respuesta_usuario = "Juan Pérez"
    print(f"Usuario: {respuesta_usuario}")
    pregunta = cuestionario.procesar_respuesta(respuesta_usuario)
    print(f"Asistente: {pregunta['texto']}")

    respuesta_usuario = "45"
    print(f"Usuario: {respuesta_usuario}")
    pregunta = cuestionario.procesar_respuesta(respuesta_usuario)
    print(f"Asistente: {pregunta['texto']}")

    # Simular respuesta vacía
    respuesta_usuario = ""
    print(f"Usuario: {respuesta_usuario}")
    error_o_pregunta = cuestionario.procesar_respuesta(respuesta_usuario)
    print(f"Asistente: {error_o_pregunta}")
