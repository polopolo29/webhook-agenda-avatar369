import os
import stripe

class StripeClient:
    """
    Un cliente para interactuar con la API de Stripe.
    Gestiona la creación de PaymentIntents.
    """
    def __init__(self, api_key=None):
        """
        Inicializa el cliente de Stripe.
        La clave de API se leerá de la variable de entorno STRIPE_SECRET_KEY.
        """
        self.api_key = api_key or os.environ.get('STRIPE_SECRET_KEY')

        if not self.api_key:
            raise ValueError("La clave secreta de Stripe (STRIPE_SECRET_KEY) no fue proporcionada.")

        stripe.api_key = self.api_key

    def create_payment_intent(self, amount, currency, customer_id=None):
        """
        Crea un PaymentIntent en Stripe.

        :param amount: El monto a cobrar, en la unidad mínima de la moneda (ej. centavos).
                       Por ejemplo, para 100.50 EUR, el monto debe ser 10050.
        :param currency: El código de la moneda en formato de 3 letras (ej. 'eur', 'usd').
        :param customer_id: El ID de un cliente de Stripe existente (opcional).
        :return: Un objeto PaymentIntent de Stripe o None si hay un error.
        """
        try:
            payment_intent_params = {
                'amount': amount,
                'currency': currency,
                'payment_method_types': ['card'],
            }
            if customer_id:
                payment_intent_params['customer'] = customer_id

            payment_intent = stripe.PaymentIntent.create(**payment_intent_params)
            return payment_intent
        except stripe.error.StripeError as e:
            print(f"Error al crear el PaymentIntent en Stripe: {e}")
            return None

# Ejemplo de uso (esto no se ejecutará directamente, es para demostración)
if __name__ == '__main__':
    # Para probar este script, necesitarías definir la variable de entorno:
    # export STRIPE_SECRET_KEY='sk_test_...'
    print("Inicializando cliente de Stripe (ejemplo)...")
    try:
        client = StripeClient()

        # Crear un PaymentIntent por 199.99 EUR
        amount_in_cents = 19999
        currency_code = "eur"

        print(f"Creando PaymentIntent para {amount_in_cents / 100} {currency_code.upper()}...")
        payment_intent = client.create_payment_intent(amount=amount_in_cents, currency=currency_code)

        if payment_intent:
            print("PaymentIntent creado con éxito:")
            print(f"  ID: {payment_intent.id}")
            print(f"  Client Secret: {payment_intent.client_secret}")
            print("El 'client_secret' se usaría en el frontend para confirmar el pago.")
        else:
            print("No se pudo crear el PaymentIntent.")

    except ValueError as e:
        print(e)
        print("Por favor, asegúrate de configurar la variable de entorno STRIPE_SECRET_KEY.")
