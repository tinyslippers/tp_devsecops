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
