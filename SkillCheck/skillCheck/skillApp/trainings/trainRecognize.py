import spacy
import random
from spacy.training import Example

# Definizione del dataset
TRAIN_DATA = [
    (
        "Ho lavorato come sviluppatore software presso ABC Company, dove mi sono occupato dello sviluppo di "
        "applicazioni web e gestionali utilizzando tecnologie come Python, Django e PostgreSQL.",
        {"entities": [(17, 38, "esperienze"), (87, 128, "competenze"), (157, 163, "competenze"),
                      (165, 171, "competenze"), (174, 184, "competenze")]}
    ),
    (
        "Laurea in Informatica conseguita presso l'Università di Roma.",
        {"entities": [(0, 21, "titoli_di_studio")]}
    ),
    (
        "Esperienza pluriennale nell'analisi dei dati utilizzando Python, Pandas e scikit-learn.",
        {"entities": [(28, 44, "competenze"), (57, 63, "competenze"), (65, 71, "competenze"), (74, 86, "competenze")]}
    ),
]


def train_spacy(data, iterations):
    nlp = spacy.blank("it")
    ner = nlp.add_pipe('ner')

    # Togli il commento e aggiungilo sopra per partire dal modello addestrato
    #nlp = spacy.load("C:/Users/termi/PycharmProjects/skillCheck/modelli/recognizer")
    #ner = nlp.get_pipe("ner")

    # commenta questa parte per partire dal modello addestrato, in caso di addestramento dal modello base lascialo
    for _, annotations in data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    optimizer = nlp.begin_training()
    for itn in range(iterations):
        random.shuffle(data)
        losses = {}
        for text, annotations in data:
            entities = [(start, end, label) for start, end, label in annotations["entities"]]
            example = Example.from_dict(nlp.make_doc(text), {"entities": entities})
            try:
                nlp.update([example], losses=losses, drop=0.5)
            except Exception as e:
                print("Errore durante l'aggiornamento del modello:", e)
        print("Iterazione", itn + 1, "Losses:", losses)

    return nlp


# Esegui il training
nlp = train_spacy(TRAIN_DATA, 250)

# Salva il modello addestrato
output_dir = "C:/Users/termi/PycharmProjects/skillCheck/modelli/recognizer"
nlp.to_disk(output_dir)
print("Modello salvato in:", output_dir)
