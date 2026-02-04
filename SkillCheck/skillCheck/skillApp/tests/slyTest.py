import string


def divide_in_parole(testo):
    # Rimuovi la punteggiatura, converti tutto in minuscolo e dividilo in parole
    parole = []
    parola_corrente = ''

    for carattere in testo:
        if carattere.isalnum() or carattere == "'":  # considera anche l'apostrofo nelle parole
            parola_corrente += carattere.lower()
        elif parola_corrente:
            parole.append(parola_corrente)
            parola_corrente = ''

    if parola_corrente:
        parole.append(parola_corrente)

    return set(parole)


def testo_contenuto_percentuale(testo_principale, testo_da_cercare, soglia_percentuale=75):
    # Ottieni l'insieme di parole dal testo principale e dal testo da cercare
    parole_principale = divide_in_parole(testo_principale)
    parole_da_cercare = divide_in_parole(testo_da_cercare)

    # Calcola il numero di parole nel sottoinsieme presenti nel testo principale
    parole_presenti = sum(1 for parola in parole_da_cercare if parola in parole_principale)

    # Calcola la percentuale di corrispondenza considerando tutte le parole da cercare
    percentuale_corrispondenza = (parole_presenti / len(parole_da_cercare)) * 100

    # Verifica se la percentuale di corrispondenza supera la soglia specificata
    if percentuale_corrispondenza >= soglia_percentuale:
        return True
    else:
        return False


# Esempio di utilizzo:
testo1 = """La figura ricercata, a riporto del Direttore dei Sistemi Informativi, dovrà occuparsi della Progettazione, sviluppo e manutenzione di applicazioni software in linguaggio C su piattaforma Linux ed in particolare di:

· Collaborare con la squadra per comprendere i requisiti del progetto e tradurli in soluzioni software efficienti.

· Effettuare test, debug e ottimizzazione del codice per garantire prestazioni e stabilità ottimali.

· Creare documentazione tecnica dettagliata per il codice sviluppato e i processi implementati.

· Collaborare con altri membri della squadra per il completamento efficace dei progetti.

Requisiti:

· Esperienza consolidata nello sviluppo di applicazioni in linguaggio C su piattaforma Linux.

· Conoscenza approfondita delle librerie standard di C e delle best practice di programmazione.

· Familiarità con i sistemi operativi Linux e la loro struttura.

· Capacità di problem-solving e debugging efficace.

· Ottime capacità di comunicazione e lavoro di squadra.

Requisiti preferenziali:

· Conoscenza di altri linguaggi di programmazione (es. Python, Shell scripting, Java, etc.).

· Conoscenza delle base dati tipo Mysql, SqlServer.

· Esperienza con la gestione di progetti open-source.

· Familiarità con il versioning software (es. Git).

· Certificazioni rilevanti sono considerate un plus.

La presente ricerca è rivolta ad entrambi i sessi, ai sensi delle leggi 903/77 e 125/91, e a persone di tutte le età e tutte le nazionalità, ai sensi dei decreti legislativi 215/03 e 216/03.

Si prega, nel curriculum, di autorizzare il trattamento dei dati personali ai sensi del Regolamento UE 2016/679.

Contratto di lavoro: Tempo pieno, Tempo indeterminato

Orario:

Dal lunedì al venerdì
Esperienza:

Programmatore Software: 2 anni (Preferenziale)

Richiesta una laurea in ingegneria informatica"""
testo2 = """
ABOUT ME 

Sono una persona che si concentra 
sulla creazione di connessioni 
significative con gli altri, credo 
fermamente nell'importanza della 
comunicazione efficace e nella capacità 
di collaborare con gli altri per 
raggiungere obiettivi comuni.  
Sono guidato dall'obiettivo di 
raggiungere l'eccellenza, se ritengo ciò 
che faccio incompleto o imperfetto 
spesso mi è intollerabile.  
Sono per natura analitico e creativo, ciò 
mi ha aiutato sempre nel risolvere 
problemi in modo innovativo. 
"""

if testo_contenuto_percentuale(testo2, testo1, soglia_percentuale=50):
    print("Il testo 2 contiene almeno il 50% del testo 1.")
else:
    print("Il testo 2 non contiene almeno il 50% del testo 1.")
