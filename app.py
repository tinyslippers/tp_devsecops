# app.py
from flask import Flask, request
import os

app = Flask(__name__)

# FAILLE 1 (Pour Gitleaks) : Un faux secret en dur dans le code
# Les scanners de secrets vont hurler en voyant ça.
AWS_ACCESS_KEY = "AKIAIMNOVALIDKEYEXAMPLE" 

@app.route('/')
def home():
    return "Bienvenue sur l'API DevSecOps v1"

@app.route('/user')
def get_user():
    user_id = request.args.get('id')
    
    # FAILLE 2 (Pour Semgrep/Sonar) : Une injection de commande basique
    # C'est une très mauvaise pratique que les scanners SAST détectent immédiatement.
    os.system("echo " + user_id) 
    
    return f"Utilisateur: {user_id}"

if __name__ == '__main__':
    # Le port 5000 correspond à la description du système
    app.run(host='0.0.0.0', port=5000)