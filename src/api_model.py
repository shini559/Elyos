from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import pandas as pd
import joblib
import os

# --- Configuration & Chargement du Modèle ---

app = FastAPI(title="Elyos Wine Quality API", description="API de prédiction de la qualité du vin.", version="1.0")

# Montage des fichiers statiques (CSS, JS, Images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration des templates (Jinja2)
templates = Jinja2Templates(directory="templates")

MODEL_PATH = "models/best_model.joblib"
model = None

@app.on_event("startup")
def load_model():
    """Charge le modèle au démarrage de l'application."""
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"Modèle chargé depuis {MODEL_PATH}")
    else:
        print(f"ATTENTION: Modèle non trouvé à {MODEL_PATH}. L'API ne pourra pas faire de prédictions.")

# --- Schémas de Données (Pydantic) ---

class WineFeatures(BaseModel):
    """
    Définit les caractéristiques attendues pour la prédiction.
    Les types sont tous float pour simplifier, c'est ce qu'attend le modèle.
    """
    fixed_acidity: float
    volatile_acidity: float
    citric_acid: float
    residual_sugar: float
    chlorides: float
    free_sulfur_dioxide: float
    total_sulfur_dioxide: float
    density: float
    pH: float
    sulphates: float
    alcohol: float
    temperature: float  # Sera renommé en temperature_2m_mean
    rain: float         # Sera renommé en rain_sum

# --- Endpoints ---

@app.get("/")
def read_root(request: Request):
    """Endpoint de base pour vérifier que l'API est en ligne."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
def predict_quality(features: WineFeatures):
    """
    Reçoit les caractéristiques du vin et retourne la qualité prédite.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Le modèle n'est pas chargé.")

    # Conversion des données en DataFrame
    data_dict = features.dict()
    df = pd.DataFrame([data_dict])

    # Renommage des colonnes pour correspondre à celles utilisées lors de l'entraînement
    df = df.rename(columns={
        "fixed_acidity": "fixed acidity",
        "volatile_acidity": "volatile acidity",
        "citric_acid": "citric acid",
        "residual_sugar": "residual sugar",
        "free_sulfur_dioxide": "free sulfur dioxide",
        "total_sulfur_dioxide": "total sulfur dioxide",
        "temperature": "temperature_2m_mean",
        "rain": "rain_sum"
    })

    # Prédiction
    try:
        prediction = model.predict(df)
        return {"predicted_quality": float(prediction[0])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction: {str(e)}")

# Comme demandé, ce commentaire justifie l'architecture REST :
# L'architecture REST est choisie ici pour sa simplicité, sa standardisation (HTTP, JSON) 
# et sa compatibilité universelle. FastAPI permet de créer rapidement des endpoints performants (asynchrones)
# avec une validation automatique des données via Pydantic, ce qui est crucial pour un service ML 
# afin d'éviter les erreurs de types ou de format en entrée de modèle.
