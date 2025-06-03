# chatbot_agent.py

import os

# Si defines OPENAI_API_KEY en .env, usarás OpenAI; de lo contrario, solo reglas
USE_OPENAI = bool(os.getenv("OPENAI_API_KEY"))

if USE_OPENAI:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")

def responder_con_ia(texto_usuario, numero):
    """
    Usa OpenAI (si tienes clave) o reglas simples para generar respuesta.
    """
    texto = texto_usuario.lower()
    # Reglas básicas gratuitas
    if "precio" in texto or "costo" in texto:
        return (
            "Nuestro tratamiento de 3 sesiones cuesta $XXX MXN. "
            "Puedes usar el cupón '3terapias' en: "
            "https://avatarmexchange.com/product/tratamiento-completo-3-cesiones/?currency=mxn"
        )
    if "método" in texto or "cómo funciona" in texto or "qué es" in texto:
        return (
            "Nuestros métodos siguen un protocolo cuántico y científico. "
            "Mira esto para entender cómo devolverá tu salud: https://www.instagram.com/p/C9fNSX8s6Rp/"
        )
    # Si tienes OpenAI, delega a GPT-3.5
    if USE_OPENAI:
        prompt = (
            f"Eres un asistente de ventas de AvatarM Exchange, una clínica de sanación cuántica. "
            f"El usuario dice: \"{texto_usuario}\". Responde de manera empática, científica y "
            f"guía al usuario hacia la conversión (venta de terapia o curso). Máximo 120 palabras.\n"
            "- Terapia 3 sesiones: https://avatarmexchange.com/product/tratamiento-completo-3-cesiones/\n"
            "- Terapia individual: https://avatarmexchange.com/product/terapia-online/\n"
            "- E-book: https://avatarmexchange.com/product/el-meteto-la-cura-y-sanacion-a-toda-enfermedad/\n"
            "- Curso online: https://avatarmexchange.com/product/medicina-de-quinta-dimension/\n"
            "- Videos IG: https://www.instagram.com/p/C9fNSX8s6Rp/ y https://www.instagram.com/p/C8jBPP0osN-/\n"
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    # Respuesta por defecto
    return (
        "¡Buen día! Somos AvatarM Exchange, clínica de sanación cuántica. "
        "¿En qué puedo ayudarte hoy?"
    )

