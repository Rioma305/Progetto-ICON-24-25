# Progetto-ICON-24-25
Progetto Icon dell'anno 2024-2025.

## Presentazione
Repository per l'esame di Ingegneria della Conoscenza, a.a. 24/25 - Università di Bari.

La documentazione risiede nel file: ```doc/Documentazione finale.pdf```

Studente, Nacci Mario, 760455 - mail: m.nacci22@studenti.uniba.it

## Root
- **dataset/** contiene il dataset in formato .csv e l'Ontologia in formato .owl
- **src/** contiene il codice sorgente in python
- **images/** contiene l'mmagine della struttura dell'ontologia
- **doc/** contiene la relazione completa del progetto

## Installazione dei requisiti
Installare tutte le librerie necessarie dal file requirements.txt con il comando da console nella directory del file ```requirements.txt```:

```pip install -r requirements.txt```

In caso di errori con alcune librerie usare il comando precedente ma con il file ```requirements2.txt```:

```pip install -r requirements2.txt```

Se python in windows restituisce un errore provare con:

```py -m pip install -r requirements.txt```

## Avvio del sistema
Per avviare il sistema utilizzare il comando:
  
  ```python main.py```
  
dalla directory del file ```main.py```

Analogalmente per vedere la regressione bisogna eseguire nella directory del file ```regression.py``` il comando:

  ```python regression.py```

separatamente ripesto al main per questioni di ottimizzazione delle tempistiche.
