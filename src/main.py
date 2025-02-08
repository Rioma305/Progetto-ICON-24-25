from ontology import main_ontology
from classification_validation import main_recommender
from knowledge_base import main_kb

def avvio():
    print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
    print("BENVENUTO\n")

    while(True):
        print("\nScegli una tra le seguenti opzioni (numero corrispondente):\n\n1) Recommender System\n2) Knowledge Base\n3) Ontologia\n4) Exit\n\nInserisci qui:\t")
        risposta = input()
        if risposta == '1':
            main_recommender()
        elif risposta == '2':
            main_kb()
        elif risposta == '3':
            main_ontology()
        elif risposta == '4':
            print("\nArrivederci!")
            break
        else:
            print("\n-!-Inserisci correttamente il numero-!-")
        
        print("\nVuoi terminare l'esecuzione? (si-no)\n")
        risposta2 = input()
        if(risposta2 == 'SI'):
            print("\nArrivederci!")
            print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
            break
        elif(risposta2 == 'si'):
            print("\nArrivederci!")
            print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
            break
        elif(risposta2 == 's'):
            print("\nArrivederci!")
            print('\n----------------------------------------------------------------------------------------------------------------------------------------------------')
            break

if __name__ == '__main__':
    avvio()
