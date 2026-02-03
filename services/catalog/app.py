from flask import Flask, request, jsonify, send_file
import sqlite3
import os

app = Flask(__name__)

# SÉCURITÉ : Secret via variable d'environnement
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "default-dev-key")

# --- FRONTEND (Le Joli Design) ---
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
            .search-box { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); display: flex; gap: 10px; }
            input { padding: 10px; border: 1px solid #ccc; border-radius: 4px; width: 300px; }
            button { background-color: #27ae60; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
            
            .container { max-width: 1000px; margin: 40px auto; padding: 0 20px; }
            h2 { color: #333; }
            .destinations { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
            .card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); transition: transform 0.2s; }
            .card:hover { transform: translateY(-5px); }
            .card img { width: 100%; height: 150px; object-fit: cover; }
            .card-body { padding: 15px; }
            .price { color: #27ae60; font-weight: bold; font-size: 1.2em; float: right; }
            
            footer { text-align: center; padding: 20px; color: #666; font-size: 0.8em; margin-top: 50px; }
            .badge-secure { background: #27ae60; color: white; padding: 5px 10px; border-radius: 20px; font-size: 0.8em; }
        </style>
    </head>
    <body>
        <header>
            <div class="logo">🛡️ TravelBooking (Secure)</div>
            <nav>
                <a href="/">Accueil</a>
                <a href="#">Mes Réservations</a>
                </nav>
        </header>

        <div class="hero">
            <div>
                <h1>Voyagez en toute sécurité</h1>
                <p>Version validée par le pipeline DevSecOps</p>
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
            
            <br><hr><br>
            <div style="text-align: center;">
                <span class="badge-secure">✅ SQL Injection Corrigée</span>
                <span class="badge-secure">✅ Secrets Protégés</span>
                <span class="badge-secure">✅ RCE Supprimée</span>
            </div>
        </div>
        
        <footer>
            &copy; 2024 TravelBooking Inc. - <a href="/health">System Status</a>
        </footer>
    </body>
    </html>
    """

@app.get("/health")
def health():
    return {"status": "ok", "service": "travel-booking-secure"}

# SÉCURITÉ : Requêtes paramétrées (Le ? protège l'injection)
@app.get("/search")
def search():
    q = request.args.get("q", "")
    
    if not os.path.exists("bookings.db"):
        conn = sqlite3.connect("bookings.db")
        cur = conn.cursor()
        cur.execute("CREATE TABLE trips (id INTEGER, city TEXT, hotel TEXT, price REAL)")
        cur.execute("INSERT INTO trips VALUES (1, 'Paris', 'Hotel Luxury', 450.0)")
        cur.execute("INSERT INTO trips VALUES (2, 'New York', 'Business Suite', 1200.0)")
        cur.execute("INSERT INTO trips VALUES (3, 'Tokyo', 'Capsule Hotel', 80.0)")
        conn.commit()
    
    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()
    
    try:
        # SECURE : Utilisation de placeholder ?
        query = "SELECT city, hotel, price FROM trips WHERE city LIKE ?"
        rows = cur.execute(query, (f"%{q}%",)).fetchall()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": "Database error"}), 500

# SÉCURITÉ : Whitelist pour les fichiers
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

# SÉCURITÉ : Logique métier corrigée
@app.post("/discount")
def discount():
    try:
        data = request.get_json(force=True)
        pct = int(data.get("pct", 0))
        if pct < 0 or pct > 100:
            return {"error": "Invalid percentage"}, 400
        new_price = 1000 * (100 - pct) / 100
        return {"new_price": new_price}
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
