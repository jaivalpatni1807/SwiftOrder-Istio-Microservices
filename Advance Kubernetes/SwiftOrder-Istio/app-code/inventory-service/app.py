# app-code/inventory-service/app.py
from flask import Flask, jsonify
import os
import psycopg2

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    )
    return conn

@app.route('/inventory/<item_id>/check', methods=['GET'])
def check_stock(item_id):
    print(f"Checking stock for item: {item_id}")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT stock_count FROM inventory WHERE item_id = %s', (item_id,))
        item = cur.fetchone()
        cur.close()
        conn.close()

        if item is None:
            return jsonify({"error": "Item not found"}), 404
        
        stock_count = item[0]
        status = "available" if stock_count > 0 else "out_of_stock"

        return jsonify({"itemId": item_id, "stock": status, "quantity": stock_count})

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)