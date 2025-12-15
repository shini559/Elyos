import joblib
import pandas as pd
import os
import pytest
from src.api_model import WineFeatures

# Chemin vers le modèle
MODEL_PATH = "models/best_model.joblib"

@pytest.fixture
def model():
    """Fixture qui charge le modèle pour les tests."""
    if not os.path.exists(MODEL_PATH):
        pytest.skip(f"Modèle non trouvé à {MODEL_PATH}")
    return joblib.load(MODEL_PATH)

def test_model_loaded(model):
    """Vérifie que le modèle est bien chargé (pas None)."""
    assert model is not None

def test_model_prediction(model):
    """Vérifie que le modèle fait une prédiction valide sur des données typiques."""
    # Données d'exemple (fictives mais réalistes)
    input_data = {
        "fixed acidity": 7.4,
        "volatile acidity": 0.7,
        "citric acid": 0.0,
        "residual sugar": 1.9,
        "chlorides": 0.076,
        "free sulfur dioxide": 11.0,
        "total sulfur dioxide": 34.0,
        "density": 0.9978,
        "pH": 3.51,
        "sulphates": 0.56,
        "alcohol": 9.4,
        "temperature_2m_mean": 15.0,
        "rain_sum": 0.0
    }
    
    df = pd.DataFrame([input_data])
    prediction = model.predict(df)
    
    # Vérifications
    assert len(prediction) == 1
    assert isinstance(prediction[0], float)
    assert 0 <= prediction[0] <= 10  # Note de qualité du vin entre 0 et 10
