# sistema_adherencia/test_suite.py
import unittest
import os
import json
import shutil
import sys

# Añadir la ruta del proyecto para poder importar los módulos
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from modules.pdf_processor import PDFProcessor
from modules.questionnaire import CuestionarioEstricto
from modules.protocol_manager import ProtocolManager
from modules.persistence import SistemaPersistencia

class TestSistemaAdherencia(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Se ejecuta una vez antes de todas las pruebas."""
        print("Configurando el entorno de prueba...")

        # --- CORRECCIÓN DE RUTA ---
        # Construir rutas absolutas basadas en la ubicación de este script
        cls.base_dir = os.path.dirname(os.path.abspath(__file__))
        cls.test_pdf_dir = os.path.join(cls.base_dir, "test_data", "pdfs")
        cls.test_sessions_dir = os.path.join(cls.base_dir, "test_data", "sessions")
        cls.source_pdf_dir = os.path.join(cls.base_dir, "data", "pdfs")

        # Crear directorios de prueba
        os.makedirs(cls.test_pdf_dir, exist_ok=True)
        os.makedirs(cls.test_sessions_dir, exist_ok=True)

        # Copiar los PDFs de muestra al directorio de prueba
        shutil.copytree(cls.source_pdf_dir, cls.test_pdf_dir, dirs_exist_ok=True)

        # Inicializar los módulos con las rutas de prueba
        cls.pdf_processor = PDFProcessor(pdf_directory=cls.test_pdf_dir)
        cls.protocol_manager = ProtocolManager(cls.pdf_processor)
        cls.persistence = SistemaPersistencia(session_dir=cls.test_sessions_dir)

    @classmethod
    def tearDownClass(cls):
        """Se ejecuta una vez después de todas las pruebas."""
        print("Limpiando el entorno de prueba...")
        shutil.rmtree(os.path.join(cls.base_dir, "test_data"))

    def test_1_pdf_processor(self):
        """Prueba que el PDFProcessor cargue y estructure los datos correctamente."""
        print("Ejecutando prueba: PDF Processor")
        causa_diabetes = self.pdf_processor.get_info("Diabetes", "Causa del Origen")
        self.assertIsNotNone(causa_diabetes)
        self.assertIn("Resistencia a la insulina", causa_diabetes)

        productos = self.pdf_processor.get_productos_por_enfermedad("Diabetes")
        self.assertEqual(len(productos), 2)
        self.assertEqual(productos[0]['nombre'], 'Canela de Ceylán')

    def test_2_questionnaire(self):
        """Prueba el flujo del CuestionarioEstricto."""
        print("Ejecutando prueba: Cuestionario")
        cuestionario = CuestionarioEstricto()
        self.assertEqual(cuestionario.obtener_pregunta_actual()['numero'], 1)

        cuestionario.procesar_respuesta("Test User")
        self.assertEqual(cuestionario.progreso, 1)

        resultado = cuestionario.procesar_respuesta("")
        self.assertIn("Por favor, responde", resultado)
        self.assertEqual(cuestionario.progreso, 1)

        for _ in range(1, len(cuestionario.preguntas)):
            cuestionario.procesar_respuesta("Dato de prueba")

        self.assertTrue(cuestionario.esta_completo())

    def test_3_protocol_manager(self):
        """Prueba que el ProtocolManager genere todos los pasos correctamente."""
        print("Ejecutando prueba: Protocol Manager")
        diagnostico = "Diabetes"

        paso1 = self.protocol_manager.generar_paso_1_causa_origen(diagnostico)
        self.assertIn("CAUSA DEL ORIGEN DE DIABETES", paso1)

        paso3 = self.protocol_manager.generar_paso_3_protocolo_especifico(diagnostico)
        self.assertIn("PROTOCOLO ESPECÍFICO PARA DIABETES", paso3)

        paso_fail = self.protocol_manager.generar_paso_3_protocolo_especifico("Enfermedad Inventada")
        self.assertIn("No se encontró un protocolo", paso_fail)

    def test_4_persistence(self):
        """Prueba el ciclo de vida de una sesión en SistemaPersistencia."""
        print("Ejecutando prueba: Persistencia")
        sesion = self.persistence.nueva_sesion()
        session_id = sesion['session_id']
        self.assertIsNotNone(session_id)

        sesion['datos_paciente']['nombre'] = 'Test Persistence'
        self.persistence.guardar_sesion(session_id, sesion)

        sesion_recuperada = self.persistence.recuperar_sesion(session_id)
        self.assertEqual(sesion_recuperada['datos_paciente']['nombre'], 'Test Persistence')

        self.assertTrue(self.persistence.eliminar_sesion(session_id))
        self.assertIsNone(self.persistence.recuperar_sesion(session_id))

if __name__ == '__main__':
    unittest.main(verbosity=2)
