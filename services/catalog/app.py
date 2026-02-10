from flask import Flask, request, jsonify, send_file, g
import sqlite3
import os
import time
import uuid
import json

app = Flask(__name__)

# Config TP2
SERVICE_NAME = "catalog"

# SÉCURITÉ : Secret via variable d'environnement
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "default-dev-key")

# --- PARTIE B TP2 : Request-ID & LOGGING JSON ---
@app.before_request
def _before():
    g.t0 = time.time()
    # B.1 : Conserver ou générer le Request-ID 
    rid = request.headers.get("X-Request-Id")
    g.request_id = rid if rid else str(uuid.uuid4())

@app.after_request
def _after(resp):
    # B.2 : Calcul de latence et log JSON [cite: 28, 29, 37]
    latency_ms = int((time.time() - g.t0) * 1000)
    record = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "level": "INFO",
        "service": SERVICE_NAME,
        "request_id": g.request_id,
        "method": request.method,
        "path": request.path,
        "status": resp.status_code,
        "latency_ms": latency_ms,
        "query": (request.query_string.decode("utf-8")[:200] if request.query_string else ""),
    }
    # On affiche le JSON pour que Docker le capture [cite: 41]
    print(json.dumps(record), flush=True)
    resp.headers["X-Request-Id"] = g.request_id
    return resp

# --- FRONTEND (Gardé tel quel) ---
@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TravelBooking - Secure Edition</title>
        <style>
            body { font-family: 'Helvetica Neue', sans-serif; margin: 0; padding: 0; background-color: #f4f7f6; }
            header { background-color: #27ae60; color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center; }
            .logo { font-size: 24px; font-weight: bold; }
            nav a { color: white; text-decoration: none; margin-left: 20px; font-weight: bold; }
            .hero { background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1600&q=80'); background-size: cover; height: 300px; display: flex; align-items: center; justify-content: center; text-align: center; color: white; }
            .search-box { background: white; padding: 20px; border-radius: 8px; shadow: 0 4px 10px rgba(0,0,0,0.3); display: flex; gap: 10px; }
            input { padding: 10px; border: 1px solid #ccc; border-radius: 4px; width: 300px; }
            button { background-color: #27ae60; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
            .container { max-width: 1000px; margin: 40px auto; padding: 0 20px; }
            .destinations { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
            .card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .card-body { padding: 15px; }
            .price { color: #27ae60; font-weight: bold; float: right; }
            .badge-secure { background: #27ae60; color: white; padding: 5px 10px; border-radius: 20px; font-size: 0.8em; }
            footer { text-align: center; padding: 20px; color: #666; font-size: 0.8em; margin-top: 50px; }
        </style>
    </head>
    <body>
        <header><div class="logo">🛡️ TravelBooking (Secure)</div></header>
        <div class="hero">
            <div>
                <h1>Voyagez en toute sécurité</h1>
                <p>Version validée par le pipeline DevSecOps (Runtime Monitored)</p>
                <form action="/search" method="get" class="search-box">
                    <input type="text" name="q" placeholder="Rechercher une destination...">
                    <button type="submit">Rechercher</button>
                </form>
            </div>
        </div>
        <div class="container">
            <div style="text-align: center;">
                <span class="badge-secure">✅ Logs JSON Activés</span>
                <span class="badge-secure">✅ Monitoring Staging</span>
            </div>
        </div>
        <footer>&copy; 2024 TravelBooking Inc. - <a href="/health">System Status</a></footer>
    </body>
    </html>
    """

@app.get("/health")
def health():
    return {"status": "ok", "service": "travel-booking-secure"}

@app.get("/search")
def search():
    q = request.args.get("q", "")
    if not os.path.exists("bookings.db"):
        conn = sqlite3.connect("bookings.db")
        cur = conn.cursor()
        cur.execute("CREATE TABLE trips (id INTEGER, city TEXT, hotel TEXT, price REAL)")
        cur.execute("INSERT INTO trips VALUES (1, 'Paris', 'Hotel Luxury', 450.0)")
        conn.commit()
    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()
    try:
        query = "SELECT city, hotel, price FROM trips WHERE city LIKE ?"
        rows = cur.execute(query, (f"%{q}%",)).fetchall()
        return jsonify(rows)
    except Exception:
        return jsonify({"error": "Database error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)