from flask import Flask, request, jsonify, send_file
import sqlite3
import os

app = Flask(__name__)

# CORRECTION 1 (Gitleaks) : Secret via variable d'environnement
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "default-dev-key")

# --- FRONTEND SÉCURISÉ ---
@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TravelBooking - Secure</title>
        <style>
            body { font-family: sans-serif; padding: 40px; text-align: center; background: #f0f2f5; }
            .card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 600px; margin: auto; }
            h1 { color: #27ae60; }
            input { padding: 10px; width: 70%; margin-right: 5px; }
            button { padding: 10px 20px; background: #27ae60; color: white; border: none; cursor: pointer; }
            .badge { background: #27ae60; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🛡️ TravelBooking (Secure)</h1>
            <p>Version validée et sécurisée.</p>
            <form action="/search" method="get">
                <input type="text" name="q" placeholder="Rechercher une destination...">
                <button type="submit">Rechercher</button>
            </form>
            <br>
            <p><span class="badge">SECURE</span> Injection SQL corrigée</p>
            <p><span class="badge">SECURE</span> RCE supprimée</p>
            <p><span class="badge">SECURE</span> Path Traversal bloqué</p>
            <br>
            <a href="/health">Healthcheck API</a>
        </div>
    </body>
    </html>
    """

@app.get("/health")
def health():
    return {"status": "ok", "service": "travel-booking-secure"}

# CORRECTION 2 (Semgrep - SQLi) : Requêtes paramétrées
@app.get("/search")
def search():
    q = request.args.get("q", "")
    
    # DB Setup
    if not os.path.exists("bookings.db"):
        conn = sqlite3.connect("bookings.db")
        cur = conn.cursor()
        cur.execute("CREATE TABLE trips (id INTEGER, city TEXT, price REAL)")
        cur.execute("INSERT INTO trips VALUES (1, 'Paris', 450.0)")
        cur.execute("INSERT INTO trips VALUES (2, 'New York', 1200.0)")
        conn.commit()
    
    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()
    
    try:
        # SECURE: Utilisation de ? pour les paramètres (Pas de f-string !)
        query = "SELECT city, price FROM trips WHERE city LIKE ?"
        rows = cur.execute(query, (f"%{q}%",)).fetchall()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": "Database error"}), 500

# CORRECTION 3 (Semgrep - RCE) : L'endpoint /debug/run est supprimé.

# CORRECTION 4 (ZAP - Path Traversal) : Whitelist
@app.get("/report")
def report():
    filename = request.args.get("file", "requirements.txt")
    ALLOWED = ['requirements.txt', 'README.md']
    
    if filename not in ALLOWED:
        return {"error": "Access denied"}, 403
        
    try:
        return send_file(filename)
    except Exception:
        return {"error": "File not found"}, 404

# CORRECTION 5 (Pytest) : Logique corrigée
@app.post("/discount")
def discount():
    try:
        data = request.get_json(force=True)
        pct = int(data.get("pct", 0))
        
        if pct < 0 or pct > 100:
            return {"error": "Invalid percentage"}, 400
            
        base_price = 1000
        new_price = base_price * (100 - pct) / 100
        return {"new_price": new_price}
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
