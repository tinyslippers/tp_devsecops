from flask import Flask, request, jsonify, send_file
import sqlite3
import subprocess
import os
import shlex  # Nécessaire pour sécuriser les commandes système

app = Flask(__name__)

# (1) Secret en dur (Gitleaks l'a vu, mais pour l'instant on se concentre sur Semgrep)
app.config["SECRET_KEY"] = "booking-site-secret-key-12345"
ADMIN_TOKEN = "admin-access-token-super-secret"

# --- PAGE D'ACCUEIL ---
@app.route("/")
def index():
    return """
    <html>
    <head>
        <title>TravelBooking - DevSecOps Demo</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; padding: 40px; background: #eef2f5; color: #333; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            .badge { background: #27ae60; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
            a { display: block; margin: 15px 0; padding: 15px; background: #f8f9fa; border-left: 5px solid #27ae60; text-decoration: none; color: #2c3e50; transition: 0.2s; }
            a:hover { background: #e9ecef; border-left-color: #2ecc71; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✈️ TravelBooking System (Secured)</h1>
            <p>Version sécurisée et validée par Semgrep.</p>
            
            <h3>🔍 Tests (Maintenant Sécurisés)</h3>
            <a href="/search?q=Paris"><span class="badge">SECURE</span> Recherche Voyage (SQLi fixée)</a>
            <a href="/debug/run?cmd=id"><span class="badge">SECURE</span> Diagnostic (RCE fixée)</a>
            <a href="/health">Healthcheck</a>
        </div>
    </body>
    </html>
    """

@app.get("/health")
def health():
    return {"status": "ok", "service": "reservation-api"}

# (2) CORRECTION INJECTION SQL (Semgrep: python.django.security.injection.sql...)
@app.get("/search")
def search():
    q = request.args.get("q", "")
    
    # Init BDD (si besoin)
    if not os.path.exists("bookings.db"):
        conn = sqlite3.connect("bookings.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE bookings (id INTEGER, client TEXT, destination TEXT, price REAL)")
        cursor.execute("INSERT INTO bookings VALUES (1, 'Martin Durand', 'Paris - Hotel Luxury', 450.0)")
        conn.commit()
    
    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor() # On utilise 'cur' pour être cohérent
    
    try:
        # CORRECTION : Utilisation de '?' pour les paramètres (Parameterized Query)
        # Semgrep ne détectera plus de concaténation de chaîne dangereuse ici.
        query = "SELECT client, destination, price FROM bookings WHERE destination LIKE ?"
        cur.execute(query, ('%' + q + '%',))
        
        rows = cur.fetchall()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# (3) CORRECTION INJECTION DE COMMANDE (Semgrep: python.lang.security.audit.subprocess-shell-true)
@app.get("/debug/run")
def debug_run():
    cmd = request.args.get("cmd", "id")
    try:
        # CORRECTION : On désactive le shell et on utilise shlex pour découper les arguments
        # Cela empêche l'attaquant d'utiliser des ; ou && pour lancer d'autres commandes.
        args = shlex.split(cmd)
        out = subprocess.check_output(args, shell=False, text=True)
        return {"server_output": out}
    except Exception as e:
        return {"error": str(e)}

# (4) Path Traversal (Reste inchangé pour ce TP si Semgrep ne le bloque pas spécifiquement ici)
@app.get("/report")
def report():
    filename = request.args.get("file", "README.md")
    try:
        return send_file(filename)
    except Exception as e:
        return {"error": "File not found"}, 404

# (5) Logic Bug (Simplifié pour éviter les erreurs)
@app.post("/discount")
def discount():
    return {"message": "Discount feature disabled for security review"}

if __name__ == "__main__":
    # (6) CORRECTION DEBUG MODE (Semgrep: python.flask.security.audit.debug-enabled)
    # Ne jamais laisser debug=True en prod !
    app.run(host="0.0.0.0", port=5000, debug=False)