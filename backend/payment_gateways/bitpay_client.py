import os
from bitpay_sdk import Client as BitPaySdkClient
from bitpay_sdk.exceptions.bitpay_exception import BitPayException

class BitPayClient:
    """
    Un cliente para interactuar con la API de BitPay.
    Gestiona la creación de facturas para pagos con criptomonedas.
    """
    def __init__(self, api_token=None):
        """
        Inicializa el cliente de BitPay.
        El token de API se leerá de la variable de entorno BITPAY_API_TOKEN.
        Este token se obtiene tras un proceso de 'pairing' con el servidor de BitPay.
        """
        self.api_token = api_token or os.environ.get('BITPAY_API_TOKEN')

        if not self.api_token:
            raise ValueError("El token de API de BitPay (BITPAY_API_TOKEN) no fue proporcionado.")

        # El cliente de BitPay se inicializa para el entorno de producción o de prueba.
        # Usaremos el de prueba (Testnet) para el desarrollo.
        self.client = BitPaySdkClient(
            api_uri="https://test.bitpay.com",
            tokens={'merchant': self.api_token}
        )

    def create_invoice(self, price, currency, order_id):
        """
        Crea una factura en BitPay.

        :param price: El monto a cobrar en la moneda especificada.
        :param currency: El código de la moneda fiat (ej. 'EUR', 'MXN', 'USD').
        :param order_id: Un ID de orden único de nuestro sistema.
        :return: Un objeto Invoice de BitPay o None si hay un error.
        """
        params = {
            "price": price,
            "currency": currency,
            "orderId": order_id,
            "redirectURL": f"https://www.tu-sitio.com/pago_exitoso?orderId={order_id}",
            "notificationURL": "https://www.tu-sitio.com/webhook/bitpay"
        }

        try:
            invoice = self.client.create_invoice(params)
            return invoice
        except BitPayException as e:
            print(f"Error al crear la factura en BitPay: {e}")
            return None

# Ejemplo de uso (esto no se ejecutará directamente, es para demostración)
if __name__ == '__main__':
    # Para probar este script, necesitarías definir la variable de entorno:
    # export BITPAY_API_TOKEN='...'
    print("Inicializando cliente de BitPay (ejemplo)...")
    try:
        client = BitPayClient()

        # Crear una factura por 1500 EUR
        price = 1500.0
        currency_code = "EUR"
        order_id = "ORDER-12345"

        print(f"Creando factura para {price} {currency_code} (Orden: {order_id})...")
        invoice = client.create_invoice(price=price, currency=currency_code, order_id=order_id)

        if invoice:
            print("Factura de BitPay creada con éxito:")
            print(f"  ID de Factura: {invoice.get('id')}")
            print(f"  URL de pago: {invoice.get('url')}")
            print("El usuario sería redirigido a esta URL para completar el pago.")
        else:
            print("No se pudo crear la factura.")

    except ValueError as e:
        print(e)
        print("Por favor, asegúrate de configurar la variable de entorno BITPAY_API_TOKEN.")
