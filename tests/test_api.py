from fastapi.testclient import TestClient
from src.api_model import app

def test_read_root():
    """Vérifie que la route racine renvoie la page HTML (status 200)."""
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Élyos" in response.text

def test_predict_endpoint():
    """Vérifie que l'endpoint de prédiction fonctionne avec des données JSON valides."""
    payload = {
        "fixed_acidity": 7.4,
        "volatile_acidity": 0.7,
        "citric_acid": 0.0,
        "residual_sugar": 1.9,
        "chlorides": 0.076,
        "free_sulfur_dioxide": 11.0,
        "total_sulfur_dioxide": 34.0,
        "density": 0.9978,
        "pH": 3.51,
        "sulphates": 0.56,
        "alcohol": 9.4,
        "temperature": 15.0,
        "rain": 0.0
    }
    
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "predicted_quality" in data
        assert isinstance(data["predicted_quality"], float)
