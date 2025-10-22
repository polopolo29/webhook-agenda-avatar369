# create_pdfs.py
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
import textwrap

# Contenido estructurado para los PDFs
CONTENIDO = {
    "base_conocimiento.pdf": """
##ENFERMEDAD:Diabetes##
##SECCION:Causa del Origen##
La diabetes mellitus tipo 2 es una enfermedad metabólica caracterizada por altos niveles de glucosa en la sangre.
Mecanismo fisiopatológico: Resistencia a la insulina y deficiencia relativa de insulina.
Factores desencadenantes: Genética, obesidad, sedentarismo y dieta inadecuada.
Progresión documentada: La enfermedad progresa desde una fase de prediabetes hasta una diabetes establecida con posibles complicaciones a largo plazo.

##ENFERMEDAD:Hipertension##
##SECCION:Causa del Origen##
La hipertensión arterial es una condición en la que la fuerza de la sangre contra las paredes de las arterias es consistentemente demasiado alta.
Mecanismo fisiopatológico: Aumento del gasto cardíaco o de la resistencia vascular periférica.
Factores desencadenantes: Dieta alta in sodio, estrés, genética, obesidad y consumo de alcohol.
Progresión documentada: Si no se trata, puede llevar a enfermedades cardíacas, accidentes cerebrovasculares y daño renal.
    """,
    "protocolos.pdf": """
##PROTOCOLO:Espiritual Universal##
##SECCION:Descripcion##
Este protocolo está diseñado para conectar con el bienestar interior y reducir el estrés.
Video obligatorio: https://www.youtube.com/watch?v=video_espiritual
Instrucciones literales: Siéntese en un lugar tranquilo, cierre los ojos y concéntrese en su respiración durante 30 minutos exactos.
Frecuencia definida: Diaria, preferiblemente por la mañana.

##ENFERMEDAD:Diabetes##
##SECCION:Protocolo Especifico##
Procedimiento documentado: Monitoreo diario de glucosa, administración de metformina según prescripción, y seguimiento de la dieta recomendada.
Duración del tratamiento: Crónico, de por vida.
Frecuencia: El monitoreo debe ser 3 veces al día.
Precauciones: Estar atento a signos de hipoglucemia como mareos o sudoración.
Evidencia del PDF: Estudio controlado aleatorizado (RCT) publicado en The Lancet, 2021.

##ENFERMEDAD:Diabetes##
##SECCION:Protocolo de Ejercicio##
Tipo de ejercicio: Caminata a paso ligero o ciclismo.
Intensidad: Moderada, sin llegar a la fatiga extrema.
Duración: 30 minutos.
Frecuencia: 5 días a la semana.
Ejercicios detallados: 10 minutos de calentamiento, 15 minutos de caminata a 5 km/h, 5 minutos de enfriamiento.
Precauciones importantes: Medir la glucosa antes y después del ejercicio. No inyectar insulina en músculos que se van a ejercitar.
    """,
    "dietas_y_productos.pdf": """
##ENFERMEDAD:Diabetes##
##SECCION:Dieta Base##
Dieta baja en carbohidratos simples y alta en fibra. Se deben evitar azúcares refinados, bebidas azucaradas y alimentos procesados.
Horarios y porciones: 5 comidas pequeñas al día para mantener estables los niveles de glucosa.

##NACIONALIDAD:Mexicana##
##SECCION:Adaptacion Dieta##
Alimentos recomendados: Nopales, aguacate, frijoles negros, pollo a la plancha.
Alimentos a evitar: Tortillas de harina, refrescos, pan dulce.
Preparaciones típicas: Tacos de nopal en lugar de tortilla de maíz, caldos de pollo sin arroz.

##ENFERMEDAD:Diabetes##
##SECCION:Productos Naturales##
Producto: Canela de Ceylán
Propiedades: Ayuda a regular los niveles de glucosa en sangre.
Dosis recomendada: 1 cucharadita al día.
Enlace de compra: https://tienda.example.com/canela
Evidencia científica: Múltiples estudios sugieren un efecto moderado en la reducción de la glucosa en ayunas.

Producto: Berberina
Propiedades: Mejora la sensibilidad a la insulina.
Dosis recomendada: 500 mg antes de cada comida.
Enlace de compra: https://tienda.example.com/berberina
Evidencia científica: Metaanálisis de 14 estudios demostró eficacia similar a la metformina.
    """
}

def create_pdf(file_path, content):
    """Crea un archivo PDF con el contenido proporcionado."""
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    styles = getSampleStyleSheet()
    style = styles['Normal']
    style.fontSize = 10

    # Corregido: Dividir por el carácter de nueva línea real
    lines = content.strip().split('\\n')
    y = height - 40
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Envolvemos el texto para que quepa en el ancho de la página
        # Usamos un Paragraph para un mejor manejo del texto
        p = Paragraph(line.replace('  ', ' '), style) # Normalizamos espacios
        p_width, p_height = p.wrapOn(c, width - 80, height)
        if y < p_height + 40:
            c.showPage()
            y = height - 40
        p.drawOn(c, 40, y)
        y -= p_height + 6 # Espacio entre párrafos

    c.save()
    print(f"PDF creado: {file_path}")

def main():
    """Función principal para generar todos los PDFs."""
    pdf_dir = os.path.join("sistema_adherencia", "data", "pdfs")
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    for filename, content in CONTENIDO.items():
        file_path = os.path.join(pdf_dir, filename)
        create_pdf(file_path, content)

if __name__ == "__main__":
    main()
