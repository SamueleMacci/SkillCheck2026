import spacy

def divide_in_frasi(testo):
    # Carica il modello di lingua italiana di SpaCy
    nlp = spacy.load("it_core_news_sm")

    # Analizza il testo per estrarre le frasi
    doc = nlp(testo)

    # Estrai le frasi dal documento considerando gli accapo, i punti e i doppi accapo come separatori di frasi
    frasi = []
    frase_corrente = ''
    for token in doc:
        # Verifica se il token corrente è un accapo, un punto o un doppio accapo
        if token.text in ['\n', '.', '\n\n']:
            # Se la frase corrente non è vuota, la aggiungiamo alla lista delle frasi
            if frase_corrente:
                frasi.append(frase_corrente.strip())
                frase_corrente = ''
        else:
            frase_corrente += token.text_with_ws

    # Aggiungiamo l'ultima frase corrente alla lista delle frasi se non è vuota
    if frase_corrente.strip():
        frasi.append(frase_corrente.strip())

    return frasi

# Testiamo la funzione con un esempio di testo
testo = """Per azienda cliente operante nel settore dell'arredamento indoor/outdoor siamo alla ricerca di una cucitrice da inserire in organico. E' richiesta esperienza pluriennale nella mansione, capacità di utilizzo delle principali macchine da cucire quali rettilinea, taglia e cuci, zigzag, ecc. Completano il profilo una buona manualità e precisione. Si offre un contratto iniziale a termine con buone prospettive di assunzione.

Responsabilità:

La risorsa utilizzerà le principali macchine da cucire ed effettuerà il controllo qualità dei prodotti.



Esperienze lavorative:
Cucitore/Cucitrice - 12 mesi

Titolo di studio:
Licenza Media

Competenze:
Tessile - Utilizzo taglia-cuci

Disponibilità oraria: Full Time

CCNL: CCNL Commercio Confcommercio 01/03/2011

Livello contratto: 06 LIVELLO 6

Benefits: Nessuno

Patente: B

Mezzo di trasporto: Auto,

Osservazioni: Contratto iniziale a termine, buone prospettive di assunzione"""

# Chiama la funzione divide_in_frasi per dividere il testo in frasi
frasi_divise = divide_in_frasi(testo)

# Stampa le frasi divise
for i, frase in enumerate(frasi_divise, start=1):
    print(f"Frase {i}: {frase}")
