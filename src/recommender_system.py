import numpy as np
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.stats import pearsonr

#Funzione che gestisce la comunicazione con l'utente, chiedendo di inserire le caratteristiche del gioco su cui vuole che venga fatta la recomendation
def get_info():

    #Prendo gli input dall'utente
    print("\n(Ricorda di inserire i dati con la lettera maiuscola iniziale)\n")
    nome = input("Inserisci il nome:\n")
    developer = input("\nInserisci lo sviluppatore:\n")
    publisher = input("\nInserisci la casa pubblicatrice:\n")
    platforms = input("\nInserisci le piattaforme:\t (ricorda tra una parola e l'altra di mettere il simbolo ';' )\n")
    genres = input("\nInserisci il genere:\t (ricorda tra una parola e l'altra di mettere il simbolo ';' )\n")

    #Creo un dataframe temporaneo contenente i dati messi dall'utente
    users_data = pd.DataFrame({'name': nome, 'developer': developer,'publisher': publisher,'platforms': platforms,'genres': genres}, index=[0])

    return users_data

#Funzione che legge il dataset iniziale, lo riduce, controlla se il gioco inserito dall'utente sia già presente o meno, se non lo è lo aggiunge,
#vettorizza il dataset aggiornato, calcola la similarità del coseno, trova i 5 giochi più simili a quello indicato dall'utente, basandosi sulla sua posizione
#nel dataframe utilizzando l'indice ottenuto e si salva gli indici
def construct_recommendation(filename, users_data):

    steam_data = pd.read_csv(filename)
    steam_data['positivity_quote'] = steam_data['positive_ratings'] // steam_data['negative_ratings']
    steam_data['genres'] = steam_data['steamspy_tags']
    steam_data = steam_data[['name','release_date','developer','publisher','platforms','genres','positivity_quote', 'average_playtime','owners','price']].copy()

    #Controllo se l'elemento dato dall'utente si trova già nel dataset o meno, se non si trova, lo aggiungo all'inizio/fine. Mi salvo l'indice di cosa ha chiesto l'utente in ogni caso
    control = 0

    for name in steam_data['name']:
        if users_data['name'][0] != name:
            index = 0
            control = 1
        else:
            #Invece di Zelda metterai il gioco dato da input che si trova nel dataset
            index = steam_data.index[steam_data['name'] == name].values[0] 
            control = 0
            break

    if control == 1:
        steam_data = pd.concat([users_data,steam_data], ignore_index=True)

    #Creazione della categoria che conterrà le altre categorie per procedere alla vettorizzazione dei dati
    steam_data['all_content'] = steam_data['name'] + ';' + steam_data['developer'] + ';' + steam_data['publisher'] + ';' + steam_data['platforms'] + ';' + steam_data['genres'] #definisci le categorie che vuoi usare e uniscile in una, per poter applicare il tf-idf
    
    #Vettorizzazione
    tfidf_matrix = vectorize_data(steam_data)
    tfidf_matrix_array = tfidf_matrix.toarray()

    print('\nInizio ricerca di giochi...')

    indices = pd.Series(steam_data['name'].index)

    id = indices[index]
    correlation = []
    for i in range(len(tfidf_matrix_array)):
        correlation.append(pearsonr(tfidf_matrix_array[id], tfidf_matrix_array[i])[0])
    correlation = list(enumerate(correlation))
    sorted_corr = sorted(correlation, reverse=True, key=lambda x: x[1])[1:6]
    #Indici dei 5 giochi più simili a quello passato dall'utente
    games_index = [i[0] for i in sorted_corr] 

    print('\n[5 giochi più simili a quello inserito trovati]')
    print('\nPassaggio alla analisi del modello...')

    return games_index

#Funzione che prende il dataframe ridotto e aggiornato e lo vettorizza per crearsi una matrice tfidf
def vectorize_data(steam_data):
    #Riempie i NaN con stringhe vuote
    steam_data['all_content'] = steam_data['all_content'].fillna("").astype(str)

    vectorizer = TfidfVectorizer(analyzer='word')
    tfidf_matrix = vectorizer.fit_transform(steam_data['all_content'])
    return tfidf_matrix

#Funzione che gestisce l'ottenimento di informazioni dall'utente per la recommendation
def get_recommendation():
    print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
    print("GET RECOMMENDED\n\nBenvenuto, digita le caratteristiche del gioco su cui vuoi che si avvii la raccomandazione\n")
    users_data = get_info()

    while(True):
        print("\nQuesto è il videogioco che hai inserito:\n")
        print(users_data.head())
        risposta = input("\nE' corretto?:\t")

        if risposta == 'no':
            users_data = get_info()
        if risposta == 'NO':
            users_data = get_info()
        elif risposta == 'n':
            users_data = get_info()
        else:
            break

    games_index = construct_recommendation('dataset/steam.csv', users_data)

    return games_index
