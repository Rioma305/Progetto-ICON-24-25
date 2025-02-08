from recommender_system import vectorize_data
import numpy as np
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import euclidean_distances
from scipy.stats import pearsonr
import time

#Funzione che esegue una raccomandazione di giochi, utilizzando come metrica per il calcolo di similarità il coseno e si ricava la quantità di tempo utilizzata
#per l'elaborazione
def recommend_cosine(data):

    nome = "Team Fortress Classic"
    index = data.index[data['name'] == nome].values[0]
    
    #Definisce le categorie che si vuole usare e unisce in una, per poter applicare il tf-idf
    data['all_content'] = data['name'] + ';' + data['developer'] + ';' + data['publisher'] + ';' + data['platforms'] + ';' + data['genres'] 
    
    start = time.time()

    tfidf_matrix = vectorize_data(data)

    #Costruzione della similarità del coseno da applicare poi alla matrice creata
    cosine_similarity = linear_kernel(tfidf_matrix, tfidf_matrix) 

    indices = pd.Series(data['name'].index)

    id = indices[index]

    #Ottiene i punteggi di similarità tra tutti i giochi rispetto a quello selezionato, li ordina e ne ottiene i primi 5
    similarity_scores = list(enumerate(cosine_similarity[id]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    similarity_scores = similarity_scores[1:6]
    
    #Ottiene l'indice dei giochi
    games_index = [i[0] for i in similarity_scores]
    
    #Restituisce i primi 5 giochi più simili utilizzando l'indicizzazione basata sulla posizione intera (iloc)
    result = data[['name','genres','developer','price']].iloc[games_index]

    end = time.time()
    print("Tempo di esecuzione con similarità del coseno: ", end - start)

#Funzione che esegue una raccomandazione di giochi, utilizzando come metrica per il calcolo di similarità la distanza Euclidea e si ricava la quantità di tempo utilizzata
#per l'elaborazione
def recommend_euclidean(data):

    nome = "Team Fortress Classic"
    index = data.index[data['name'] == nome].values[0]
    
    #Definisce le categorie che vuol usare e le unisce in una, per poter applicare il tf-idf
    data['all_content'] = data['name'] + ';' + data['developer'] + ';' + data['publisher'] + ';' + data['platforms'] + ';' + data['genres'] 
    
    start = time.time()

    tfidf_matrix = vectorize_data(data)
    #Costruzione della similarità del coseno da applicare poi alla matrice creata
    euclidean = euclidean_distances(tfidf_matrix) 

    indices = pd.Series(data['name'].index)

    id = indices[index]

    #Ottiene i punteggi di similarità tra tutti i giochi rispetto a quello selezionato, li ordina e ne ottiene i primi 5
    similarity_scores = list(enumerate(euclidean[id]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    similarity_scores = similarity_scores[1:6]
    
    #Ottiene l'indice dei giochi
    games_index = [i[0] for i in similarity_scores]
    
    #Restituisce i primi 5 giochi più simili utilizzando l'indicizzazione basata sulla posizione intera (iloc)
    result = data[['name','genres','developer','price']].iloc[games_index]

    end = time.time()
    print("\nTempo di esecuzione con distanza euclidea: ", end - start)

#Funzione che esegue una raccomandazione di giochi, utilizzando come metrica per il calcolo di similarità Pearson e si ricava la quantità di tempo utilizzata
#per l'elaborazione
def recommend_pearson(data):

    index = 0
    
    #Definisce le categorie che vuol usare e le unisce in una, per poter applicare il tf-idf
    data['all_content'] = data['name'] + ';' + data['developer'] + ';' + data['publisher'] + ';' + data['platforms'] + ';' + data['genres'] 
    
    start = time.time()

    tfidf_matrix = vectorize_data(data)
    tfidf_matrix_array = tfidf_matrix.toarray()

    indices = pd.Series(data['name'].index)

    id = indices[index]
    correlation = []
    for i in range(len(tfidf_matrix_array)):
        correlation.append(pearsonr(tfidf_matrix_array[id], tfidf_matrix_array[i])[0])
    correlation = list(enumerate(correlation))
    sorted_corr = sorted(correlation, reverse=True, key=lambda x: x[1])[1:6]
    games_index = [i[0] for i in sorted_corr]

    result = data[['name','genres','developer','price']].iloc[games_index]

    end = time.time()
    print("\nTempo di esecuzione con correlazione di Pearson: ", end - start)

#Funzione che calcola la percentuale di spasità che un dataset possa avere
def calculating_sparsity(data):
    
    data = data.to_numpy()

    sparsity = 1.0 - (np.count_nonzero(data) / float(data.size))

    print('\nSparsità del dataset:', sparsity*100, "%\n")


steam_data = pd.read_csv('dataset/steam.csv')
steam_data['positivity_quote'] = steam_data['positive_ratings'] // steam_data['negative_ratings']
steam_data['genres'] = steam_data['steamspy_tags']
steam_data = steam_data[['name','release_date','developer','publisher','platforms','genres','positivity_quote', 'average_playtime','owners','price']].copy()

recommend_cosine(steam_data)
recommend_euclidean(steam_data)
recommend_pearson(steam_data)
calculating_sparsity(steam_data)
