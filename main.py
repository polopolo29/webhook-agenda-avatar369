from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("🔔 Webhook recibido:", data)
    
    if "Tratamiento completo" in data.get("product_name", ""):
        name = data.get("name", "Usuario")
        phone = data.get("phone", "Sin teléfono")
        print(f"🌀 Compra detectada de {name}, Tel: {phone}")
        return jsonify({"status": "ok", "message": "Compra recibida"}), 200

    return jsonify({"status": "ignored"}), 200

@app.route('/')
def home():
    return "✅ Webhook de Avatar369 corriendo"

if __name__ == "__main__":
    app.run()
