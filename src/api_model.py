from fastapi import FastAPI, HTTPException, Request
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from loguru import logger
import sys
import pandas as pd
import joblib
import os

# --- Configuration Logging (Loguru) ---
logger.remove() # Enlever le handler par défaut
logger.add(sys.stderr, level="INFO") # Réajouter pour la console
logger.add("logs/elyos.log", rotation="1 day", level="INFO") # Fichier log quotidien

# --- Configuration & Chargement du Modèle ---

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Charge le modèle au démarrage
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"Modèle chargé depuis {MODEL_PATH}")
    else:
        print(f"ATTENTION: Modèle non trouvé à {MODEL_PATH}. L'API ne pourra pas faire de prédictions.")
    yield
    # Code à l'arrêt si nécessaire (rien ici)

app = FastAPI(title="Elyos Wine Quality API", description="API de prédiction de la qualité du vin.", version="1.0", lifespan=lifespan)

# [MONITORING] Capture des erreurs de validation (422) pour les logs
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Formattage simplifié des erreurs pour les logs
    error_messages = []
    for error in exc.errors():
        field = error["loc"][-1]  # Le dernier élément est le nom du champ (ex: 'alcohol')
        msg = error["msg"]
        error_messages.append(f"Erreur sur le champ '{field}': {msg}")
    
    formatted_log = " | ".join(error_messages)
    
    # On loggue l'erreur de façon lisible
    logger.warning(f"Rejet 422 (Validation) : {formatted_log}")
    
    # On renvoie la réponse standard 422
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# Montage des fichiers statiques (CSS, JS, Images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration des templates (Jinja2)
templates = Jinja2Templates(directory="templates")

MODEL_PATH = "models/best_model.joblib"
model = None

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
    alcohol: float = Field(..., le=20.0, description="Taux d'alcool (max 20%)")
    temperature: float  # Sera renommé en temperature_2m_mean
    rain: float         # Sera renommé en rain_sum

# --- Endpoints ---

@app.get("/")
def read_root(request: Request):
    """Endpoint de base pour vérifier que l'API est en ligne."""
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/predict")
def predict_quality(features: WineFeatures):
    """
    Reçoit les caractéristiques du vin et retourne la qualité prédite.
    """
    # [MONITORING] Log de la requête entrante
    logger.info(f"Prédiction demandée pour un vin avec Alcool={features.alcohol}, Acidité={features.fixed_acidity}, Temp={features.temperature}")

    # [INCIDENT] Le check manuel a été remplacé par une validation Pydantic.
    # Si alcohol > 20, FastAPI renvoie automatiquement une 422 (Bad Request).
    
    if model is None:
        logger.error("Tentative de prédiction alors que le modèle n'est pas chargé.")
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
        predicted_score = float(prediction[0])
        
        # [MONITORING] Log du succès
        logger.success(f"Prédiction envoyée : {predicted_score:.2f}/10")
        
        return {"predicted_quality": predicted_score}
    except Exception as e:
        logger.error(f"Erreur interne du modèle : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction: {str(e)}")

# Comme demandé, ce commentaire justifie l'architecture REST :
# L'architecture REST est choisie ici pour sa simplicité, sa standardisation (HTTP, JSON) 
# et sa compatibilité universelle. FastAPI permet de créer rapidement des endpoints performants (asynchrones)
# avec une validation automatique des données via Pydantic, ce qui est crucial pour un service ML 
# afin d'éviter les erreurs de types ou de format en entrée de modèle.
