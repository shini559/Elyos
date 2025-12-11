import pandas as pd
import sqlite3
import numpy as np
import os
import logging
import random

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(filepath, sep=','):
    """
    Charge un fichier CSV dans un DataFrame Pandas.
    Gère les erreurs si le fichier n'existe pas.
    """
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Le fichier {filepath} est introuvable.")
        
        df = pd.read_csv(filepath, sep=sep)
        logging.info(f"Fichier chargé avec succès : {filepath} ({len(df)} lignes)")
        return df
    except Exception as e:
        logging.error(f"Erreur lors du chargement de {filepath} : {e}")
        return None

def clean_augment_wine(df_wine):
    """
    Nettoie et augmente les données de vin.
    - Ajoute une colonne 'year' avec une année aléatoire entre 2010 et 2020.
    """
    logging.info("Début du nettoyage et augmentation des données Vin...")
    
    # Data Augmentation : Année aléatoire entre 2010 et 2020
    # Utilisation de np.random.randint pour la performance sur tout le tableau
    df_wine['year'] = np.random.randint(2010, 2021, size=len(df_wine))
    
    logging.info("Augmentation terminée : Colonne 'year' ajoutée.")
    return df_wine

def clean_aggregate_meteo(df_meteo):
    """
    Nettoie et agrège les données météo.
    - Convertit la date en année.
    - Agrège par année : Moyenne température, Somme pluie.
    """
    logging.info("Début du nettoyage et agrégation des données Météo...")
    
    # Conversion en datetime si ce n'est pas déjà le cas
    if 'time' in df_meteo.columns:
        df_meteo['date'] = pd.to_datetime(df_meteo['time'])
    elif 'date' in df_meteo.columns:
        df_meteo['date'] = pd.to_datetime(df_meteo['date'])
    
    # Extraction de l'année
    df_meteo['year'] = df_meteo['date'].dt.year
    
    # Agrégation
    df_agg = df_meteo.groupby('year').agg({
        'temperature_2m_mean': 'mean',
        'rain_sum': 'sum'
    }).reset_index()
    
    logging.info(f"Agrégation terminée : {len(df_agg)} années météo disponibles.")
    return df_agg

def clean_countries(df_country):
    """
    Nettoie les données de production par pays.
    - Renomme les colonnes.
    - Nettoie les noms de pays (strip).
    - Convertit la production en entier numérique.
    """
    logging.info("Début du nettoyage des données Pays...")
    
    # Renommage pour clarté, basé sur les données observées : Raw_Data_1 -> pays, Raw_Data_2 -> volume
    # Supposons que Raw_Data_1 est le pays et Raw_Data_2 la production, basé sur le head du fichier
    df_country = df_country.rename(columns={
        'Raw_Data_1': 'pays',
        'Raw_Data_2': 'volume_production'
    })
    
    # Nettoyage des noms de pays
    df_country['pays'] = df_country['pays'].astype(str).str.strip()
    
    # Nettoyage de la production (enlever espaces, virguless, etc. pour conversion int)
    # Exemple "5,088,500" -> 5088500
    if df_country['volume_production'].dtype == object:
        df_country['volume_production'] = df_country['volume_production'].astype(str).str.replace(',', '').str.replace(' ', '')
        # Conversion en numeric, coerce errors pour les valeurs non convertibles
        df_country['volume_production'] = pd.to_numeric(df_country['volume_production'], errors='coerce').fillna(0).astype(int)
    
    # Sélection des colonnes utiles
    df_final = df_country[['pays', 'volume_production']]
    
    logging.info("Nettoyage Pays terminé.")
    return df_final

def merge_data(df_wine, df_meteo):
    """
    Fusionne les données Vin et Météo sur l'année (Left Join).
    """
    logging.info("Fusion des données Vin et Météo...")
    
    merged_df = pd.merge(df_wine, df_meteo, on='year', how='left')
    
    logging.info(f"Fusion terminée. Taille finale : {len(merged_df)} lignes.")
    return merged_df

def save_to_db(df_vins, df_pays, db_path):
    """
    Sauvegarde les DataFrames dans une base SQLite.
    Crée les tables avec un schéma défini.
    """
    logging.info(f"Sauvegarde dans la base de données : {db_path}")
    
    try:
        # Création du dossier si inexistant (au cas où)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # --- Table vins_enrichis ---
        # On recrée la table pour être propres
        cursor.execute("DROP TABLE IF EXISTS vins_enrichis")
        
        # Création table vins_enrichis
        # Note: id est ajouté automatiquement si on ne le spécifie pas dans to_sql avec index=False, mais on veut une PRIMARY KEY explicite.
        # Le plus simple avec pandas to_sql est de laisser pandas créer la table ou de créer la table avant et d'append.
        # Ici, on va utiliser to_sql pour la simplicité, mais on va s'assurer que index=False et on ne chargera pas 'id' si on veut l'autoincrément par la DB.
        # Cependant, le user demande "Ajoute une Clé Primaire id". Pandas to_sql ne crée pas de PK par défaut.
        
        create_vins_table = """
        CREATE TABLE vins_enrichis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            "fixed acidity" REAL,
            "volatile acidity" REAL,
            "citric acid" REAL,
            "residual sugar" REAL,
            chlorides REAL,
            "free sulfur dioxide" REAL,
            "total sulfur dioxide" REAL,
            density REAL,
            pH REAL,
            sulphates REAL,
            alcohol REAL,
            quality INTEGER,
            year INTEGER,
            temperature_2m_mean REAL,
            rain_sum REAL
        );
        """
        cursor.execute(create_vins_table)
        
        # Insertion des données (append)
        df_vins.to_sql('vins_enrichis', conn, if_exists='append', index=False)
        logging.info(f"{len(df_vins)} lignes insérées dans 'vins_enrichis'.")
        
        # --- Table referentiel_pays ---
        cursor.execute("DROP TABLE IF EXISTS referentiel_pays")
        
        create_pays_table = """
        CREATE TABLE referentiel_pays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pays TEXT,
            volume_production INTEGER
        );
        """
        cursor.execute(create_pays_table)
        
        df_pays.to_sql('referentiel_pays', conn, if_exists='append', index=False)
        logging.info(f"{len(df_pays)} lignes insérées dans 'referentiel_pays'.")
        
        conn.commit()
        conn.close()
        logging.info("Base de données mise à jour avec succès.")
        
    except Exception as e:
        logging.error(f"Erreur lors de la sauvegarde en BDD : {e}")

def main():
    # Chemins des fichiers
    base_dir = "data_pipeline/data"
    path_wine = os.path.join(base_dir, "raw/wine_quality.csv")
    path_meteo = os.path.join(base_dir, "raw/meteo_bordeaux.csv")
    path_country = os.path.join(base_dir, "raw/wine_production_by_country.csv")
    db_path = os.path.join(base_dir, "viti_quality.db")
    
    # 1. Chargement
    df_wine = load_data(path_wine, sep=';') # wine_quality est souvent point-virgule
    df_meteo = load_data(path_meteo, sep=',')
    df_country = load_data(path_country, sep=',')
    
    if df_wine is None or df_meteo is None or df_country is None:
        logging.error("Arrêt du script : Un ou plusieurs fichiers manquants.")
        return

    # 2. Nettoyage & Augmentation
    df_wine = clean_augment_wine(df_wine)
    df_meteo_agg = clean_aggregate_meteo(df_meteo)
    df_country_clean = clean_countries(df_country)
    
    # 3. Fusion Vin + Météo
    df_final_wines = merge_data(df_wine, df_meteo_agg)
    
    # 4. Sauvegarde BDD
    save_to_db(df_final_wines, df_country_clean, db_path)

if __name__ == "__main__":
    main()
