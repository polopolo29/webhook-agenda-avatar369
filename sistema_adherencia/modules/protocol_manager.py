# sistema_adherencia/modules/protocol_manager.py
import re # <-- Añadir esta importación
from .pdf_processor import PDFProcessor

class ProtocolManager:
    def __init__(self, pdf_processor: PDFProcessor):
        self.pdf_processor = pdf_processor

    def generar_paso_1_causa_origen(self, diagnostico):
        """
        PASO 1: Extrae LITERALMENTE la explicación del PDF sobre el origen de la enfermedad.
        """
        causa_texto = self.pdf_processor.get_info(diagnostico, "Causa del Origen")

        if not causa_texto:
            return f"No se encontró información sobre el origen de '{diagnostico}' en nuestra base de conocimiento."

        # Extraer detalles específicos del texto si es posible
        mecanismo = re.search(r"Mecanismo fisiopatológico:(.*?)(?=Factores|$)", causa_texto, re.DOTALL)
        factores = re.search(r"Factores desencadenantes:(.*?)(?=Progresión|$)", causa_texto, re.DOTALL)
        progresion = re.search(r"Progresión documentada:(.*)", causa_texto, re.DOTALL)

        return f"""📖 **PASO 1: CAUSA DEL ORIGEN DE {diagnostico.upper()}**

{causa_texto}

**Base científica (extraída del PDF):**
• **Mecanismo fisiopatológico:** {mecanismo.group(1).strip() if mecanismo else "No especificado."}
• **Factores desencadenantes:** {factores.group(1).strip() if factores else "No especificados."}
• **Progresión documentada:** {progresion.group(1).strip() if progresion else "No especificada."}
"""

    def generar_paso_2_protocolo_espiritual(self):
        """
        PASO 2: Obtiene el protocolo espiritual universal.
        """
        protocolo = self.pdf_processor.get_info("Espiritual Universal", "Descripcion")
        if not protocolo:
            return "No se encontró el protocolo espiritual en nuestra base de conocimiento."

        return f"""🙏 **PASO 2: PROTOCOLO ESPIRITUAL OBLIGATORIO**

{protocolo}
"""

    def generar_paso_3_protocolo_especifico(self, diagnostico):
        """
        PASO 3: Busca en el PDF el protocolo EXACTO para la enfermedad.
        """
        protocolo_texto = self.pdf_processor.get_info(diagnostico, "Protocolo Especifico")
        if not protocolo_texto:
            return f"No se encontró un protocolo específico para '{diagnostico}'."

        return f"""🔬 **PASO 3: PROTOCOLO ESPECÍFICO PARA {diagnostico.upper()}**

{protocolo_texto}
"""

    def generar_paso_4_dieta_personalizada(self, diagnostico, nacionalidad):
        """
        PASO 4: Crea la dieta adaptada a la nacionalidad del paciente.
        """
        dieta_base = self.pdf_processor.get_info(diagnostico, "Dieta Base")
        adaptacion = self.pdf_processor.get_info(nacionalidad, "Adaptacion Dieta")

        if not dieta_base:
            return f"No se encontró una dieta base para '{diagnostico}'."
        if not adaptacion:
            adaptacion = f"No se encontró una adaptación gastronómica específica para '{nacionalidad}'. Se aplicará la dieta base sin modificaciones culturales."

        return f"""🥗 **PASO 4: DIETA PERSONALIZADA PARA {nacionalidad.upper()}**

**Dieta base para {diagnostico}:**
{dieta_base}

**Adaptación para gastronomía {nacionalidad}:**
{adaptacion}
"""

    def generar_paso_5_protocolo_ejercicio(self, diagnostico):
        """
        PASO 5: Protocolo de ejercicio extraído literalmente del PDF.
        """
        ejercicio_texto = self.pdf_processor.get_info(diagnostico, "Protocolo de Ejercicio")
        if not ejercicio_texto:
            return f"No se encontró un protocolo de ejercicio para '{diagnostico}'."

        return f"""💪 **PASO 5: PROTOCOLO DE EJERCICIO PARA {diagnostico.upper()}**

{ejercicio_texto}
"""

    def generar_paso_6_productos_naturales(self, diagnostico):
        """
        PASO 6: Recomienda productos naturales con enlaces, extraídos del PDF.
        """
        productos = self.pdf_processor.get_productos_por_enfermedad(diagnostico)
        if not productos:
            return f"No se encontraron productos naturales recomendados para '{diagnostico}'."

        mensaje = "🌿 **PASO 6: PRODUCTOS NATURALES RECOMENDADOS**\\n"
        for producto in productos:
            mensaje += f"""
**{producto.get('nombre', 'N/A')}**
• **Propiedades:** {producto.get('propiedades', 'No especificado.')}
• **Dosis recomendada:** {producto.get('dosis', 'No especificado.')}
• **Enlace de compra:** {producto.get('enlace_tienda', 'No disponible.')}
• **Evidencia científica:** {producto.get('evidencia_cientifica', 'No especificada.')}
"""
        return mensaje

# --- Bloque de prueba ---
if __name__ == '__main__':
    # Inicializar el procesador de PDF
    pdf_processor = PDFProcessor(pdf_directory='sistema_adherencia/data/pdfs')

    # Inicializar el gestor de protocolos
    protocol_manager = ProtocolManager(pdf_processor)

    # Datos de ejemplo del paciente
    datos_paciente_ejemplo = {
        "diagnostico": "Diabetes",
        "nacionalidad": "Mexicana"
    }

    print("--- INICIANDO PRUEBA DEL GESTOR DE PROTOCOLOS ---")

    # Probar cada paso
    print(protocol_manager.generar_paso_1_causa_origen(datos_paciente_ejemplo["diagnostico"]))
    print("\\n" + "="*50 + "\\n")
    print(protocol_manager.generar_paso_2_protocolo_espiritual())
    print("\\n" + "="*50 + "\\n")
    print(protocol_manager.generar_paso_3_protocolo_especifico(datos_paciente_ejemplo["diagnostico"]))
    print("\\n" + "="*50 + "\\n")
    print(protocol_manager.generar_paso_4_dieta_personalizada(datos_paciente_ejemplo["diagnostico"], datos_paciente_ejemplo["nacionalidad"]))
    print("\\n" + "="*50 + "\\n")
    print(protocol_manager.generar_paso_5_protocolo_ejercicio(datos_paciente_ejemplo["diagnostico"]))
    print("\\n" + "="*50 + "\\n")
    print(protocol_manager.generar_paso_6_productos_naturales(datos_paciente_ejemplo["diagnostico"]))

    print("\\n--- PRUEBA FINALIZADA ---")
