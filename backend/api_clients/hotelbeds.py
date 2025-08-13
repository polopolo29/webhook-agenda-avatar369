import os
import time
import hashlib
import requests

class HotelbedsClient:
    """
    Un cliente para interactuar con la API de Hotelbeds.
    Gestiona la autenticación (basada en firma) y proporciona métodos
    para buscar y reservar hoteles.
    """
    def __init__(self, api_key=None, secret=None):
        """
        Inicializa el cliente de Hotelbeds.
        Las credenciales se leerán de las variables de entorno
        HOTELBEDS_API_KEY y HOTELBEDS_SECRET.
        """
        self.api_key = api_key or os.environ.get('HOTELBEDS_API_KEY')
        self.secret = secret or os.environ.get('HOTELBEDS_SECRET')

        # Hotelbeds tiene un endpoint para API-Audits y otro para Bookings
        self.base_url = "https://api.test.hotelbeds.com"

        if not self.api_key or not self.secret:
            raise ValueError("Las credenciales de Hotelbeds (api_key, secret) no fueron proporcionadas.")

    def _generate_signature(self):
        """
        Genera la firma X-Signature requerida por la API de Hotelbeds.
        La firma es un hash SHA256 de: apiKey + secret + timestamp.
        """
        utc_timestamp = int(time.time())
        signature_str = f"{self.api_key}{self.secret}{utc_timestamp}"

        # Se usa hashlib para crear el hash SHA256
        signature_hash = hashlib.sha256(signature_str.encode('utf-8')).hexdigest()

        return signature_hash, utc_timestamp

    def get_api_headers(self):
        """
        Prepara los encabezados de autorización para las llamadas a la API.
        """
        signature, timestamp = self._generate_signature()

        headers = {
            'Api-key': self.api_key,
            'X-Signature': signature,
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json'
        }
        return headers

    def search_hotels(self, stay, occupancies, geolocation=None):
        """
        Busca disponibilidad de hoteles usando el endpoint /hotels de Hotelbeds.

        :param stay: Un diccionario con 'checkIn' y 'checkOut' en formato 'YYYY-MM-DD'.
        :param occupancies: Una lista de diccionarios, cada uno representando una habitación
                            con 'rooms', 'adults' y 'children'.
        :param geolocation: Un diccionario con 'latitude', 'longitude' y 'radius'.
        :return: Un diccionario con la respuesta de la API de Hotelbeds o None si hay un error.
        """
        search_url = f"{self.base_url}/hotel-api/1.0/hotels"

        payload = {
            "stay": stay,
            "occupancies": occupancies
        }
        if geolocation:
            payload['geolocation'] = geolocation

        try:
            headers = self.get_api_headers()
            response = requests.post(search_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al buscar hoteles: {e}")
            if e.response:
                # Imprimir el cuerpo del error de la API si está disponible
                print(f"Detalles del error de la API: {e.response.text}")
            return None

    def book_hotel(self, rate_key, rooms, holder_info):
        """
        Confirma una reserva de hotel usando el endpoint /bookings de Hotelbeds.

        :param rate_key: La clave de la tarifa obtenida en la búsqueda.
        :param rooms: Una lista de diccionarios con los detalles de los paxes por habitación.
        :param holder_info: Un diccionario con los datos del titular de la reserva.
        :return: Un diccionario con la confirmación de la reserva o None si hay un error.
        """
        booking_url = f"{self.base_url}/hotel-api/1.0/bookings"

        # Un identificador único para esta reserva del lado del cliente
        client_reference = f"ViajesWeb-{int(time.time())}"

        payload = {
            "holder": holder_info,
            "rooms": rooms,
            "clientReference": client_reference,
            "rateKey": rate_key
        }

        try:
            headers = self.get_api_headers()
            response = requests.post(booking_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al reservar el hotel: {e}")
            if e.response:
                print(f"Detalles del error de la API: {e.response.text}")
            return None

# Ejemplo de uso (esto no se ejecutará directamente, es para demostración)
if __name__ == '__main__':
    # Para probar este script, necesitarías definir las variables de entorno:
    # export HOTELBEDS_API_KEY='TU_API_KEY'
    # export HOTELBEDS_SECRET='TU_SECRET'
    print("Inicializando cliente de Hotelbeds (ejemplo)...")
    try:
        client = HotelbedsClient()
        headers = client.get_api_headers()
        print("Encabezados de API de Hotelbeds listos para usar:")
        print(headers)
    except ValueError as e:
        print(e)
        print("Por favor, asegúrate de configurar las variables de entorno HOTELBEDS_API_KEY y HOTELBEDS_SECRET.")
