import requests
import os

def extract_csv():
    """
    Télécharge le dataset "Wine Quality" (Red Wine) depuis le dépôt UCI.
    Sauvegarde le fichier brut dans data/raw/wine_quality.csv.
    """
    # URL du fichier CSV source
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
    
    # Chemin de destination (relatif à la racine du projet, supposé être le parent de src/)
    # On remonte d'un niveau depuis src/ pour atteindre la racine data_pipeline/ puis data/raw/
    # Ou plus simplement, on assume que le script est lancé depuis la racine du projet
    output_path = os.path.join("data_pipeline", "data", "raw", "wine_quality.csv")
    
    # Création du dossier parent si nécessaire (sécurité supplémentaire)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Début du téléchargement depuis {url}...")
    
    try:
        # Envoi de la requête GET
        response = requests.get(url)
        
        # Vérification du statut de la réponse (lève une erreur si 4xx ou 5xx)
        response.raise_for_status()
        
        # Écriture du contenu dans le fichier destination
        with open(output_path, 'wb') as file:
            file.write(response.content)
            
        print(f"Succès : Le fichier a été sauvegardé sous '{output_path}'.")
        
    except requests.exceptions.RequestException as e:
        # Gestion des erreurs de connexion ou HTTP
        print(f"Erreur lors du téléchargement : {e}")
    except OSError as e:
        # Gestion des erreurs liées au système de fichiers
        print(f"Erreur lors de la sauvegarde du fichier : {e}")

if __name__ == "__main__":
    extract_csv()
