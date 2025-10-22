# Asistente Médico PDF - Sistema de Adherencia y Consulta

Este proyecto es un sistema de asistente médico virtual diseñado para guiar a los pacientes a través de un cuestionario detallado y un protocolo médico de 6 pasos. La lógica del sistema se basa al 100% en el contenido de una base de conocimiento de documentos PDF.

El sistema se compone de dos partes principales:
1.  **Backend Flask**: Una aplicación Python que maneja la lógica de la conversación, el procesamiento de PDFs y la persistencia de las sesiones.
2.  **Plugin de WordPress**: Un plugin que proporciona una interfaz de chat frontend y un panel de administración para subir nuevos PDFs.

## Requisitos Previos

- Python 3.8 o superior
- `pip` y `virtualenv`
- Un sitio de WordPress con permisos de administrador
- Acceso a la línea de comandos en el servidor donde se ejecutará el backend

## Guía de Instalación y Ejecución

Sigue estos pasos para poner en marcha el sistema completo.

### 1. Configuración del Backend

Primero, clona el repositorio y configura el entorno de Python.

```bash
# 1. Clona el repositorio (si aún no lo has hecho)
git clone <url-del-repositorio>
cd <nombre-del-repositorio>

# 2. Crea y activa un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows, usa `venv\\Scripts\\activate`

# 3. Instala las dependencias de Python
pip install -r sistema_adherencia/requirements.txt
```

### 2. Ejecutar el Servidor Backend

El backend debe estar ejecutándose de forma continua para que el chat funcione.

-   **Para desarrollo (con recarga automática):**
    ```bash
    python sistema_adherencia/app.py
    ```
    El servidor se ejecutará en `http://127.0.0.1:5000`.

-   **Para producción (24/7 y estable):**
    Recomendamos usar el script `run.sh` que utiliza Gunicorn, un servidor WSGI de nivel de producción.
    ```bash
    # Asegúrate de que el script sea ejecutable
    chmod +x run.sh

    # Ejecuta el servidor
    ./run.sh
    ```
    Esto iniciará el servidor en segundo plano, asegurando que permanezca activo incluso si cierras la terminal.

### 3. Empaquetar e Instalar el Plugin de WordPress

Para instalar el plugin en tu sitio de WordPress, primero debes empaquetarlo en un archivo `.zip`.

```bash
# Desde la raíz del proyecto, ejecuta este comando:
zip -r wordpress-plugin.zip wordpress-plugin/
```

Esto creará un archivo `wordpress-plugin.zip`. Ahora, sigue estos pasos en tu panel de administración de WordPress:

1.  Ve a **Plugins > Añadir nuevo**.
2.  Haz clic en **Subir Plugin**.
3.  Selecciona el archivo `wordpress-plugin.zip` que acabas de crear y haz clic en **Instalar ahora**.
4.  Una vez instalado, haz clic en **Activar Plugin**.

### 4. Usar el Asistente

-   **Chat**: Para añadir el chat a cualquier página o entrada, simplemente añade el shortcode `[asistente_medico_pdf]`.
-   **Subir PDFs**: En el menú de administración de WordPress, ve a la nueva sección **Asistente PDF** para subir nuevos documentos a la base de conocimiento. El backend los cargará automáticamente.

## Estructura del Proyecto

```
.
├── sistema_adherencia/         # Backend de Flask
│   ├── data/pdfs/              # PDFs de conocimiento
│   ├── sessions/               # Archivos de sesión de chat
│   ├── sent_emails/            # Emails de resumen (simulados)
│   ├── app.py                  # Servidor principal
│   ├── pdf_processor.py        # Lógica de carga de PDFs
│   ├── questionnaire.py        # Lógica del cuestionario
│   ├── protocol.py             # Lógica del protocolo de 6 pasos
│   ├── email_handler.py        # Lógica de envío de emails
│   └── requirements.txt        # Dependencias de Python
│
├── wordpress-plugin/           # Frontend de WordPress
│   ├── css/chat-style.css
│   ├── js/chat.js
│   └── asistente-medico-pdf.php
│
├── run.sh                      # Script para producción
└── README.md                   # Esta guía
```
