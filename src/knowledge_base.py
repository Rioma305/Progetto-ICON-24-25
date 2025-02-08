import pytholog as pl
import pandas as pd

#Funzione che costruisce il dataframe basato sul dataset steam.csv.
#Aggiunge una nuova colonna 'star', in cui converte i valori del rapporto tra 'negative_ratings' e
#'positive_ratings' in delle stelle che rappresentanto il voto dato al gioco dagli utenti.
#Converte la colonna 'english' in stringhe.
def build_dataframe():

    #Creo il dataframe
    steam_data = pd.read_csv("dataset/steam.csv")

    #Creo una nuova colonna 'star', che avrà come valori la percentuale dei 'negative_ratings'
    #in rapporto ai 'positive_ratings'
    steam_data['star'] = (steam_data['negative_ratings'] / steam_data['positive_ratings']) * 100
    #Converto 'star' in dei range rappresentati dalle stelle
    #più basso è il valore della percentuale, più alta è la stella
    #[0, 12.5] = 5*;
    #[12.6, 25] = 4*;
    #[25.1, 37.5] = 3*;
    #[37.6, 50] = 2*;
    #[50, inf] = 1*
    steam_data.loc[(steam_data['star'] >= 0) & (steam_data['star'] <= 12.5), ['star']] = 5
    steam_data.loc[(steam_data['star'] > 12.5) & (steam_data['star'] <= 25), ['star']] = 4
    steam_data.loc[(steam_data['star'] > 25) & (steam_data['star'] <= 37.5), ['star']] = 3
    steam_data.loc[(steam_data['star'] > 37.5) & (steam_data['star'] <= 50), ['star']] = 2
    steam_data.loc[(steam_data['star'] > 50), ['star']] = 1
    #Converto i valori "0" e "1" di 'english' nelle string "no" e "yes"
    steam_data.loc[(steam_data['english'] == 0), ['english']] = 'no'
    steam_data.loc[(steam_data['english'] == 1), ['english']] = 'yes'

    #Creo una copia del dataframe con all'interno solo le colonne d'interesse
    steam_data = steam_data[['name','developer','publisher','english','star','steamspy_tags','price','average_playtime','genres']].copy()

    return steam_data

#Funzione che si occupa di popolare la knowledge base con i dati presi dal dataframe passato in input.
#Crea una lista in cui inizialmente inserisce i dati estratti dal dataframe sottoforma di 'fatti' e 'regole'.
#Questa lista viene poi inserita nella knowledge base creata con pytholog.
def populate_kb(dataframe):
    import pytholog as pl

    #Creo la knowledge base
    steam_kb = pl.KnowledgeBase('Steam Games')
    kb = []

    #Fatti riguardanti gli sviluppatori dei giochi
    #Trasformo in minuscolo le colonne 'name' e 'developer' e creo la lista di dizionari
    df_dev = dataframe[['name', 'developer']].drop_duplicates().copy()
    df_dev['name'] = df_dev['name'].str.lower()
    df_dev['developer'] = df_dev['developer'].str.lower()
    dev_records = df_dev.to_dict(orient="records")
    for d in dev_records:
        kb.append(f"developer({d['name']},{d['developer']})")

    #Fatti riguardanti chi ha pubblicato i giochi
    df_pub = dataframe[['name', 'publisher']].drop_duplicates().copy()
    df_pub['name'] = df_pub['name'].str.lower()
    df_pub['publisher'] = df_pub['publisher'].str.lower()
    pub_records = df_pub.to_dict(orient="records")
    for d in pub_records:
        kb.append(f"publisher({d['name']},{d['publisher']})")

    #Fatti riguardanti i prezzi dei giochi
    df_price = dataframe[['name', 'price']].drop_duplicates().copy()
    df_price['name'] = df_price['name'].str.lower()
    price_records = df_price.to_dict(orient="records")
    for d in price_records:
        kb.append(f"prices({d['name']},{d['price']})")

    #Fatti riguardanti i ratings in stelle dei giochi
    df_stars = dataframe[['name', 'star']].drop_duplicates().copy()
    df_stars['name'] = df_stars['name'].str.lower()
    stars_records = df_stars.to_dict(orient="records")
    for d in stars_records:
        kb.append(f"stars({d['name']},{d['star']})")

    #Fatti riguardanti i generi dei giochi
    df_genre = dataframe[['name', 'steamspy_tags']].drop_duplicates().copy()
    df_genre['name'] = df_genre['name'].str.lower()
    df_genre['steamspy_tags'] = df_genre['steamspy_tags'].str.lower()
    genre_records = df_genre.to_dict(orient="records")
    for d in genre_records:
        kb.append(f"genre({d['name']},{d['steamspy_tags']})")

    #Fatti che indicano se un gioco è in inglese
    df_eng = dataframe[['name', 'english']].drop_duplicates().copy()
    df_eng['name'] = df_eng['name'].str.lower()
    df_eng['english'] = df_eng['english'].astype(str).str.lower()
    eng_records = df_eng.to_dict(orient="records")
    for d in eng_records:
        kb.append(f"english({d['name']},{d['english']})")

    #L'utente può chiedere il costo di un gioco partendo dal nome
    kb.append("has_price(X, Y) :- prices(Y, X)")

    #L'utente può chiedere il rating di un gioco partendo dal nome
    kb.append("quality(X, Y) :- stars(Y, X)")

    #L'utente può chiedere qual è lo sviluppatore di un gioco
    kb.append("developed_by(X, Y) :- developer(Y, X)")

    #L'utente può chiedere chi ha rilasciato un gioco
    kb.append("released_by(X, Y) :- publisher(Y, X)")

    #L'utente può chiedere il genere di un gioco
    kb.append("is_genre(X, Y) :- genre(Y, X)")

    #L'utente può chiedere se un gioco è in lingua inglese
    kb.append("has_english(X, Y) :- english(Y, X)")

    #L'utente può confrontare la qualità di due giochi
    kb.append("quality_check(X, Y, T, Z) :- stars(X, T), stars(Y, Z)")

    #Popolo la knowledge base con i fatti e le regole accumulate
    steam_kb(kb)

    return steam_kb

def liking_prob(dataframe):

    liking_kb = pl.KnowledgeBase('Liking Probability')
    kb = []

    #Chiedo di darmi il nome di un gioco che è piaciuto all'utente e di un gioco di cui vuole sapere la liking probability
    Gioco_Piaciuto = input("Insrisci il nome del gioco che ti è piaciuto: ").lower()
    genere = input("Dimmi il genere del gioco: ").lower()
    tempo_gioco = input("e il tempo di gioco medio (in ore): ")
    tempo_gioco = int(tempo_gioco)

    #Aggiungo i fatti riguardanti questo gioco
    kb.append(f"is_genre({Gioco_Piaciuto}, {genere}")
    kb.append(f"avg_playtime({Gioco_Piaciuto}, %s" % tempo_gioco)
    kb.append(f"liked_game(utente, {Gioco_Piaciuto}")

    Gioco_Nuovo = input("\nInserisci il nome di un gioco di cui vuoi calcolare la probabilità che ti piaccia: ").lower()
    genere_n = input("Dimmi il genere del gioco: ").lower()
    tempo_gioco_n = input("e il tempo di gioco medio (in ore): ")
    tempo_gioco_n = int(tempo_gioco_n)
    #Aggiungo i fatti riguardanti questo gioco
    kb.append(f"is_genre({Gioco_Nuovo}, {genere_n}")
    kb.append(f"avg_playtime({Gioco_Nuovo}, %s" % tempo_gioco_n)

    #Chiedo di sapere quante ora l'utente lavora in un giorno
    Orario = input("\nQuante ore lavori/studi al giorno? ")
    Orario = int(Orario)

    #Fatto che associa l'utente e le sue ore di lavorio giornaliere
    kb.append(f"has_work(utente, %s)" % Orario)

    #Regola che calcola lo stress dell'utente
    kb.append(f"stress(utente, Prob) :- Prob is %s" % Orario)

    #Aggiungo i fatti che associano un genere al genere stesso, potendo dare la conferma che due generi siano uguali
    data = dataframe['genres']
    result = list(set(data))
    i = 0
    while(i < len(result)):
        kb.append(f"same_genre({result[i].lower()},{result[i].lower()}")
        i += 1

    #L'utente può chiedere l'avg_playtime di un gioco
    kb.append("has_avg_playtime(X, Y) :- avg_playtime(X, Y)")

    #Regola che fa la differenza tra l’avg_playtime del gioco che già piace all’utente e del gioco nuovo.
    #kb.append(f"avg_playtime_comp({Gioco_Piaciuto}, {Gioco_Nuovo}, Y) :- liked_game(utente, Gioco_Piaciuto), has_avg_playtime({Gioco_Piaciuto}, Avg1), has_avg_playtime({Gioco_Nuovo}, Avg2), Y is Avg1 - Avg2")
    kb.append(f"avg_playtime_comp(Gioco1, Gioco2, Y) :- liked_game(utente, Gioco1), has_avg_playtime(Gioco1, Avg1), has_avg_playtime(Gioco2, Avg2), Y is Avg1 - Avg2")

    #Regola che controlla se due giochi hanno lo stesso genere
    kb.append(f"has_same_genre(Gioco1, Gioco2) :- is_genre(Gioco1, X), is_genre(Gioco2, Y), same_genre(X, Y)")

    liking_kb(kb)

    #Faccio la query per potermi salvare il valore di Y
    result = liking_kb.query(pl.Expr(f"avg_playtime_comp({Gioco_Piaciuto}, {Gioco_Nuovo}, What)"))
    Playtime_Similarity = result[0]['What']

    Playtime_Similarity = assign_range(Playtime_Similarity)

    result = liking_kb.query(pl.Expr(f"has_same_genre({Gioco_Piaciuto}, {Gioco_Nuovo})"))
    bool = result[0]
    Genre_Similarity = 0
    if(bool == 'Yes'):
        Genre_Similarity = 2.5
    elif(bool == 'No'):
        Genre_Similarity = -2.5

    #Regola che calcola la compatibilità dei 2 giochi
    kb.append(f"compatibility(Num1, Num2, S1) :- S1 is Num1 + Num2")

    #Aggiungo la regola che calcola la probabilità che il gioco nuovo possa piacere all'utente
    #Regola che calcola la probabilità che il nuovo gioco possa piacere all'utente
    kb.append(f"to_like(utente, Num1, Num2, Prob) :- stress(utente, P1), compatibility(Num1, Num2, S1), Prob is P1 + S1")

    liking_kb(kb)

    result = liking_kb.query(pl.Expr(f"to_like(utente, {Playtime_Similarity}, {Genre_Similarity}, What)"))
    comp = list(result[0].keys())[0]
    p = result[0][f"{comp}"]

    if(p > 100):
        p = 100
    elif(p < 0):
        p = 0

    print("\nLa probabilità che", Gioco_Nuovo, "ti possa piacere è:", p, "%")

def assign_range(num):

    num = int(num)

    if((abs(num) >= 0) & (abs(num) <= 100)):
        i = 100
    elif((abs(num) > 100) & (abs(num) <= 250)):
        i = 90
    elif((abs(num) > 250) & (abs(num) <= 500)):
        i = 80
    elif((abs(num) > 500) & (abs(num) <= 750)):
        i = 70
    elif((abs(num) > 750) & (abs(num) <= 1000)):
        i = 60
    elif((abs(num) > 1000) & (abs(num) <= 1250)):
        i = 50
    elif((abs(num) > 1250) & (abs(num) <= 1500)):
        i = 40
    elif((abs(num) > 1500) & (abs(num) <= 1750)):
        i = 30
    elif((abs(num) > 1750) & (abs(num) <= 2000)):
        i = 20
    elif((abs(num) > 2000) & (abs(num) <= 2500)):
        i = 20
    elif((abs(num) > 2500) & (abs(num) <= 10000)):
        i = 10
    elif(abs(num) > 10000):
        i = 0

    return i

#Funzione che si occupa della interazione con l'utente, permettendogli di eseguire ricerche sui giochi e sulle loro caratteristiche.
def main_kb():

    dataframe = build_dataframe()
    kb = populate_kb(dataframe)

    print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
    print("\nKNOWLEDGE BASE\n")
    print("Benvenuto, qui puoi eseguire ricerche sui giochi e sulle loro caratteristiche\n\n")

    while(True):
        print("\nEcco le ricerche che puoi eseguire :")
        print("1) Ricerche sulle caratteristiche di un gioco")
        print("2) Confronti e ricerca di giochi in base ad una caratteristica")
        print("3) Verificare delle caratteristiche")
        print("4) Vedere con quale probabilità ti possa piacere un nuovo gioco")
        print("5) Exit Knowledge Base\n\n")
        choice1 = input("Inserisci qui (numero):\t")
        c1 = int(choice1)

        if(c1 == 1):
            while(True):
                game_name = input("\nDammi il nome di un gioco: ").lower()
                print("\nQueste sono le caratteristiche che puoi cercare:")
                print("1) Chi lo ha sviluppato")
                print("2) Chi lo ha distribuito")
                print("3) Quanto costa")
                print("4) Quante stelle ha (su una scala da 1 a 5)")
                print("5) Di che genere è")
                print("6) Se è disponibile in lingua inlgese")
                print("7) Indietro\n")
                choice2 = input("Selezionane una opzione (numero): ")
                c2 = int(choice2)

                if(c2 == 1):
                    result = kb.query(pl.Expr(f"developed_by(What,{game_name})"))
                    parola = result[0]['What']
                    print("\n", game_name, "è stato sviluppato da:", parola)

                elif(c2 == 2):
                    result = kb.query(pl.Expr(f"released_by(What,{game_name})"))
                    parola = result[0]['What']
                    print("\n", game_name, "è stato rilasciato da:", parola)

                elif(c2 == 3):
                    result = kb.query(pl.Expr(f"has_price(What,{game_name})"))
                    parola = result[0]['What']
                    print("\n", game_name, "costa:", parola)

                elif(c2 == 4):
                    result = kb.query(pl.Expr(f"quality(What,{game_name})"))
                    parola = result[0]['What']
                    print("\n", game_name, "ha:", parola, "stelle")

                elif(c2 == 5):
                    result = kb.query(pl.Expr(f"is_genre(What,{game_name})"))
                    parola = result[0]['What']
                    print("\nIl genere di", game_name, "è:", parola)

                elif(c2 == 6):
                    result = kb.query(pl.Expr(f"has_english(What,{game_name})"))
                    parola = result[0]['What']
                    if (parola == 'yes'):
                        print("\n", game_name, "è disponibile in lingua inglese")
                    elif (parola == 'no'):
                        print("\n", game_name, "non è disponibile in lingua inglese")

                elif(c2 == 7):
                    break

                else:
                    print("\n-!-Inserisci correttamente il numero-!-\n")
                
                risposta = input("\nVuoi tornare indietro?\t (sì-no)\n")
                if(risposta == 'SI'):
                    print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
                    break
                elif(risposta == 'si'):
                    print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
                    break
                elif(risposta == 's'):
                    print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
                    break

        elif(c1 == 2):
            print("\nQueste sono ricerche che puoi eseguire sulle caratteristiche:")
            while(True):
                print("1) Lista di giochi di un prezzo")
                print("2) Confronto di qualità tra 2 giochi")
                print("3) Indietro\n")
                choice3 = input("Selezionane una (inserisci il numero corrispondente alla tua scelta): ")
                c3 = int(choice3)

                if(c3 == 1):
                    prezzo = input("Inserisci un prezzo (es 3.99): ")
                    result = kb.query(pl.Expr(f"has_price({prezzo},What)"))
                    print("\nEcco la lista dei primi 100 giochi con prezzo ", prezzo, ":\n")
                    result = result[0:100]
                    i = 1
                    for r in result:
                        print(i, ")", r[f"{prezzo}"])
                        i += 1
                    print("\nPuoi selezionare una nuova ricerca:")

                #Confronto di qualità tra 2 giochi
                elif(c3 == 2):
                    game1 = input("Dimmi il nome del primo gioco: ").lower()
                    game2 = input("Dimmi il nome del secondo gioco: ").lower()
                    result = kb.query(pl.Expr(f"quality_check({game1}, {game2}, X, Y"))
                    star1 = result[0]['X']
                    star2 = result[0]['Y']
                    if(star1 > star2):
                        print("\nIl gioco migliore è: ", game1, ", perché la qualità di", game1, "è", star1, "è la qualità di", game2, "è", star2)
                    elif(star1 < star2):
                        print("\nIl gioco migliore è: ", game2, ", perché la qualità di", game2, "è", star2, "è la qualità di", game1, "è", star1)
                    elif(star1 == star2):
                        print("\nI due giochi hanno la stessa qualità, perché la qualità di", game1, "è", star1, ", e la qualità di", game2, "è", star2)
                    print("\nPuoi selezionare una nuova ricerca:")

                elif(c3 == 3):
                    break
                else:
                    print("\n-!-Inserisci correttamente il numero-!-\n")
                    
        elif(c1 == 3):
            while(True):
                print("\nQuesti sono le caratteristiche che puoi verificare:")
                print("1) developer\n2) publisher\n3) prices\n4) stars\n5) genre\n6) english\n")
                choice4 = input("Seleziona una caratteristica(inserisci il numero corrispondente alla tua scelta): ")
                c4 = int(choice4)
                if(c4 == 1):
                    fatto = "developer"
                    name = input("Quale gioco vuoi controllare? ").lower()
                    char = input("Inserisci un dato corrispondente alla caratteristica scelta: ").lower()
                    print(kb.query(pl.Expr(f"{fatto}({name},{char})")))
                elif(c4 == 2):
                    fatto = "publisher"
                    name = input("Quale gioco vuoi controllare? ").lower()
                    char = input("Inserisci un dato corrispondente alla caratteristica scelta: ").lower()
                    print(kb.query(pl.Expr(f"{fatto}({name},{char})")))
                elif(c4 == 3):
                    fatto = "prices"
                    name = input("Quale gioco vuoi controllare? ").lower()
                    char = input("Inserisci un dato corrispondente alla caratteristica scelta: ").lower()
                    print(kb.query(pl.Expr(f"{fatto}({name},{char})")))
                elif(c4 == 4):
                    fatto = "stars"
                    name = input("Quale gioco vuoi controllare? ").lower()
                    char = input("Inserisci un dato corrispondente alla caratteristica scelta: ").lower()
                    print(kb.query(pl.Expr(f"{fatto}({name},{char})")))
                elif(c4 == 5):
                    fatto = "genre"
                    name = input("Quale gioco vuoi controllare? ").lower()
                    char = input("Inserisci un dato corrispondente alla caratteristica scelta: ").lower()
                    print(kb.query(pl.Expr(f"{fatto}({name},{char})")))
                elif(c4 == 6):
                    fatto = "english"
                    name = input("Quale gioco vuoi controllare? ").lower()
                    char = input("Inserisci un dato corrispondente alla caratteristica scelta: ").lower()
                    print(kb.query(pl.Expr(f"{fatto}({name},{char})")))
                else:
                    print("\n-!-Inserisci correttamente il numero-!-\n")
                    
                risposta = input("Vuoi tornare indietro?\t(si-no)\n")
                if(risposta == 'SI'):
                    print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
                    break
                elif(risposta == 'si'):
                    print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
                    break
                elif(risposta == 's'):
                    print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
                    break

        elif(c1 == 4):
            while(True):
                liking_prob(dataframe)
                risposta = input("Vuoi tornare indietro?\t(si-no)\n")
                if(risposta == 'SI'):
                    print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
                    break
                elif(risposta == 'si'):
                    print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
                    break
                elif(risposta == 's'):
                    print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
                    break

        elif(c1 == 5):
            print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
            break
        else:
            print("\n-!-Inserisci correttamente il numero-!-\n")