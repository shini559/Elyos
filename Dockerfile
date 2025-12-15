# Utiliser une image Python légère officielle
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier de dépendances
COPY requirements.txt .

# Installer les dépendances
# --no-cache-dir réduit la taille de l'image
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY src/ src/
COPY templates/ templates/
COPY static/ static/
COPY models/ models/
# Copier data si nécessaire, mais idéalement les données ne sont pas dans le conteneur de code
# Pour ce projet, on suppose que le modèle est déjà entraîné et dans models/

# Exposer le port 80
EXPOSE 80

# Commande de lancement de l'application
CMD ["uvicorn", "src.api_model:app", "--host", "0.0.0.0", "--port", "80"]
