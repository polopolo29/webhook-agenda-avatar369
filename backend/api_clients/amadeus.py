import os
import requests

class AmadeusClient:
    """
    Un cliente para interactuar con la API Self-Service de Amadeus.
    Gestiona la autenticación (obtención de token de acceso) y proporciona
    métodos para realizar llamadas a los endpoints de la API de Amadeus.
    """
    def __init__(self, client_id=None, client_secret=None):
        """
        Inicializa el cliente de Amadeus.
        Las credenciales se pueden pasar directamente o se leerán de las
        variables de entorno AMADEUS_CLIENT_ID y AMADEUS_CLIENT_SECRET.
        """
        self.client_id = client_id or os.environ.get('AMADEUS_CLIENT_ID')
        self.client_secret = client_secret or os.environ.get('AMADEUS_CLIENT_SECRET')

        # El entorno 'test' usa un endpoint diferente al de 'production'
        self.base_url = "https://test.api.amadeus.com"

        if not self.client_id or not self.client_secret:
            raise ValueError("Las credenciales de cliente (client_id, client_secret) no fueron proporcionadas.")

        self._access_token = None

    def _get_access_token(self):
        """
        Obtiene un token de acceso OAuth2 de Amadeus.
        El token se almacena en caché en la instancia para reutilizarlo en
        llamadas posteriores hasta que expire.
        """
        auth_url = f"{self.base_url}/v1/security/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            response = requests.post(auth_url, headers=headers, data=data)
            response.raise_for_status()  # Lanza una excepción para respuestas de error (4xx o 5xx)
            self._access_token = response.json()['access_token']
            print("Token de acceso de Amadeus obtenido con éxito.")
            return self._access_token
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener el token de acceso de Amadeus: {e}")
            # En una aplicación real, aquí se manejaría el error de forma más robusta.
            return None

    def get_api_headers(self):
        """
        Prepara los encabezados de autorización para las llamadas a la API.
        Si no hay un token, intenta obtener uno nuevo.
        """
        if not self._access_token:
            self._get_access_token()

        if self._access_token:
            return {
                "Authorization": f"Bearer {self._access_token}"
            }
        else:
            raise RuntimeError("No se pudo obtener el token de acceso de Amadeus.")

    def search_flights(self, origin, destination, departure_date, adults=1, return_date=None, currency='EUR'):
        """
        Busca ofertas de vuelos utilizando el endpoint 'Flight Offers Search' de Amadeus.

        :param origin: Código IATA de la ciudad de origen (ej. 'MAD').
        :param destination: Código IATA de la ciudad de destino (ej. 'MEX').
        :param departure_date: Fecha de salida en formato 'YYYY-MM-DD'.
        :param adults: Número de pasajeros adultos.
        :param return_date: Fecha de regreso en formato 'YYYY-MM-DD' (opcional, para vuelos de ida y vuelta).
        :param currency: Código de moneda para los precios (ej. 'EUR', 'MXN').
        :return: Un diccionario con la respuesta de la API de Amadeus o None si hay un error.
        """
        search_url = f"{self.base_url}/v2/shopping/flight-offers"

        params = {
            'originLocationCode': origin,
            'destinationLocationCode': destination,
            'departureDate': departure_date,
            'adults': adults,
            'currencyCode': currency,
            'max': 10  # Limitar el número de resultados para empezar
        }
        if return_date:
            params['returnDate'] = return_date

        try:
            headers = self.get_api_headers()
            response = requests.get(search_url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, RuntimeError) as e:
            print(f"Error al buscar vuelos: {e}")
            return None

    def book_flight(self, flight_offer, travelers):
        """
        Reserva un vuelo utilizando el endpoint 'Flight Create Orders' de Amadeus.

        :param flight_offer: El objeto de oferta de vuelo obtenido de search_flights.
        :param travelers: Una lista de diccionarios con la información de los viajeros.
        :return: Un diccionario con la confirmación de la reserva o None si hay un error.
        """
        booking_url = f"{self.base_url}/v1/booking/flight-orders"

        payload = {
            "data": {
                "type": "flight-order",
                "flightOffers": [flight_offer],
                "travelers": travelers
            }
        }

        try:
            headers = self.get_api_headers()
            response = requests.post(booking_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, RuntimeError) as e:
            print(f"Error al reservar el vuelo: {e}")
            if e.response:
                print(f"Detalles del error de la API: {e.response.text}")
            return None

# Ejemplo de uso (esto no se ejecutará directamente, es para demostración)
if __name__ == '__main__':
    # Para probar este script, necesitarías definir las variables de entorno:
    # export AMADEUS_CLIENT_ID='TU_CLIENT_ID'
    # export AMADEUS_CLIENT_SECRET='TU_CLIENT_SECRET'
    print("Inicializando cliente de Amadeus (ejemplo)...")
    try:
        client = AmadeusClient()
        headers = client.get_api_headers()
        print("Encabezados de API listos para usar:")
        print(headers)
    except (ValueError, RuntimeError) as e:
        print(e)
        print("Por favor, asegúrate de configurar las variables de entorno AMADEUS_CLIENT_ID y AMADEUS_CLIENT_SECRET.")
