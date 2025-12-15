import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

def train():
    # 1. Chargement des données
    db_path = 'data_pipeline/data/viti_quality.db'
    if not os.path.exists(db_path):
        print(f"Erreur: La base de données n'existe pas à l'emplacement: {db_path}")
        # Fallback check if the user meant data/viti_quality.db relative to current dir if they moved it
        if os.path.exists('data/viti_quality.db'):
             db_path = 'data/viti_quality.db'
             print(f"Base de données trouvée à: {db_path}")
        else:
             return

    print(f"Chargement des données depuis {db_path}...")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM vins_enrichis", conn)
    conn.close()

    # 2. Préparation (Features/Target)
    features = [
        'fixed acidity', 'volatile acidity', 'citric acid', 'residual sugar',
        'chlorides', 'free sulfur dioxide', 'total sulfur dioxide', 'density',
        'pH', 'sulphates', 'alcohol', 'temperature_2m_mean', 'rain_sum'
    ]
    target = 'quality'

    # Vérification des colonnes
    missing_cols = [col for col in features if col not in df.columns]
    if missing_cols:
        print(f"Erreur: Colonnes manquantes dans la base de données: {missing_cols}")
        return

    X = df[features]
    y = df[target]

    # 3. Split
    print("Séparation des données (Train 80% / Test 20%)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Benchmark (Compétence C7)
    print("Entraînement des modèles...")
    
    # Modèle 1: Régression Linéaire
    # Nous utilisons la régression linéaire comme baseline simple pour comparer avec des méthodes plus complexes.
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    mse_lr = mean_squared_error(y_test, y_pred_lr)
    r2_lr = r2_score(y_test, y_pred_lr)

    # Modèle 2: Random Forest
    # Nous testons Random Forest car il gère mieux les relations non-linéaires et les interactions entre variables.
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    mse_rf = mean_squared_error(y_test, y_pred_rf)
    r2_rf = r2_score(y_test, y_pred_rf)

    # 5. Évaluation
    print("\n--- RÉSULTATS DU BENCHMARK ---")
    print(f"Linear Regression: MSE={mse_lr:.4f}, R2={r2_lr:.4f}")
    print(f"Random Forest:     MSE={mse_rf:.4f}, R2={r2_rf:.4f}")

    # 6. Sélection & Sauvegarde (Compétence C8)
    best_model = None
    best_name = ""
    best_r2 = -float('inf')

    if r2_rf > r2_lr:
        best_model = rf
        best_name = "Random Forest"
        best_r2 = r2_rf
    else:
        best_model = lr
        best_name = "Linear Regression"
        best_r2 = r2_lr

    print(f"\nLe meilleur modèle est : {best_name} (R2={best_r2:.4f})")

    # Sauvegarde
    models_dir = 'models'
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, 'best_model.joblib')
    joblib.dump(best_model, model_path)
    print(f"Modèle sauvegardé dans : {model_path}")

if __name__ == "__main__":
    train()
