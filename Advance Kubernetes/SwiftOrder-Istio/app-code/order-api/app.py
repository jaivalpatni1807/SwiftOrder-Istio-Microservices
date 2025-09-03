# app-code/order-api/app.py
from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Get service URLs from environment variables, with defaults for local running
USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://localhost:8080")
INVENTORY_SERVICE_URL = os.environ.get("INVENTORY_SERVICE_URL", "http://localhost:5000")

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    if not data or 'userId' not in data or 'itemId' not in data:
        return jsonify({"error": "Missing userId or itemId"}), 400

    user_id = data['userId']
    item_id = data['itemId']

    # 1. Call User Service to check credit
    try:
        credit_response = requests.get(f"{USER_SERVICE_URL}/users/{user_id}/credit")
        credit_response.raise_for_status() # Raise an exception for bad status codes
        credit_data = credit_response.json()
        user_service_version = credit_data.get('version', 'unknown')
        if credit_data.get('status') != 'approved':
            return jsonify({"status": "order_declined", "reason": "insufficient_credit", "user_service_version": user_service_version}), 402
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"User service unavailable: {e}"}), 503

    # 2. Call Inventory Service to check stock
    try:
        stock_response = requests.get(f"{INVENTORY_SERVICE_URL}/inventory/{item_id}/check")
        stock_response.raise_for_status()
        stock_data = stock_response.json()
        if stock_data.get('stock') != 'available':
            return jsonify({"status": "order_declined", "reason": "out_of_stock"}), 409
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Inventory service unavailable: {e}"}), 503
    
    # If all checks pass, confirm the order
    return jsonify({
        "status": "order_confirmed", 
        "userId": user_id, 
        "itemId": item_id,
        "checked_by_user_service": user_service_version
    }), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)