from flask import Flask, jsonify, request
import time
import psycopg2
from psycopg2 import sql

app = Flask("server-db")

# Wait for Postgres to be ready
for i in range(15):
    try:
        conn = psycopg2.connect(
            database="flask_db",
            user="user",
            password="pass",
            host="postgres",
            port="5432"
        )
        print("Connected to Postgres!")
        break
    except psycopg2.OperationalError:
        print("Postgres not ready yet, retrying in 2 seconds...")
        time.sleep(2)
else:
    raise Exception("Could not connect to Postgres after multiple attempts")

curr = conn.cursor()

# Create table if it doesn't exist
try:
    curr.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) UNIQUE,
        price FLOAT
    );
    ''')
    conn.commit()
except psycopg2.errors.UniqueViolation:
    conn.rollback() # Important: rollback the failed transaction
    print("Table already being created by another instance, skipping...")

# Insert data only if it doesn't exist
products = [
    ('APPLE', 1.99),
    ('ORANGE', 0.99),
    ('BANANA', 0.59)
]

for name, price in products:
    curr.execute(
        sql.SQL("INSERT INTO products (name, price) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING"),
        [name, price]
    )

conn.commit()
curr.close()
conn.close()

@app.route('/health')
def healt_check():
    return jsonify({"health": "true"})

@app.route('/')
def get_products():
    conn = psycopg2.connect(
        database="flask_db",
        user="user",
        password="pass",
        host="postgres",
        port="5432"
    )
    curr = conn.cursor()
    curr.execute('SELECT * FROM products')
    data = curr.fetchall()
    curr.close()
    conn.close()
    return jsonify(data)

@app.route('/add', methods=["POST"])
def add_items():
    conn = None
    curr = None
    try:
        conn = psycopg2.connect(
            database="flask_db",
            user="user",
            password="pass",
            host="postgres",
            port="5432"
        )
        curr = conn.cursor()

        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        items = request.get_json()
        name = items.get("name")
        price = items.get("price")

        if not name or price is None:
            return jsonify({"error": "Missing name or price"}), 400

        curr.execute('''
            INSERT INTO products (name, price) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING
        ''', (name, price))
        conn.commit()

        return jsonify({"message": "Item added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if curr:
            curr.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)