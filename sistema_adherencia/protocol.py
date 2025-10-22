

class ProtocoloMedico:
    def __init__(self, pdf_processor, session_data):
        self.pdf_processor = pdf_processor
        self.session_data = session_data
        self.paso_actual = session_data.get("paso_actual", 1)

    def ejecutar_paso(self):
        """
        Executes the current step of the protocol and returns the response.
        """
        if self.paso_actual == 1:
            return self.generar_causa_origen()
        elif self.paso_actual == 2:
            return self.ejecutar_protocolo_espiritual()
        elif self.paso_actual == 3:
            return self.obtener_protocolo_especifico()
        elif self.paso_actual == 4:
            return self.crear_dieta_personalizada()
        elif self.paso_actual == 5:
            return self.generar_protocolo_ejercicio()
        elif self.paso_actual == 6:
            return self.recomendar_productos_naturales()
        else:
            return "Has completado el protocolo. Pronto recibirás un resumen por correo.", True

    def generar_causa_origen(self):
        diagnostico = self.session_data.get("datos_paciente", {}).get("primer_diagnostico", "su condición").strip()
        # Attempt to find the specific disease section first, fallback to general
        causa = self.pdf_processor.get_knowledge(diagnostico, "Causa del Origen")

        response = f"📖 **PASO 1: CAUSA DEL ORIGEN DE {diagnostico.upper()}**\n\n"
        response += f"Según nuestra base de conocimiento, la causa del origen de {diagnostico} es la siguiente:\n\n"
        response += f"_{causa}_\n\n"
        response += "¿Está completamente clara esta información sobre el origen? Por favor, responda 'sí' para continuar."

        self.paso_actual += 1
        return response, False

    def ejecutar_protocolo_espiritual(self):
        # The spiritual protocol is universal, so we look for it in a "General" category
        protocolo = self.pdf_processor.get_knowledge("General", "Protocolo Espiritual")
        response = f"**PASO 2: PROTOCOLO ESPIRITUAL**\n\n"
        response += "Este es un protocolo universal que cada paciente debe seguir para apoyar su bienestar general.\n\n"
        response += f"{protocolo}\n\n"
        response += "Por favor, tómese un momento para revisar y comprender este paso. Responda 'sí' para continuar."
        self.paso_actual += 1
        return response, False

    def obtener_protocolo_especifico(self):
        diagnostico = self.session_data.get("datos_paciente", {}).get("primer_diagnostico", "su condición").strip()
        protocolo = self.pdf_processor.get_knowledge(diagnostico, "Protocolo Especifico")

        response = f"🔬 **PASO 3: PROTOCOLO ESPECÍFICO PARA {diagnostico.upper()}**\n\n"
        response += "A continuación se detalla el protocolo documentado para su condición:\n\n"
        response += f"{protocolo}\n\n"
        response += "Responda 'sí' para avanzar al siguiente paso."
        self.paso_actual += 1
        return response, False

    def crear_dieta_personalizada(self):
        diagnostico = self.session_data.get("datos_paciente", {}).get("primer_diagnostico", "su condición").strip()
        nacionalidad = self.session_data.get("datos_paciente", {}).get("nacionalidad", "su nacionalidad").strip()

        # Get the base diet for the disease
        dieta_base = self.pdf_processor.get_knowledge(diagnostico, "Dieta Base")
        # Get the specific adaptation for the nationality
        adaptacion = self.pdf_processor.get_knowledge(nacionalidad, "Adaptacion Gastronomica")

        response = f"🥗 **PASO 4: DIETA PERSONALIZADA PARA {nacionalidad.upper()}**\n\n"
        response += f"**Dieta base para {diagnostico}:**\n{dieta_base}\n\n"
        response += f"**Adaptación para la gastronomía de {nacionalidad}:**\n{adaptacion}\n\n"
        response += "Responda 'sí' para continuar."
        self.paso_actual += 1
        return response, False

    def generar_protocolo_ejercicio(self):
        diagnostico = self.session_data.get("datos_paciente", {}).get("primer_diagnostico", "su condición").strip()
        ejercicio = self.pdf_processor.get_knowledge(diagnostico, "Protocolo de Ejercicio")

        response = f"💪 **PASO 5: PROTOCOLO DE EJERCICIO PARA {diagnostico.upper()}**\n\n"
        response += "El ejercicio es una parte fundamental del tratamiento. Aquí está su protocolo:\n\n"
        response += f"{ejercicio}\n\n"
        response += "Responda 'sí' para ver la recomendación final."
        self.paso_actual += 1
        return response, False

    def recomendar_productos_naturales(self):
        diagnostico = self.session_data.get("datos_paciente", {}).get("primer_diagnostico", "su condición").strip()
        productos = self.pdf_processor.get_knowledge(diagnostico, "Productos Naturales Recomendados")

        response = f"🌿 **PASO 6: PRODUCTOS NATURALES RECOMENDADOS**\n\n"
        response += "Estos productos naturales han sido recomendados para apoyar su tratamiento:\n\n"
        response += f"{productos}\n\n"
        response += "Hemos llegado al final del protocolo. Recibirá un resumen completo por correo electrónico en breve."
        self.paso_actual += 1
        return response, True # Final step

    def get_session_data(self):
        """Returns the updated session data to be saved."""
        self.session_data["paso_actual"] = self.paso_actual
        return self.session_data
