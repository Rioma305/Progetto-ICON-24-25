import sklearn
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import roc_auc_score
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import RepeatedKFold

from recommender_system import get_recommendation

#Funzione che esegue una Randomized Search degli hyperparameters del modello scelto
def RandomizedSearch(hyperparameters, X_train, y_train):

    knn = KNeighborsClassifier()

    #Utilizzo della cross validation per trovare il numero di fold
    cvFold = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
    randomSearch = RandomizedSearchCV(estimator=knn, cv=cvFold, param_distributions=hyperparameters)

    best_model = randomSearch.fit(X_train, y_train)

    return best_model

#Funzione che valuta una serie di metriche sul modello, come accuracy, recall f1 etc...
def modelEvaluation(y_test, y_pred, pred_prob):

    #Check delle metriche di validazione
    print('Classification report: \n', classification_report(y_test, y_pred))

    #Check performance del nostro modello con ROC score
    roc_score = roc_auc_score(y_test, pred_prob, multi_class='ovr')
    print('ROC score: ', roc_score)

    return roc_score

#Funzione che cerca i migliori hyperparameters in assoluto, ripetendo più volte la funzione che effettua la Randomized Search
#Restituisce un dizionario contenente hyperparameters e ROC score
def HyperparametersSearch(X_train, X_test, y_train, y_test):

    result = {}
    n_neighbors = list(range(1,30))
    weights = ['uniform', 'distance']
    metric = ['euclidean', 'manhattan', 'hamming']

    #Conversione ii dizionario
    hyperparameters = dict(metric=metric, weights=weights, n_neighbors=n_neighbors)

    i = 0
    while i < 15:
        best_model = RandomizedSearch(hyperparameters, X_train, y_train)

        bestweights = best_model.best_estimator_.get_params()['weights']

        bestMetric = best_model.best_estimator_.get_params()['metric']

        bestNeighbours = best_model.best_estimator_.get_params()['n_neighbors']

        knn = KNeighborsClassifier(n_neighbors=bestNeighbours, weights=bestweights, algorithm='auto', metric=bestMetric, metric_params=None, n_jobs=None)

        knn.fit(X_train,y_train)

        pred_prob = knn.predict_proba(X_test)

        #Valutiamo il modello con star come target
        roc_score = roc_auc_score(y_test, pred_prob, multi_class='ovr')

        #Farlo diventare un dataframe
        result[i] = {'n_neighbors' : bestNeighbours, 'metric' : bestMetric, 'weights' : bestweights, 'roc_score' : roc_score} 
        i += 1

    result = dict(sorted(result.items(), key = lambda x: x[1]['roc_score'], reverse=True))

    first_el = list(result.keys())[0]

    result = list(result[first_el].values())
    return result

#Funzione che cerca le migliori statistiche da applicare al modello scelto, valutando la performance man mano
def SearchingBestModelStats(X_train, X_test, y_train, y_test):

    print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
    print('\n\nIniziale composizione del modello con hyperparameters basici...')
    knn = KNeighborsClassifier(n_neighbors=5, weights='uniform', algorithm='auto', p=2, metric='minkowski', metric_params=None, n_jobs=None)

    knn.fit(X_train,y_train)

    #Mostra i primo 5 elementi predetti sul test data
    print('\nPredizioni dei primi 5 elementi: ',knn.predict(X_test)[0:5],'Valori effettivi: ', y_test[0:5])

    y_pred = knn.predict(X_test)

    pred_prob = knn.predict_proba(X_test)

    #Valutiamo il modello
    print('\nValutazione del modello...\n')
    modelEvaluation(y_test, y_pred, pred_prob)

    print('\nLa nostra accuratezza è bassa, dobbiamo migliorare la qualità delle nostre predizioni\n')
    print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')

    result = {}

    result = HyperparametersSearch(X_train, X_test, y_train, y_test)

    #Stampa dei migliori risultati ottenuti dalla ricerca degli hyperparameters
    print('\nWITH GRID SEARCH:\n')

    bestweights = result[2]
    print('Best weights:', bestweights)

    bestMetric = result[1]
    print('Best metric:', bestMetric)

    bestNeighbours = result[0]
    print('Best n_neighbors:', bestNeighbours)

    #Ricomposizione del modello con i nuovi parametri e valutazione dello stesso

    print('\nRicomponiamo il modello utilizzando i nuovi iperparametri...')

    knn = KNeighborsClassifier(n_neighbors=bestNeighbours, weights=bestweights, algorithm='auto', metric=bestMetric, metric_params=None, n_jobs=None)

    knn.fit(X_train,y_train)

    #Mostra i primo 5 elementi predetti sul test data
    print('\nPredizioni dei primi 5 elementi sulla categoria star: ',knn.predict(X_test)[0:5],'Valori effettivi: ', y_test[0:5])

    y_pred = knn.predict(X_test)

    pred_prob = knn.predict_proba(X_test)

    #Valutiamo il modello
    modelEvaluation(y_test, y_pred, pred_prob)

    print('\nAbbiamo incrementato la accuratezza del nostro modello')
    print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
    print('\nOra possiamo procedere alla fase di recommendation...')

    return knn

#Funzione main che gestisce la creazione dei dataset di training e test, li trasforma ed esegue predizione su nuovi dati passati
def main_recommender():
    steam_data = pd.read_csv('dataset/steam.csv')

    #Creiamo le categoria star
    steam_data['star'] = (steam_data['negative_ratings'] / steam_data['positive_ratings']) * 100

    #Assegniamo i dati alla sezione corretta
    steam_data.loc[(steam_data['star'] >= 0) & (steam_data['star'] <= 12.5), ['star']] = 5
    steam_data.loc[(steam_data['star'] > 12.5) & (steam_data['star'] <= 25), ['star']] = 4
    steam_data.loc[(steam_data['star'] > 25) & (steam_data['star'] <= 37.5), ['star']] = 3
    steam_data.loc[(steam_data['star'] > 37.5) & (steam_data['star'] <= 50), ['star']] = 2
    steam_data.loc[(steam_data['star'] > 50), ['star']] = 1

    steam_data['genres'] = steam_data['steamspy_tags']

    knn_data = steam_data[['appid', 'english', 'achievements', 'star','average_playtime','median_playtime', 'price']].copy()

    x = knn_data.drop(columns=['star'])

    y = knn_data['star'].values

    games_index = get_recommendation()

    recommend_data = steam_data[['name','genres','developer','price', 'star']].iloc[games_index]

    predict_data = steam_data[['appid', 'english', 'achievements','average_playtime','median_playtime', 'price']].iloc[games_index]

    #Splittiamo il dataset in due parti, training e test, con una ratio di 80% training e 20% test
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=1, stratify=y)

    #Trasformiamo i dati per renderli adeguati
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    predict_data = scaler.transform(predict_data)

    #Creiamo il nuovo modello usando gli hyperparameters nuovi e ottimali trovati
    knn = SearchingBestModelStats(X_train, X_test, y_train, y_test)

    #Alleniamo il modello sulla parte di training
    knn.fit(X_train,y_train)

    #Facciamo predizioni su dati nuovi
    predizione_star = knn.predict(predict_data)

    recommend_data['star_prediction'] = predizione_star

    print("\nEcco a te i 5 giochi più simili a quello proposto con una predizione sulla categoria star:\n",recommend_data, '\n')
    print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
