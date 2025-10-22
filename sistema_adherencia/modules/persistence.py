# sistema_adherencia/modules/persistence.py
import json
import os
from datetime import datetime
import uuid

class SistemaPersistencia:
    def __init__(self, session_dir="sistema_adherencia/sessions"):
        self.session_dir = session_dir
        if not os.path.exists(self.session_dir):
            os.makedirs(self.session_dir)

    def _get_session_filepath(self, session_id):
        """Construye la ruta al archivo de la sesión."""
        return os.path.join(self.session_dir, f"session_{session_id}.json")

    def nueva_sesion(self):
        """Crea una nueva sesión con un ID único."""
        session_id = str(uuid.uuid4())
        # Datos iniciales de la sesión, incluyendo el progreso del protocolo
        datos_sesion = {
            "session_id": session_id,
            "datos_paciente": {},
            "progreso_cuestionario": 0,
            "paso_protocolo_actual": 0, # Para rastrear en qué paso del protocolo se encuentra
            "historial_protocolo": [], # Para almacenar los textos generados de cada paso
            "timestamp_inicio": datetime.now().isoformat(),
            "timestamp_ultima_actividad": datetime.now().isoformat()
        }
        self.guardar_sesion(session_id, datos_sesion)
        return datos_sesion

    def guardar_sesion(self, session_id, datos_sesion):
        """
        Guarda CADA detalle de la sesión en un archivo JSON.
        """
        datos_sesion["timestamp_ultima_actividad"] = datetime.now().isoformat()
        filepath = self._get_session_filepath(session_id)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(datos_sesion, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar la sesión {session_id}: {e}")

    def recuperar_sesion(self, session_id):
        """
        Recupera EXACTAMENTE donde el paciente se quedó, cargando el archivo JSON.
        """
        filepath = self._get_session_filepath(session_id)
        if not os.path.exists(filepath):
            return None # La sesión no existe

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al recuperar la sesión {session_id}: {e}")
            return None

    def eliminar_sesion(self, session_id):
        """
        Elimina el archivo de sesión si el paciente lo solicita explícitamente.
        """
        filepath = self._get_session_filepath(session_id)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"Sesión {session_id} eliminada.")
                return True
            except Exception as e:
                print(f"Error al eliminar la sesión {session_id}: {e}")
                return False
        return False

# --- Bloque de prueba ---
if __name__ == '__main__':
    persistencia = SistemaPersistencia()

    print("--- Probando creación y guardado de sesión ---")
    nueva_sesion = persistencia.nueva_sesion()
    session_id = nueva_sesion["session_id"]
    print(f"Nueva sesión creada con ID: {session_id}")

    # Simular progreso
    nueva_sesion["datos_paciente"]["nombre"] = "Maria Rodriguez"
    nueva_sesion["progreso_cuestionario"] = 2
    nueva_sesion["paso_protocolo_actual"] = 1
    nueva_sesion["historial_protocolo"].append("Texto del Paso 1 generado aquí...")

    persistencia.guardar_sesion(session_id, nueva_sesion)
    print("Sesión actualizada y guardada.")

    print("\\n--- Probando recuperación de sesión ---")
    sesion_recuperada = persistencia.recuperar_sesion(session_id)

    if sesion_recuperada:
        print("Sesión recuperada exitosamente:")
        print(json.dumps(sesion_recuperada, indent=2))
        assert sesion_recuperada["datos_paciente"]["nombre"] == "Maria Rodriguez"
        assert sesion_recuperada["paso_protocolo_actual"] == 1
    else:
        print("Fallo al recuperar la sesión.")

    print("\\n--- Probando eliminación de sesión ---")
    if persistencia.eliminar_sesion(session_id):
        sesion_post_eliminacion = persistencia.recuperar_sesion(session_id)
        assert sesion_post_eliminacion is None
        print("La sesión ya no existe, como se esperaba.")

    print("\\n--- PRUEBA FINALIZADA ---")
