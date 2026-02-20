# 🍷 Élyos 

Ce projet consiste au développement et au déploiement d'une solution d'intelligence artificielle permettant de prédire la qualité d'un vin (score sur 10) en fonction de ses caractéristiques physico-chimiques et des données météorologiques de son millésime.

Le projet a été industrialisé pour répondre aux exigences de production (SRE), incluant une API RESTful robuste, de la validation de données (Pydantic), du monitoring applicatif (Loguru), et un packaging Docker.

## 🚀 Fonctionnalités
- **Pipeline de Données (ETL)** : Scraping, requêtes API météo et consolidation de datasets sur SQLite.
- **Machine Learning** : Modèle Random Forest entraîné sur des données combinées (chimie + météo).
- **API Backend** : Développée avec FastAPI, serveur Uvicorn performant.
- **Interface Web** : Formulaire HTML simple et accessible pour interagir avec le modèle interactif.
- **SRE & Résilience** : Gestion fine des erreurs (422 Bad Request), monitoring des requêtes, et simulation de pannes (Status 500).

---

## 💻 Comment Lancer le Projet

### Pré-requis
*   Python 3.11+
*   Docker & Docker Compose (Recommandé pour la production)

### Option 1 : Déploiement avec Docker (La plus rapide 🐳)
C'est la méthode recommandée. Elle lance le serveur avec la configuration de production (Fuseau horaire, volumes de logs, etc.).

Dans le terminal, à la racine du projet :
```bash
docker compose up -d --build
```
*   L'API et l'interface web seront accessibles à l'adresse : [http://localhost](http://localhost) ou [http://127.0.0.1](http://127.0.0.1).
*   Pour arrêter : `docker compose down`

### Option 2 : Lancement en Local (Environnement Virtuel 🐍)
Si vous souhaitez développer ou lancer sans Docker, il faut impérativement utiliser l'environnement virtuel pour que toutes les dépendances soient reconnues.

1.  **Créer / Activer l'environnement virtuel** :
    ```bash
    source .venv/bin/activate
    ```
2.  **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```
3.  **Lancer le serveur** :
    ```bash
    uvicorn src.api_model:app --port 8000 --reload
    ```
*   L'application sera accessible sur : [http://127.0.0.1:8000](http://127.0.0.1:8000)

*(Note: Si vous avez une erreur `Address already in use`, assurez-vous de couper l'ancien processus uvicorn ou docker qui tournerait en arrière-plan).*

---

## 🛠️ Outils & Technologies
*   **Backend / API** : Python, FastAPI, Pydantic, Uvicorn
*   **Machine Learning** : Scikit-learn, Pandas, Joblib
*   **Monitoring** : Loguru
*   **DevOps** : Docker, Pytest
*   **Frontend** : HTML/CSS/JS natif, Jinja2 Templates
