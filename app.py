from flask import Flask, request, jsonify, send_file
import sqlite3
import subprocess
import os

app = Flask(__name__)

# (1) FAILLE SECRET : Clé en dur (Détecté par Gitleaks)
app.config["SECRET_KEY"] = "super-secret-key-12345-do-not-use"
ADMIN_TOKEN = "admin-token-revealed-in-code"

# --- PARTIE 1 : LE VRAI SITE (FRONTEND) ---

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TravelBooking - Vacances de Rêve</title>
        <style>
            body { font-family: 'Helvetica Neue', sans-serif; margin: 0; padding: 0; background-color: #f4f7f6; }
            header { background-color: #003580; color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center; }
            .logo { font-size: 24px; font-weight: bold; }
            nav a { color: white; text-decoration: none; margin-left: 20px; font-weight: bold; }
            nav a.danger { background: #d9534f; padding: 8px 15px; border-radius: 4px; }
            
            .hero { background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1600&q=80'); background-size: cover; height: 300px; display: flex; align-items: center; justify-content: center; text-align: center; color: white; }
            .search-box { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); display: flex; gap: 10px; }
            input { padding: 10px; border: 1px solid #ccc; border-radius: 4px; width: 300px; }
            button { background-color: #0071c2; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
            
            .container { max-width: 1000px; margin: 40px auto; padding: 0 20px; }
            h2 { color: #333; }
            .destinations { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
            .card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); transition: transform 0.2s; }
            .card:hover { transform: translateY(-5px); }
            .card img { width: 100%; height: 150px; object-fit: cover; }
            .card-body { padding: 15px; }
            .price { color: #008009; font-weight: bold; font-size: 1.2em; float: right; }
            
            footer { text-align: center; padding: 20px; color: #666; font-size: 0.8em; margin-top: 50px; }
        </style>
    </head>
    <body>
        <header>
            <div class="logo">✈️ TravelBooking</div>
            <nav>
                <a href="/">Accueil</a>
                <a href="#">Mes Réservations</a>
                <a href="/hacker-console" class="danger">⚠️ Console Admin (Hacker)</a>
            </nav>
        </header>

        <div class="hero">
            <div>
                <h1>Trouvez votre prochain séjour</h1>
                <p>Des offres exclusives vers le monde entier</p>
                <form action="/search" method="get" class="search-box">
                    <input type="text" name="q" placeholder="Rechercher une destination (ex: Paris)...">
                    <button type="submit">Rechercher</button>
                </form>
            </div>
        </div>

        <div class="container">
            <h2>🔥 Destinations Populaires</h2>
            <div class="destinations">
                <div class="card">
                    <img src="https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=500&q=60" alt="Paris">
                    <div class="card-body">
                        <h3>Paris, France</h3>
                        <p>Hôtel vue Tour Eiffel</p>
                        <span class="price">450€</span>
                    </div>
                </div>
                <div class="card">
                    <img src="https://images.unsplash.com/photo-1496442226666-8d4a0e62e6e9?auto=format&fit=crop&w=500&q=60" alt="New York">
                    <div class="card-body">
                        <h3>New York, USA</h3>
                        <p>Business Suite Manhattan</p>
                        <span class="price">1200€</span>
                    </div>
                </div>
                <div class="card">
                    <img src="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=500&q=60" alt="Tokyo">
                    <div class="card-body">
                        <h3>Tokyo, Japon</h3>
                        <p>Capsule Hotel Shinjuku</p>
                        <span class="price">80€</span>
                    </div>
                </div>
            </div>
        </div>
        
        <footer>
            &copy; 2024 TravelBooking Inc. - <a href="/health">System Status</a>
        </footer>
    </body>
    </html>
    """

# --- PARTIE 2 : LE TABLEAU DE BORD "HACKER" ---

@app.route("/hacker-console")
def hacker_console():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hacker Console - TravelBooking</title>
        <style>
            body { font-family: monospace; background-color: #1e1e1e; color: #00ff00; padding: 40px; }
            h1 { border-bottom: 2px solid #00ff00; padding-bottom: 10px; }
            .box { border: 1px solid #444; background: #252526; padding: 20px; margin-bottom: 20px; border-radius: 5px; }
            a { color: #fff; text-decoration: underline; }
            a:hover { color: #ff0000; }
            .tag { background: #ff0000; color: white; padding: 2px 5px; font-weight: bold; border-radius: 3px; }
            code { background: #333; padding: 2px 5px; color: #fff; }
        </style>
    </head>
    <body>
        <h1>💀 CONSOLE D'EXPLOITATION DES FAILLES</h1>
        <p>Ce panneau permet de démontrer les vulnérabilités laissées par les développeurs.</p>

        <div class="box">
            <h3>1. <span class="tag">SQL INJECTION</span> - Vol de base de données</h3>
            <p>La barre de recherche sur l'accueil est vulnérable. On peut dumper toute la base.</p>
            <p>Payload: <code>' OR 1=1 --</code></p>
            <ul>
                <li><a href="/search?q=Paris" target="_blank">Recherche normale (Paris)</a></li>
                <li><a href="/search?q=' OR 1=1 --" target="_blank">🚨 Lancer l'attaque (Dump DB)</a></li>
            </ul>
        </div>

        <div class="box">
            <h3>2. <span class="tag">RCE</span> - Exécution de commande (Remote Code Execution)</h3>
            <p>Le développeur a laissé un outil de debug accessible.</p>
            <p>Payload: <code>cat /etc/passwd</code> ou <code>id</code></p>
            <ul>
                <li><a href="/debug/run?cmd=id" target="_blank">🚨 Qui est l'utilisateur ? (id)</a></li>
                <li><a href="/debug/run?cmd=ls -la" target="_blank">🚨 Lister les fichiers serveur</a></li>
            </ul>
        </div>

        <div class="box">
            <h3>3. <span class="tag">LFI</span> - Path Traversal (Vol de fichiers)</h3>
            <p>Le endpoint de téléchargement de rapport ne vérifie pas le chemin.</p>
            <ul>
                <li><a href="/report?file=/etc/passwd" target="_blank">🚨 Lire /etc/passwd</a></li>
                <li><a href="/report?file=app.py" target="_blank">🚨 Lire le code source (app.py)</a></li>
            </ul>
        </div>

        <p><a href="/" style="color: #fff; text-decoration: none;">&larr; Retour au site normal</a></p>
    </body>
    </html>
    """

# --- PARTIE 3 : LE BACKEND VULNÉRABLE ---

@app.get("/health")
def health():
    return {"status": "ok", "service": "travel-booking-v1"}

# FAILLE SQL INJECTION (Simulée)
@app.get("/search")
def search():
    q = request.args.get("q", "")
    
    # Setup DB temporaire
    if not os.path.exists("bookings.db"):
        conn = sqlite3.connect("bookings.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE trips (id INTEGER, city TEXT, hotel TEXT, price REAL)")
        cursor.execute("INSERT INTO trips VALUES (1, 'Paris', 'Hotel Luxury', 450.0)")
        cursor.execute("INSERT INTO trips VALUES (2, 'New York', 'Business Suite', 1200.0)")
        cursor.execute("INSERT INTO trips VALUES (3, 'Tokyo', 'Capsule Hotel', 80.0)")
        cursor.execute("INSERT INTO trips VALUES (4, 'Admin Secret', 'Hidden Base', 0.0)")
        conn.commit()
    
    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()
    
    # VULNERABLE : f-string directe
    try:
        query = f"SELECT city, hotel, price FROM trips WHERE city LIKE '%{q}%'"
        rows = cur.execute(query).fetchall()
        # On renvoie du JSON brut pour voir le résultat de l'attaque
        return jsonify(rows) 
    except Exception as e:
        return jsonify({"error": str(e), "query": query}), 500

# FAILLE RCE
@app.get("/debug/run")
def debug_run():
    cmd = request.args.get("cmd", "id")
    try:
        # VULNERABLE : shell=True
        out = subprocess.check_output(cmd, shell=True, text=True)
        return {"output": out}
    except Exception as e:
        return {"error": str(e)}

# FAILLE LFI
@app.get("/report")
def report():
    filename = request.args.get("file", "requirements.txt")
    try:
        return send_file(filename)
    except Exception as e:
        return {"error": "File not found"}, 404

# FAILLE LOGIQUE (Pour faire planter le test unitaire)
@app.post("/discount")
def discount():
    try:
        data = request.get_json(force=True)
        pct = int(data.get("pct", 0))
        # BUG: Si on envoie 100%, ça fait une erreur ou un prix négatif non géré
        if pct < 0 or pct > 100:
            return {"error": "Invalid percentage"}, 400
        new_price = 1000 * (100 - pct) / 100
        return {"new_price": new_price}
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)