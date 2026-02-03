from flask import Flask, request, jsonify, send_file
import sqlite3
import subprocess
import os

app = Flask(__name__)

# (1) Secret en dur (Détecté par Gitleaks)
app.config["SECRET_KEY"] = "booking-site-secret-key-12345"
ADMIN_TOKEN = "admin-access-token-super-secret"

# --- INTERFACE D'ACCUEIL (FRONTEND MINIMAL) ---
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
            .badge { background: #e74c3c; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
            a { display: block; margin: 15px 0; padding: 15px; background: #f8f9fa; border-left: 5px solid #3498db; text-decoration: none; color: #2c3e50; transition: 0.2s; }
            a:hover { background: #e9ecef; border-left-color: #2980b9; }
            .vuln { border-left-color: #e74c3c; }
            .vuln:hover { border-left-color: #c0392b; background: #fadbd8; }
            code { background: #eee; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✈️ TravelBooking System</h1>
            <p>Portail de gestion des réservations (Environnement de Staging).</p>
            
            <h3>🔍 Actions Utilisateur (Tests de Vulnérabilités)</h3>
            
            <a href="/search?q=Paris" class="vuln">
                <span class="badge">FAILLE SQLi</span> 
                <b>Rechercher un voyage</b><br>
                <small>Teste l'injection SQL via le paramètre <code>?q=...</code></small>
            </a>

            <a href="/report?file=/etc/passwd" class="vuln">
                <span class="badge">FAILLE LFI</span> 
                <b>Télécharger le rapport financier</b><br>
                <small>Teste le Path Traversal via <code>?file=...</code></small>
            </a>

            <a href="/debug/run?cmd=id" class="vuln">
                <span class="badge">FAILLE RCE</span> 
                <b>Diagnostic Serveur</b><br>
                <small>Exécute des commandes via <code>?cmd=...</code></small>
            </a>

            <hr>
            <h3>✅ Monitoring</h3>
            <a href="/health">Healthcheck API (JSON)</a>
        </div>
    </body>
    </html>
    """

# --- API BACKEND VULNÉRABLE ---

@app.get("/health")
def health():
    return {"status": "ok", "service": "reservation-api"}

# (2) SQL Injection (Semgrep)
# Scénario : Recherche de destinations de voyage
@app.get("/search")
def search():
    q = request.args.get("q", "")
    
    # Création de la fausse BDD pour la démo
    if not os.path.exists("bookings.db"):
        conn = sqlite3.connect("bookings.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE bookings (id INTEGER, client TEXT, destination TEXT, price REAL)")
        cursor.execute("INSERT INTO bookings VALUES (1, 'Martin Durand', 'Paris - Hotel Luxury', 450.0)")
        cursor.execute("INSERT INTO bookings VALUES (2, 'Sophie Leroi', 'New York - Business Suite', 1200.0)")
        cursor.execute("INSERT INTO bookings VALUES (3, 'Jean Dupont', 'Tokyo - Capsule Hotel', 80.0)")
        conn.commit()
    
    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()
    
    # VULNERABLE : Concaténation directe
    try:
        query = f"SELECT client, destination, price FROM bookings WHERE destination LIKE '%{q}%'"
        rows = cur.execute(query).fetchall()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# (3) Command Injection (Semgrep)
# Scénario : Outil d'admin pour vérifier le serveur
@app.get("/debug/run")
def debug_run():
    cmd = request.args.get("cmd", "id")
    # VULNERABLE : shell=True
    try:
        out = subprocess.check_output(cmd, shell=True, text=True)
        return {"server_output": out}
    except Exception as e:
        return {"error": str(e)}

# (4) Path Traversal (ZAP / DAST)
# Scénario : Récupération de factures ou rapports
@app.get("/report")
def report():
    filename = request.args.get("file", "README.md")
    # VULNERABLE : Pas de validation du chemin
    try:
        return send_file(filename)
    except Exception as e:
        return {"error": "File not found"}, 404

# (5) Logic Bug (Pour faire échouer les tests unitaires)
# Scénario : Appliquer une remise sur une réservation
@app.post("/discount")
def discount():
    try:
        data = request.get_json(force=True)
        pct = int(data.get("pct", 0))
        base_price = 1000 # Prix standard
        
        # BUG VOLONTAIRE : Erreur de logique ou variable non définie
        # Ici, on imagine que le développeur a oublié de définir 'final_price' correctement avant le return
        # ou utilise une variable globale inexistante.
        # Pour le TP, faisons simple : Division par zéro si pct=100 ou variable mal nommée
        
        if pct == 100:
             return {"error": "Free bookings not allowed"}, 400

        # Bug simulé : calcul faux qui renvoie un prix négatif si remise > 100 (ce qui ne devrait pas arriver)
        # Ou simplement une erreur de syntaxe simulée qui ferait planter le test
        new_price = base_price * (100 - pct) / 100
        
        return {"new_price": new_price}
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    # (6) Debug activé (Mauvaise pratique en prod)
    app.run(host="0.0.0.0", port=5000, debug=True)