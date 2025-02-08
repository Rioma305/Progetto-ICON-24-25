import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

#Caricamento dell dataset
df = pd.read_csv("dataset/steam.csv")

#Creazione di una nuova feature che combina positive e negative ratings
def calculate_rating_score(positive, negative):
    total = positive + negative
    if total == 0:
        return 0
    return (positive / total) * 5

df["rating_score"] = df.apply(lambda row: calculate_rating_score(row["positive_ratings"], row["negative_ratings"]), axis=1)

#Preprocessing: rimuozione di colonne non necessarie
columns_to_drop = ["appid", "name", "release_date", "owners", "positive_ratings", "negative_ratings"]
df = df.drop(columns=columns_to_drop)

#Separazione target e features
y = df["rating_score"]
X = df.drop(columns=["rating_score"])

#Selezione feature numeriche e categoriche
num_features = ["required_age", "achievements", "average_playtime", "median_playtime"]
cat_features = ["developer", "publisher", "platforms", "categories", "genres", "steamspy_tags"]

#Rimozione righe con valori NaN
X = X.dropna()
y = y[X.index]

#Divisione dei dati: Training (60%), Tuning (20%), Test (20%)
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.4, random_state=42)
X_tune, X_test, y_tune, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

#Preprocessing: StandardScaler per feature numeriche e OneHotEncoder per feature categoriche
preprocessor = ColumnTransformer([
    ("num", StandardScaler(), num_features),
    ("cat", OneHotEncoder(handle_unknown='ignore'), cat_features)
])

#Definizione dei modelli
models = {
    "Random Forest": RandomForestRegressor(random_state=42),
    "Gradient Boosting": GradientBoostingRegressor(random_state=42)
}

#Definizione dei parametri per la ricerca degli iperparametri
#(per RandomForest è stato rimosso il valore 'auto' per max_features)
param_grid = {
    "Random Forest": {
        "model__n_estimators": [50, 100, 200],
        "model__max_depth": [None, 10, 20, 30],
        "model__min_samples_split": [2, 5, 10],
        "model__min_samples_leaf": [1, 2, 4],
        "model__max_features": ["sqrt", "log2"]
    },
    "Gradient Boosting": {
        "model__n_estimators": [50, 100, 200],
        "model__learning_rate": [0.01, 0.05, 0.1],
        "model__max_depth": [3, 5, 7],
        "model__min_samples_split": [2, 4],
        "model__subsample": [0.8, 1.0]
    }
}

results = {}

#Per ciascun modello, esecuzione della ricerca degli iperparametri e creazione di una pipeline finale
for name, model in models.items():
    #Costruzione della pipeline (preprocessor + modello)
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model)
    ])
    
    #Esecuzione GridSearchCV sulla porzione di tuning
    grid_search = GridSearchCV(pipeline, param_grid[name], cv=5,
                               scoring="neg_mean_squared_error", n_jobs=-1)
    grid_search.fit(X_tune, y_tune)
    best_parameters = grid_search.best_params_
    print(f"{name} - Best Parameters: {best_parameters}")
    
    #Utilizzo diretto della pipeline ottimizzata
    best_pipeline = grid_search.best_estimator_
    
    #Riadattamento della pipeline sul training set (X_train, y_train)
    # Il preprocessor verrà adattato solo su X_train e poi applicato ad X_test
    best_pipeline.fit(X_train, y_train)
    
    #Valutazione sul Test Set
    
    y_pred = best_pipeline.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    results[name] = (best_pipeline, mse)
    print(f"{name} - Evaluation Metrics:")
    print(f"MSE: {mse:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")
    print(f"R2 Score: {r2:.4f}")

#Funzione per il grafico della learning curve
def plot_learning_curve(model, X, y, title):
    #Utilizzo di un intervallo da 0.1 a 0.9 per evitare il valore 1.0
    train_sizes = np.linspace(0.1, 0.9, 10)
    train_scores, test_scores = [], []
    
    for size in train_sizes:
        X_train_part, _, y_train_part, _ = train_test_split(X, y, train_size=float(size), random_state=42)
        
        model_copy = Pipeline([
            ("preprocessor", model.named_steps["preprocessor"]),
            ("model", model.named_steps["model"])
        ])
        model_copy.fit(X_train_part, y_train_part)
        
        train_pred = model_copy.predict(X_train_part)
        test_pred = model_copy.predict(X_test)
        
        train_scores.append({
            'mse': mean_squared_error(y_train_part, train_pred),
            'std': np.std(train_pred),
            'var': np.var(train_pred)
        })
        test_scores.append({
            'mse': mean_squared_error(y_test, test_pred),
            'std': np.std(test_pred),
            'var': np.var(test_pred)
        })

    #Creazione dei subplot
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))
    
    #Plot MSE
    ax1.plot(train_sizes, [s['mse'] for s in train_scores], label="Training Error")
    ax1.plot(train_sizes, [s['mse'] for s in test_scores], label="Validation Error")
    ax1.set_xlabel("Training Size")
    ax1.set_ylabel("MSE")
    ax1.set_title(f"{title} - Mean Squared Error")
    ax1.legend()
    
    #Plot Standard Deviation
    ax2.plot(train_sizes, [s['std'] for s in train_scores], label="Training Std")
    ax2.plot(train_sizes, [s['std'] for s in test_scores], label="Validation Std")
    ax2.set_xlabel("Training Size")
    ax2.set_ylabel("Standard Deviation")
    ax2.set_title(f"{title} - Standard Deviation")
    ax2.legend()
    
    #Plot Variance
    ax3.plot(train_sizes, [s['var'] for s in train_scores], label="Training Variance")
    ax3.plot(train_sizes, [s['var'] for s in test_scores], label="Validation Variance")
    ax3.set_xlabel("Training Size")
    ax3.set_ylabel("Variance")
    ax3.set_title(f"{title} - Variance")
    ax3.legend()
    
    plt.tight_layout()
    plt.savefig(f"{title}_metrics.png")
    plt.show()
    
    #Stampa dei valori finali
    print(f"\n{title} - Final Metrics:")
    print("Training Set:")
    print(f"MSE: {train_scores[-1]['mse']:.4f}")
    print(f"Standard Deviation: {train_scores[-1]['std']:.4f}")
    print(f"Variance: {train_scores[-1]['var']:.4f}")
    print("\nValidation Set:")
    print(f"MSE: {test_scores[-1]['mse']:.4f}")
    print(f"Standard Deviation: {test_scores[-1]['std']:.4f}")
    print(f"Variance: {test_scores[-1]['var']:.4f}")

#Generazione dei grafici delle learning curve
for name, (model, _) in results.items():
    plot_learning_curve(model, X_train, y_train, title=f"Learning Curve - {name}")