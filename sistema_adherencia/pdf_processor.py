import os
import PyPDF2
import re

class PDFProcessor:
    def __init__(self, pdfs_directory):
        self.pdfs_directory = pdfs_directory
        self.knowledge_base = self._load_and_process_pdfs()

    def _load_and_process_pdfs(self):
        """
        Loads all PDF files from the specified directory and processes them
        to build the knowledge base.
        """
        knowledge_base = {}
        for filename in os.listdir(self.pdfs_directory):
            if filename.endswith(".pdf"):
                filepath = os.path.join(self.pdfs_directory, filename)
                try:
                    content = self._extract_text_from_pdf(filepath)
                    self._parse_and_structure_content(content, knowledge_base)
                except Exception as e:
                    print(f"Error processing PDF {filename}: {e}")
        return knowledge_base

    def _extract_text_from_pdf(self, pdf_path):
        """
        Extracts all text content from a PDF file.
        """
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            full_content = ""
            for page in pdf_reader.pages:
                full_content += page.extract_text() + "\n"
        return full_content

    def _parse_and_structure_content(self, content, knowledge_base):
        """
        Parses the raw text content using ## markers and structures it
        into the knowledge base.
        """
        # Simple parsing logic based on markers like ##ENFERMEDAD:Diabetes##
        # and ##SECCION:Causa del Origen##. This needs to be very robust.
        # This is a placeholder for the detailed parsing logic.

        # Example of how it might be structured
        # This regex will find all sections and their content, robust to whitespace
        pattern = re.compile(r"##([\w\s_:]+)##\s*(.*?)(?=\s*##|$)", re.DOTALL)
        matches = pattern.findall(content)

        current_disease = None

        for match in matches:
            header, text_content = match
            header = header.strip()
            text_content = text_content.strip()

            if header.startswith("ENFERMEDAD:"):
                current_disease = header.replace("ENFERMEDAD:", "").strip()
                if current_disease not in knowledge_base:
                    knowledge_base[current_disease] = {}
            elif header.startswith("SECCION:") and current_disease:
                section_name = header.replace("SECCION:", "").strip()
                knowledge_base[current_disease][section_name] = text_content


    def get_knowledge(self, disease, section):
        """
        Retrieves a specific piece of information from the knowledge base.
        """
        return self.knowledge_base.get(disease, {}).get(section, "Información no encontrada.")

# Example usage (for testing purposes)
if __name__ == '__main__':
    # This part will only run when the script is executed directly
    # Create a dummy PDF for testing
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    # Corrected path for the dummy PDF
    dummy_pdf_dir = "sistema_adherencia/data/pdfs"
    os.makedirs(dummy_pdf_dir, exist_ok=True)
    dummy_pdf_path = os.path.join(dummy_pdf_dir, "conocimiento_medico.pdf")

    c = canvas.Canvas(dummy_pdf_path, pagesize=letter)
    # Use TextObject for more realistic line breaks
    text = c.beginText(72, 800)
    text.textLine("##ENFERMEDAD:Diabetes##")
    text.textLine("##SECCION:Causa del Origen##")
    text.textLine("La diabetes tipo 2 es causada por una combinación de factores genéticos y de estilo de vida.")
    text.textLine("##SECCION:Protocolo Especifico##")
    text.textLine("1. Monitoreo de glucosa. 2. Administración de insulina. 3. Control de dieta.")
    text.textLine("##SECCION:Dieta Base##")
    text.textLine("Dieta baja en carbohidratos y azúcares refinados.")
    text.textLine("##SECCION:Protocolo de Ejercicio##")
    text.textLine("30 minutos de ejercicio aeróbico, 5 días a la semana.")
    text.textLine("##SECCION:Productos Naturales Recomendados##")
    text.textLine("Canela en polvo (1g al día). Enlace: https://tienda.com/canela")

    text.textLine("##ENFERMEDAD:General##")
    text.textLine("##SECCION:Protocolo Espiritual##")
    text.textLine("Meditación de 15 minutos por la mañana.")

    text.textLine("##ENFERMEDAD:Mexicana##")
    text.textLine("##SECCION:Adaptacion Gastronomica##")
    text.textLine("Evitar tortillas de harina. Preferir nopales y aguacate.")

    c.drawText(text)
    c.save()

    processor = PDFProcessor(pdfs_directory=dummy_pdf_dir)
    print("Base de conocimiento cargada:")
    print(processor.knowledge_base)

    print("\nRecuperando información específica:")
    causa_diabetes = processor.get_knowledge("Diabetes", "Causa del Origen")
    print(f"Causa de la Diabetes: {causa_diabetes}")

    protocolo_espiritual = processor.get_knowledge("Diabetes", "Protocolo Espiritual")
    print(f"Protocolo Espiritual: {protocolo_espiritual}")
