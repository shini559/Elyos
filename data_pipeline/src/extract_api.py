import requests
import pandas as pd
import os

def extract_api():
    """
    Récupère l'historique météo pour Bordeaux via l'API Open-Meteo.
    Sauvegarde les données au format CSV dans data/raw/meteo_bordeaux.csv.
    """
    # URL de base de l'API
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    # Paramètres de la requête pour Bordeaux (2010-2020)
    params = {
        "latitude": 44.8,
        "longitude": -0.5,
        "start_date": "2010-01-01",
        "end_date": "2020-12-31",
        "daily": "temperature_2m_mean,rain_sum"
    }
    
    # Chemin de destination
    output_path = os.path.join("data_pipeline", "data", "raw", "meteo_bordeaux.csv")
    
    # Création du dossier parent si nécessaire
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Interrogation de l'API Open-Meteo pour Bordeaux...")
    
    try:
        # Appel API
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Traitement de la réponse JSON
        data = response.json()
        
        # Extraction des données journalières
        daily_data = data.get('daily', {})
        
        # Création d'un DataFrame Pandas
        # Les clés du dictionnaire 'daily' correspondent aux colonnes attendues (time, temperature_2m_mean, rain_sum)
        df = pd.DataFrame(daily_data)
        
        # Sauvegarde en CSV
        df.to_csv(output_path, index=False)
        
        print(f"Succès : Les données météo ont été sauvegardées sous '{output_path}'.")
        print(f"Dimensions du dataset : {df.shape}")
        
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion à l'API : {e}")
    except ValueError as e:
        print(f"Erreur lors du traitement des données JSON : {e}")
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")

if __name__ == "__main__":
    extract_api()
