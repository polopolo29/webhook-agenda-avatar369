import os
import requests

class ViatorClient:
    """
    Un cliente para interactuar con la API de Viator (TripAdvisor).
    Gestiona la autenticación y proporciona métodos para buscar tours
    y actividades.
    """
    def __init__(self, api_key=None):
        """
        Inicializa el cliente de Viator.
        La clave de API se leerá de la variable de entorno VIATOR_API_KEY.
        """
        self.api_key = api_key or os.environ.get('VIATOR_API_KEY')
        self.base_url = "https://api.viator.com/partner"

        if not self.api_key:
            raise ValueError("La clave de API de Viator (VIATOR_API_KEY) no fue proporcionada.")

    def get_api_headers(self):
        """
        Prepara los encabezados para las llamadas a la API de Viator.
        """
        headers = {
            'exp-api-key': self.api_key,
            'Accept-Language': 'es-MX', # Localización para el mercado mexicano
            'Accept': 'application/json;version=2.0'
        }
        return headers

    def search_products(self, destination_name, currency='EUR'):
        """
        Busca productos (tours) en un destino específico.

        :param destination_name: El nombre del destino a buscar (ej. 'Paris').
        :param currency: La moneda para los precios.
        :return: Un diccionario con la respuesta de la API de Viator o None si hay un error.
        """
        search_url = f"{self.base_url}/search/products"

        # El endpoint de búsqueda de Viator es un POST request con un cuerpo JSON
        payload = {
            "filtering": {
                "destination": destination_name
            },
            "pagination": {
                "start": 1,
                "count": 10
            },
            "currency": currency
        }

        try:
            headers = self.get_api_headers()
            response = requests.post(search_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al buscar productos en Viator: {e}")
            if e.response:
                print(f"Detalles del error de la API: {e.response.text}")
            return None

    def book_product(self, product_code, travel_date, currency, travelers, booker_info):
        """
        Reserva un producto (tour/actividad) usando el endpoint /booking/book de Viator.

        :param product_code: El código del producto a reservar.
        :param travel_date: La fecha del viaje en formato 'YYYY-MM-DD'.
        :param currency: La moneda para la transacción.
        :param travelers: Una lista de diccionarios con los detalles de los viajeros.
        :param booker_info: Un diccionario con los datos del titular de la reserva.
        :return: Un diccionario con la confirmación de la reserva o None si hay un error.
        """
        booking_url = f"{self.base_url}/booking/book"

        payload = {
            "currency": currency,
            "booker": booker_info,
            "items": [
                {
                    "productCode": product_code,
                    "travelDate": travel_date,
                    "paxMix": travelers
                }
            ]
        }

        try:
            headers = self.get_api_headers()
            response = requests.post(booking_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al reservar el producto en Viator: {e}")
            if e.response:
                print(f"Detalles del error de la API: {e.response.text}")
            return None

# Ejemplo de uso (esto no se ejecutará directamente, es para demostración)
if __name__ == '__main__':
    # Para probar este script, necesitarías definir la variable de entorno:
    # export VIATOR_API_KEY='TU_API_KEY'
    print("Inicializando cliente de Viator (ejemplo)...")
    try:
        client = ViatorClient()
        print("Buscando productos para 'Mexico City'...")
        products = client.search_products(destination_name="Mexico City")
        if products:
            print("Búsqueda exitosa. Productos encontrados:")
            print(products)
        else:
            print("La búsqueda no arrojó resultados o hubo un error.")

    except ValueError as e:
        print(e)
        print("Por favor, asegúrate de configurar la variable de entorno VIATOR_API_KEY.")
