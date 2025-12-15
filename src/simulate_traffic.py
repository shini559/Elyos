import requests
import random
import time
from loguru import logger

# Configuration
API_URL = "http://localhost:80/predict"
N_REQUESTS = 50   # Nombre de requêtes à simuler (ou infini si while True)
DELAY = 0.5       # Délai entre requêtes en secondes

def generate_random_wine():
    """Génère un vin avec des caractéristiques aléatoires réalistes."""
    return {
        "fixed_acidity": round(random.uniform(5.0, 15.0), 1),
        "volatile_acidity": round(random.uniform(0.1, 1.5), 2),
        "citric_acid": round(random.uniform(0.0, 1.0), 2),
        "residual_sugar": round(random.uniform(0.9, 15.0), 1),
        "chlorides": round(random.uniform(0.01, 0.2), 3),
        "free_sulfur_dioxide": round(random.uniform(5, 70), 0),
        "total_sulfur_dioxide": round(random.uniform(10, 250), 0),
        "density": round(random.uniform(0.990, 1.005), 4),
        "pH": round(random.uniform(2.8, 4.0), 2),
        "sulphates": round(random.uniform(0.3, 1.5), 2),
        "alcohol": round(random.uniform(8.0, 15.0), 1), # Normal
        "temperature": round(random.uniform(10.0, 30.0), 1),
        "rain": round(random.uniform(0.0, 1000.0), 1)
    }

def simulate():
    logger.info(f"Démarrage de la simulation de trafic vers {API_URL}...")
    
    for i in range(N_REQUESTS):
        wine_data = generate_random_wine()
        
        # Introduction aléatoire de l'incident (1 chance sur 20)
        if random.random() < 0.05:
            logger.warning(">>> Simulation d'une attaque/erreur : Alcool=150 <<<")
            wine_data["alcohol"] = 150.0

        try:
            response = requests.post(API_URL, json=wine_data)
            status = response.status_code
            
            if status == 200:
                result = response.json()
                logger.success(f"Req #{i+1}: OK | Qualité prédite: {result.get('predicted_quality')}")
            elif status == 500:
                logger.error(f"Req #{i+1}: ERREUR 500 (Incident non géré)")
            elif status == 422:
                logger.success(f"Req #{i+1}: REJETÉ 422 (Validation Pydantic active - Protection OK)")
            else:
                logger.warning(f"Req #{i+1}: Status {status}")
                
        except Exception as e:
            logger.error(f"Erreur de connexion : {e}")
        
        time.sleep(DELAY)

if __name__ == "__main__":
    simulate()
