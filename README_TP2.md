# Rapport de Réalisation : TP2 – Observabilité et Sécurité Runtime

## 1. Introduction et Problématique
Dans le cadre du premier TP, nous avons sécurisé l'application de manière **statique** (SAST avec Semgrep, Secret Scanning avec Gitleaks, SCA avec Trivy) afin de garantir l'intégrité du code source et de l'image Docker. Cependant, ces méthodes ne permettent pas de détecter les comportements anormaux survenant lors de l'exécution (erreurs de base de données, instabilité de l'infrastructure) ou les tentatives d'intrusion actives.

L'objectif de ce TP2 était donc de compléter notre chaîne **DevSecOps** par une couche d'**observabilité** et une **Security Runtime Gate** capable de valider ou de bloquer un déploiement en fonction du comportement réel de l'application en environnement de staging.

## 2. Implémentation de l'Observabilité
La première étape a consisté à rendre l'application "parlante". Nous avons abandonné les logs textuels standards pour un **Logging JSON structuré**. 

Chaque requête traitée par l'application Flask produit désormais une entrée JSON contenant :
* **Traçabilité** : Un `request_id` unique généré via UUID pour corréler les logs et faciliter le debug.
* **Performance** : La latence exacte en millisecondes (`latency_ms`) pour chaque endpoint.
* **Sécurité** : La capture des paramètres de requête (`query`) permettant d'analyser d'éventuels vecteurs d'attaque.

## 3. Développement de la Security Runtime Gate
Pour automatiser la validation du déploiement, nous avons conçu un système en trois composants interdépendants :

### A. Générateur de Trafic (`traffic.sh`)
Ce script simule une activité utilisateur diversifiée immédiatement après le déploiement. Il génère du trafic légitime (navigation, recherche) mais possède également un **Mode Suspect** (`SUSPECT_MODE=1`) pour simuler des attaques de type **Path Traversal** (`../`) ou des injections de commandes système (`cmd=`).

### B. Analyseur de Métriques (`log_metrics.py`)
Ce module Python extrait les journaux du conteneur Docker et calcule les indicateurs clés de performance (KPI) et de sécurité :
* **Fiabilité** : Décompte des erreurs HTTP 5xx (Internal Server Error).
* **Performance** : Calcul de la latence **P95** (95ème centile) pour identifier les ralentissements critiques.
* **Détection d'Intrusion** : Analyse de motifs (regex) pour repérer des tentatives d'accès aux fichiers sensibles ou d'exécution de code.

### C. La Gate de Contrôle (`log_gate.sh`)
Le script de "Gate" orchestre l'analyse. Il compare les métriques observées à des seuils définis (ex: `MAX_5XX=5`). Si un seuil est dépassé ou si une attaque est détectée, le script renvoie un code d'erreur (exit 1), ce qui provoque l'échec du job dans la CI/CD.

## 4. Intégration dans le Pipeline CI/CD (GitHub Actions)
Le workflow GitHub Actions a été mis à jour pour inclure ce job de **Runtime Monitoring** après l'étape de build :

1. **Isolation** : L'environnement de staging est lancé via `docker compose` pour isoler les logs.
2. **Exécution** : La gate lance les tests de trafic et analyse les résultats.
3. **Persistance** : Un rapport JSON (`log_report.json`) et les rapports de métriques sont archivés en tant qu'**artefacts** GitHub pour permettre un audit après incident, même si la gate a échoué.



## 5. Conclusion
L'implémentation de cette **Runtime Gate** permet de passer d'une posture de sécurité passive à une posture **active et résiliente**. Nous garantissons désormais que toute version de l'application déployée est non seulement exempte de vulnérabilités connues dans son code, mais qu'elle se comporte également de manière stable et sécurisée face à un trafic réel.
