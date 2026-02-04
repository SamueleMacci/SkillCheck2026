import spacy

# Carica il modello addestrato dalla directory specificata
model_dir = "C:/Users/termi/PycharmProjects/skillCheck/modelli/recognizer"
nlp = spacy.load(model_dir)

# Frasi di test
test_sentences = [
    "Ho lavorato come sviluppatore software presso ABC Company, dove mi sono occupato dello sviluppo di applicazioni web e gestionali utilizzando tecnologie come Python, Django e PostgreSQL.",
    "Laurea in Informatica conseguita presso l'Università di Roma.",
    "Esperienza pluriennale nell'analisi dei dati utilizzando Python, Pandas e scikit-learn.",
    "Corso di formazione in Data Science frequentato presso Big Data Academy.",
    "Ho lavorato come sviluppatore full-stack utilizzando tecnologie come React, Node.js e MongoDB.",
    "Master in Ingegneria del Software conseguito all'Università di Bologna.",
    "Sviluppatore mobile presso Mobile Solutions Ltd., specializzato in Android e Kotlin.",
    "Diploma di Perito Informatico conseguito presso l'Istituto Tecnico Industriale.",
    "Esperienza in progetti di machine learning con Python, TensorFlow e Keras.",
    "Analista di sistema presso DEF Corporation, con competenze in Java, Spring Boot e Hibernate.",
    "Esperienza pluriennale nella progettazione e sviluppo di sistemi embedded utilizzando C e C++.",
    "Project manager presso XYZ Technologies, con esperienza nella gestione di progetti Agile e Scrum.",
    "Esperienza di lavoro con reti neurali artificiali utilizzando TensorFlow e Keras.",
    "Sviluppatore web presso ABC Web Agency, specializzato in PHP, Laravel e MySQL.",
    "Ho lavorato come cuoco nel ristorante ABC",
    "Laurea in psicologia, ho esperienza nell'accudire bambini"
]

# Analizza le frasi di test
for sentence in test_sentences:
    doc = nlp(sentence)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    print("Frase:", sentence)
    print("Entità rilevate:", entities)

# Inizializzazione delle liste per le entità
esperienze_list = []
competenze_list = []
titoli_di_studio_list = []

# Loop attraverso le frasi di test
for sentence in test_sentences:
    doc = nlp(sentence)
    # Estrazione delle entità per ogni frase
    for ent in doc.ents:
        if ent.label_ == "esperienze":
            esperienze_list.append(ent.text)
        elif ent.label_ == "competenze":
            competenze_list.append(ent.text)
        elif ent.label_ == "titoli_di_studio":
            titoli_di_studio_list.append(ent.text)

# Stampa delle liste di entità
print("Lista delle esperienze:", esperienze_list)
print("Lista delle competenze:", competenze_list)
print("Lista dei titoli di studio:", titoli_di_studio_list)
