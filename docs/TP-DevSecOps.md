# Documentation TP DevSecOps - TravelBooking System

## 1. Architecture Applicative
L'application **TravelBooking** est un système microservices permettant la gestion de réservations de voyages.

* **Service Principal :** `catalog` (API de gestion des réservations).
* **Technologie :** Python / Flask.
* **Conteneurisation :** Docker (Image basée sur `python:alpine`).
* **Communication :** API REST sur le port 5000.
* **Points d'entrée exposés :**
    * `GET /` : Portail d'accueil (Front-end minimal).
    * `GET /search` : Recherche de voyages (Vulnérable SQLi).
    * `GET /health` : Endpoint de monitoring.
* **Flux de données :** Les requêtes utilisateurs transitent en HTTP clair vers l'API qui interroge une base de données SQLite locale.

## 2. Pipeline CI/CD et Sécurité
Le pipeline est orchestré via **GitHub Actions** et suit l'approche "Shift Left" (sécurité au plus tôt).

### Phase 1 : Qualité & Tests (Fast Feedback)
* **Tests Unitaires :** Exécution de `pytest` pour valider la logique métier avant tout scan de sécurité.
* **Gate Qualité :** Si les tests échouent (ex: bug fonctionnel), le pipeline s'arrête immédiatement.

### Phase 2 : Analyse Statique (SAST & Secrets)
* **Détection de secrets :** Outil **Gitleaks**. Scanne l'historique git pour trouver des clés API (ex: `SECRET_KEY`).
* **Analyse de code (SAST) :** Outil **Semgrep**. Analyse le code source Python pour détecter des patterns dangereux (Injections SQL, RCE).
* **Gate Sécurité :** Bloquante si des vulnérabilités critiques sont trouvées.

### Phase 3 : Build & Container Security (SCA)
* **Build :** Construction de l'image Docker `travel-app`.
* **Scan d'image :** Outil **Trivy**. Analyse l'image construite pour détecter les CVEs dans l'OS et les librairies.
* **Gate :** Le pipeline échoue si une faille de sévérité `CRITICAL` est détectée (exit code 1).

### Phase 4 : Déploiement Staging & DAST
* **Déploiement :** Lancement d'un conteneur éphémère simulant l'environnement de staging.
* **Supervision :** Exécution automatique des scripts `smoke.sh` et `supervision.sh` pour valider la santé du service (`/health`).
* **Scan Dynamique (DAST) :** Outil **OWASP ZAP**. Scanne l'application en cours d'exécution pour détecter des failles web.

## 3. Analyse des Risques et Contrôles
Tableau des risques identifiés dans le module `catalog` et contrôles mis en place :

| Catégorie | Risque Identifié | Origine Technique | Mécanisme de Détection |
| :--- | :--- | :--- | :--- |
| **Secrets** | Fuite de clés API | Clé `SECRET_KEY` en dur dans `app.py`. | **Gitleaks** (Commit Scan) |
| **Injection** | Injection SQL (SQLi) | Concaténation directe dans la requête SQL (`/search`). | **Semgrep** (SAST) |
| **Injection** | Exécution de commande (RCE) | Utilisation de `subprocess` avec `shell=True` (`/debug/run`). | **Semgrep** (SAST) |
| **Système** | Path Traversal | Lecture de fichiers arbitraires via `send_file` (`/report`). | **OWASP ZAP** (DAST) |
| **Dépendances** | Vulnérabilités OS | Utilisation d'images de base obsolètes. | **Trivy** (Container Scan) |

## 4. Configuration des Gates
Les gates de sécurité sont configurées pour être **bloquantes** :
* **Gitleaks :** Bloque si un secret est trouvé.
* **Semgrep :** Bloque sur les règles `p/python`.
* **Trivy :** Exit code 1 pour `CRITICAL`.
* **Tests :** `pytest` bloque si échec fonctionnel.

## 5. Guide de Déploiement
* **Lancement manuel :** `docker run -p 5000:5000 travel-app`
* **Vérification :** Script `monitoring/smoke.sh`.



## Partie 3. Analyse des risques

### Objectif
Identifier les risques majeurs du système et les associer à des contrôles de sécurité automatisés intégrés dans la pipeline CI/CD (gates).

### Tableau 1 — Mapping risques → contrôles

| Risque | Exemple concret | Impact | Probabilité | Contrôle automatisé | Gate (seuil) |
|------|----------------|--------|-------------|---------------------|--------------|
| **Injection SQL** (Code) | Endpoint `/search` concatène `q` directement dans la requête SQL | Exfiltration de la base de données | Forte | **SAST (Semgrep)** | Findings ERROR > 0 ⇒ KO |
| **Command Injection** (Code) | Endpoint `/debug/run` utilise `subprocess` avec `shell=True` | Prise de contrôle du serveur (RCE) | Moyenne | **SAST (Semgrep)** | Findings ERROR > 0 ⇒ KO |
| **Path Traversal** (Code) | Endpoint `/report` permet de lire `/etc/passwd` | Divulgation de fichiers sensibles | Moyenne | **DAST (OWASP ZAP)** | Alerts High/Medium > 0 ⇒ KO |
| **Secrets en dur** (Config) | Clé `SECRET_KEY` et tokens stockés dans le code source | Accès non autorisé, compromission admin | Forte | **Secret Scanning (Gitleaks)** | Findings > 0 ⇒ KO |
| **Dépendance Vulnérable** (Supply Chain) | Librairie Python obsolète dans `requirements.txt` | Exploitation de CVE connues (RCE, DoS) | Moyenne | **SCA (Trivy FS)** | CRITICAL > 0 ⇒ KO |
| **Image Docker Vulnérable** (Supply Chain) | Image de base `python:3.7` contenant des failles OS | Compromission du conteneur | Moyenne | **Container Scan (Trivy Image)** | CRITICAL > 0 ⇒ KO |
| **Configuration Runtime** (Config) | Application lancée avec `debug=True` en Prod | Fuite de stacktrace et infos système | Faible | **SAST (Semgrep)** | Rule match ⇒ KO |
| **Exposition Réseau** (Infra) | Ports inutiles exposés dans Docker Compose | Surface d'attaque élargie | Faible | **Revue de Code (Manuel)** | Validation par paire requise |

### Tableau 2 — Limites de l’automatisation

| Risque | Limite / Point aveugle | Mesure compensatoire |
|------|------------------------|----------------------|
| **Logique Métier** | Les scanners ne détectent pas les bugs fonctionnels (ex: calcul de remise erroné) | Tests unitaires (`pytest`) et tests fonctionnels manuels |
| **Faux Positifs (SAST)** | Semgrep peut signaler du code légitime comme dangereux | Triage manuel et affinement des règles (`.semgrepignore`) |
| **Secrets Obfusqués** | Gitleaks cherche des motifs (entropie/regex), un mot de passe simple peut passer | Rotation régulière des secrets et utilisation de Vault |
| **Contexte Runtime** | L'analyse statique ne voit pas la configuration réelle du serveur déployé | Scan DAST régulier (ZAP) sur l'environnement de staging |

---

## Partie 4. Automatisation de la Sécurité (Pipeline CI/CD)

[cite_start]Le pipeline est orchestré via **GitHub Actions** et intègre 4 niveaux de contrôle automatisés[cite: 101].

### Outils intégrés
1.  [cite_start]**Gitleaks** : Scanne l'historique Git à la recherche de secrets avant même le build[cite: 102].
2.  [cite_start]**Semgrep** : Analyse le code Python pour détecter les patterns de vulnérabilité (SQLi, RCE)[cite: 103].
3.  [cite_start]**Trivy (FS & Image)** : Scanne les dépendances (`requirements.txt`) et l'image Docker finale pour les CVEs[cite: 104, 105].
4.  [cite_start]**OWASP ZAP** : Lance une attaque dynamique sur l'application en staging pour valider la résilience HTTP[cite: 106].

### Stratégie des Gates
Chaque scanner est configuré avec un seuil de blocage (**Gate**). [cite_start]Si une vulnérabilité critique est trouvée, le pipeline s'arrête immédiatement (Exit Code 1) et empêche le déploiement ou la validation de la Pull Request[cite: 63].

### Preuve d'efficacité (Avant / Après)
* 🔴 **Branche `vuln-demo`** : Le pipeline échoue à l'étape "Security Static" (Gitleaks/Semgrep) et "Container Security" (Trivy).
* 🟢 **Branche `main`** : Après correction du code (`app.py`) et mise à jour du Dockerfile, tous les voyants sont au vert.
