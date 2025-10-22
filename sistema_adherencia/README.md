# Sistema de Adherencia Absoluta al PDF

Este proyecto implementa un sistema de asistente médico virtual que sigue estrictamente la información contenida en una base de conocimiento de archivos PDF.

## Descripción

El sistema guía al usuario a través de un cuestionario detallado y, basándose en las respuestas, genera un protocolo de 6 pasos que se adhiere 100% a la información extraída de los documentos médicos en PDF. El sistema se expone a través de una API RESTful, diseñada para ser consumida por un frontend (por ejemplo, un plugin de WordPress).

---

## Ejecución

1.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Añadir Archivos PDF:**
    Coloca tus archivos PDF médicos dentro del directorio `sistema_adherencia/data/pdfs/`.

3.  **Ejecutar la aplicación:**
    ```bash
    python sistema_adherencia/app.py
    ```
    El servidor se ejecutará en `http://0.0.0.0:5001`.

---

## Formato Requerido para PDFs

Para que el sistema pueda leer y estructurar la información, los PDFs **deben** seguir un formato de marcadores estricto. El sistema busca marcadores con el formato `##CLAVE:VALOR##`.

### Marcadores Primarios
Definen el tema principal del texto que les sigue.
-   `##ENFERMEDAD:Nombre de la Enfermedad##` (Ej: `##ENFERMEDAD:Diabetes##`)
-   `##NACIONALIDAD:Nombre de la Nacionalidad##` (Ej: `##NACIONALIDAD:Mexicana##`)
-   `##PROTOCOLO:Nombre del Protocolo##` (Ej: `##PROTOCOLO:Espiritual Universal##`)

### Marcadores de Sección
Definen una sección de contenido relacionada con el último marcador primario encontrado.
-   `##SECCION:Nombre de la Sección##`

Nombres de sección reconocidos por el sistema para el protocolo:
-   `Causa del Origen`
-   `Protocolo Especifico`
-   `Protocolo de Ejercicio`
-   `Dieta Base`
-   `Productos Naturales`
-   `Adaptacion Dieta`
-   `Descripcion` (para protocolos universales)

### Ejemplo de Estructura en un PDF:

```
##ENFERMEDAD:Diabetes##
##SECCION:Causa del Origen##
La diabetes es una enfermedad metabólica...
Mecanismo fisiopatológico: ...
Factores desencadenantes: ...

##SECCION:Protocolo Especifico##
El protocolo para la diabetes consiste en monitoreo diario...

##NACIONALIDAD:Mexicana##
##SECCION:Adaptacion Dieta##
Se recomienda el consumo de nopales y aguacate...
```

---

## Arquitectura del Proyecto

-   **`app.py`**: El servidor web Flask que expone la API y orquesta todo el flujo.
-   **`modules/pdf_processor.py`**: Módulo central que lee, parsea y estructura la información de todos los archivos PDF.
-   **`modules/questionnaire.py`**: Gestiona el flujo estricto del cuestionario inicial.
-   **`modules/protocol_manager.py`**: Contiene la lógica para generar cada uno de los 6 pasos del protocolo, consultando al `PDFProcessor`.
-   **`modules/persistence.py`**: Maneja el guardado y la recuperación del estado de las sesiones en archivos JSON.
-   **`modules/email_handler.py`**: Formatea y envía (o simula el envío) de los resúmenes de sesión por correo electrónico.
-   **`data/pdfs/`**: Directorio donde se deben colocar los PDFs.
-   **`sessions/`**: Directorio donde se guardan los archivos de sesión de los usuarios.

---

## Uso de la API

### Iniciar una Sesión
-   **Endpoint:** `GET /start`
-   **Respuesta:**
    ```json
    {
      "session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "type": "pregunta",
      "message": "¿Cuál es su nombre completo?"
    }
    ```

### Interactuar con la Sesión
-   **Endpoint:** `POST /interact`
-   **Cuerpo de la Petición:**
    ```json
    {
      "session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "response": "La respuesta del usuario"
    }
    ```
-   **Respuesta (durante el cuestionario):**
    ```json
    {
      "session_id": "...",
      "type": "pregunta",
      "message": "Siguiente pregunta..."
    }
    ```
-   **Respuesta (durante el protocolo):**
    ```json
    {
      "session_id": "...",
      "type": "protocolo",
      "message": "Texto del paso X del protocolo..."
    }
    ```
-   **Respuesta (al finalizar):**
    ```json
    {
      "session_id": "...",
      "type": "final",
      "message": "Hemos completado el protocolo..."
    }
    ```
