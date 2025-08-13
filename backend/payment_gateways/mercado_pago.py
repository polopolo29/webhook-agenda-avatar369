import os
import requests
import json

class MercadoPagoClient:
    """
    Un cliente para interactuar con la API de Mercado Pago.
    Gestiona la creación de preferencias de pago.
    """
    def __init__(self, access_token=None):
        """
        Inicializa el cliente de Mercado Pago.
        El token de acceso se leerá de la variable de entorno MERCADOPAGO_ACCESS_TOKEN.
        """
        self.access_token = access_token or os.environ.get('MERCADOPAGO_ACCESS_TOKEN')
        self.base_url = "https://api.mercadopago.com"

        if not self.access_token:
            raise ValueError("El token de acceso de Mercado Pago no fue proporcionado.")

    def get_api_headers(self):
        """
        Prepara los encabezados de autorización para las llamadas a la API.
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        return headers

    def create_preference(self, items, back_urls, payer_info=None):
        """
        Crea una preferencia de pago en Mercado Pago.

        :param items: Una lista de diccionarios, cada uno representando un item a pagar.
                      Ej: [{'title': 'Paquete a Cancún', 'quantity': 1, 'unit_price': 1500.50}]
        :param back_urls: Un diccionario con las URLs de retorno (success, failure, pending).
        :param payer_info: Un diccionario con información del pagador (opcional).
        :return: Un diccionario con la respuesta de la API de Mercado Pago o None si hay un error.
        """
        preference_url = f"{self.base_url}/checkout/preferences"

        payload = {
            "items": items,
            "back_urls": back_urls,
            "auto_return": "approved" # Redirige automáticamente solo en caso de pago aprobado.
        }
        if payer_info:
            payload['payer'] = payer_info

        try:
            headers = self.get_api_headers()
            response = requests.post(preference_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al crear la preferencia de pago en Mercado Pago: {e}")
            if e.response:
                print(f"Detalles del error de la API: {e.response.text}")
            return None

# Ejemplo de uso (esto no se ejecutará directamente, es para demostración)
if __name__ == '__main__':
    # Para probar este script, necesitarías definir la variable de entorno:
    # export MERCADOPAGO_ACCESS_TOKEN='TU_ACCESS_TOKEN'
    print("Inicializando cliente de Mercado Pago (ejemplo)...")
    try:
        client = MercadoPagoClient()

        # Datos de ejemplo para una preferencia
        sample_items = [
            {
                "title": "Viaje a Europa",
                "quantity": 2,
                "unit_price": 25000.00,
                "currency_id": "MXN"
            }
        ]
        sample_urls = {
            "success": "https://www.tu-sitio.com/pago_exitoso",
            "failure": "https://www.tu-sitio.com/pago_fallido",
            "pending": "https://www.tu-sitio.com/pago_pendiente"
        }

        print("Creando preferencia de pago...")
        preference = client.create_preference(items=sample_items, back_urls=sample_urls)

        if preference:
            print("Preferencia creada con éxito:")
            print(f"  ID de Preferencia: {preference.get('id')}")
            print(f"  URL de pago (init_point): {preference.get('init_point')}")
        else:
            print("No se pudo crear la preferencia.")

    except ValueError as e:
        print(e)
        print("Por favor, asegúrate de configurar la variable de entorno MERCADOPAGO_ACCESS_TOKEN.")
