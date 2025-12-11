import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re

def extract_scraping():
    """
    Scrape la page Wikipedia "Bordeaux Wine Official Classification of 1855" pour extraire la classification.
    Sauvegarde les données dans data/raw/bordeaux_1855.csv.
    """
    # Nouvelle URL cible
    url = "https://en.wikipedia.org/wiki/List_of_wine-producing_countries"
    
    # Chemin de destination (modifié pour refléter le nouveau contenu)
    output_path = os.path.join("data_pipeline", "data", "raw", "wine_production_by_country.csv")
    
    # Création du dossier parent si nécessaire
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Scraping de la page {url}...")
    
    try:
        # Ajout d'un User-Agent pour éviter le blocage 403 (pratique courante sur Wikipedia)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        data = []
        
        # Recherche des tables de classification (souvent classe 'wikitable')
        tables = soup.find_all('table', class_='wikitable')
        
        if tables:
            print(f"Nombre de tableaux trouvés : {len(tables)}")
            
            for i, table in enumerate(tables):
                # Essayer de déterminer la catégorie (par ex: Premier Cru)
                # On regarde le titre précédent ou juste on indexe
                category = f"Table_{i+1}"
                
                rows = table.find_all('tr')
                # Extraction des en-têtes pour comprendre la structure
                headers_list = [th.text.strip() for th in table.find_all('th')]
                
                for row in rows:
                    cols = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols]
                    
                    # On s'attend généralement à Nom du Château, Commune/AOC
                    if len(cols) >= 2:
                        # Nettoyage basique (suppression des références [1], [a] etc.)
                        clean_cols = [re.sub(r'\[.*?\]', '', c) for c in cols]
                        
                        entry = {
                            'Category_Index': category,
                            'Raw_Data_1': clean_cols[0],
                            'Raw_Data_2': clean_cols[1]
                        }
                        if len(clean_cols) > 2:
                             entry['Raw_Data_3'] = clean_cols[2]
                        
                        data.append(entry)

        # Création du DataFrame
        if data:
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False)
            print(f"Succès : {len(df)} enregistrements extraits et sauvegardés sous '{output_path}'.")
            print(df.head())
        else:
            print("Avertissement : Aucune donnée tabulaire n'a pu être extraite.")
            
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion lors du scraping : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")

if __name__ == "__main__":
    extract_scraping()
