# sistema_adherencia/modules/pdf_processor.py
import os
import re
from pypdf import PdfReader

class PDFProcessor:
    def __init__(self, pdf_directory="sistema_adherencia/data/pdfs"):
        self.pdf_directory = pdf_directory
        self.knowledge_base = self._load_and_process_pdfs()

    def _load_and_process_pdfs(self):
        """Escanea el directorio, lee todos los PDFs y los procesa."""
        knowledge = {}
        if not os.path.isdir(self.pdf_directory):
            print(f"Error: El directorio '{self.pdf_directory}' no fue encontrado.")
            return knowledge

        for filename in sorted(os.listdir(self.pdf_directory)):
            if filename.endswith(".pdf"):
                file_path = os.path.join(self.pdf_directory, filename)
                print(f"Procesando PDF: {file_path}")
                text = self._extract_text_from_pdf(file_path)
                self._parse_text_with_robust_regex(text, knowledge)
        return knowledge

    def _extract_text_from_pdf(self, file_path):
        """Extrae el texto de un único archivo PDF y lo normaliza."""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += (page.extract_text() or "")
            # Normalizar: reemplazar saltos de línea y múltiples espacios por uno solo
            return re.sub(r'\\s+', ' ', text).strip()
        except Exception as e:
            print(f"Error al leer el PDF {file_path}: {e}")
            return ""

    def _parse_text_with_robust_regex(self, text, knowledge):
        """
        Analiza el texto usando una expresión regular robusta que no depende de saltos de línea.
        """
        pattern = r"##([\w\s]+):([\w\s]+)##(.*?)(?=##|$)"
        matches = re.findall(pattern, text, re.DOTALL)

        current_primary_key = None
        for match in matches:
            marker_type, marker_value, content = [item.strip() for item in match]

            # --- CORRECCIÓN CLAVE ---
            # Normalizar el valor del marcador para eliminar saltos de línea y espacios extra
            marker_value_normalized = ' '.join(marker_value.split())

            primary_markers = ["ENFERMEDAD", "NACIONALIDAD", "PROTOCOLO"]
            if marker_type in primary_markers:
                current_primary_key = marker_value_normalized
                if current_primary_key not in knowledge:
                    knowledge[current_primary_key] = {}
                if content:
                    knowledge[current_primary_key]['descripcion_general'] = content
            elif marker_type == "SECCION" and current_primary_key:
                section_name = marker_value_normalized
                knowledge[current_primary_key][section_name] = content

    def get_info(self, primary_key, section):
        """Obtiene información literal de la base de conocimiento."""
        return self.knowledge_base.get(primary_key, {}).get(section, None)

    def get_productos_por_enfermedad(self, enfermedad):
        """Devuelve una lista de productos naturales para una enfermedad."""
        raw_text = self.get_info(enfermedad, "Productos Naturales")
        if not raw_text:
            return []

        productos = []
        bloques_producto = re.split(r"Producto:", raw_text, flags=re.IGNORECASE)[1:]

        for bloque in bloques_producto:
            producto = {}
            nombre_match = re.search(r"^(.*?)Propiedades:", bloque, re.DOTALL)
            propiedades_match = re.search(r"Propiedades:(.*?)Dosis recomendada:", bloque, re.DOTALL)
            dosis_match = re.search(r"Dosis recomendada:(.*?)Enlace de compra:", bloque, re.DOTALL)
            enlace_match = re.search(r"Enlace de compra:(.*?)Evidencia científica:", bloque, re.DOTALL)
            evidencia_match = re.search(r"Evidencia científica:(.*)", bloque, re.DOTALL)

            if nombre_match: producto['nombre'] = nombre_match.group(1).strip()
            if propiedades_match: producto['propiedades'] = propiedades_match.group(1).strip()
            if dosis_match: producto['dosis'] = dosis_match.group(1).strip()
            if enlace_match: producto['enlace_tienda'] = enlace_match.group(1).strip()
            if evidencia_match: producto['evidencia_cientifica'] = evidencia_match.group(1).strip()

            if producto.get('nombre'):
                productos.append(producto)
        return productos

# Bloque de prueba
if __name__ == '__main__':
    processor = PDFProcessor()

    print("\\n--- Base de Conocimiento Cargada (Corregida) ---")
    import json
    print(json.dumps(processor.knowledge_base, indent=2, ensure_ascii=False))
