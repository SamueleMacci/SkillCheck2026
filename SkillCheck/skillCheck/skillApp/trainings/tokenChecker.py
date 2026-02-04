import spacy

TRAIN_DATA = [

    (
        "Descrizione completa della posizione",
        {"entities": []}
    ),
    (
        "Vuoi lavorare con l'azienda leader dei ponteggi in Italia?",
        {"entities": []}
    ),
    (
        "Ponteggi Euroedile ricerca proprio te!",
        {"entities": []}
    ),
    (
        "Ricerchiamo Ingegnere strutturale da inserire nel nostro organico.",
        {"entities": [(12, 33, "esperienze")]}
    ),
    (
        "La risorsa farà parte di un team altamente qualificato ed in fase di potenziamento: si occuperà del calcolo strutturale di ponteggi di notevoli dimensioni e della redazione delle relazioni di calcolo tenendo conto anche dell'entrata in vigore delle nuove normative tecniche.",
        {"entities": [(100, 154, "competenze"), (163, 199, "competenze")]}
    ),
    (
        "Requisiti",
        {"entities": []}
    ),
    (
        "Laurea magistrale in Ingegneria meccanica, civile o edile;",
        {"entities": [(0, 57, "titoli_di_studio")]}
    ),
    (
        "Neolaureato;",
        {"entities": [(0, 11, "titoli_di_studio")]}
    ),
    (
        "Residenza non superiore a 20 km dalla ns. sede;",
        {"entities": []}
    ),
    (
        "Buone capacità di lavoro in team e problem-solving;",
        {"entities": [(35, 50, "competenze")]}
    ),
    (
        "Buona conoscenza di Autocad 3D e del programma ad elementi finiti Straus 7",
        {"entities": [(20, 30, "competenze"), (66, 74, "competenze")]}
    ),
    (
        "Sede di lavoro: Paese (TV).",
        {"entities": []}
    ),
    (
        "Inserimento immediato",
        {"entities": []}
    ),
    (
        "Inquadramento: a seconda della seniority del candidato, a partire da 1.600,00€",
        {"entities": []}
    ),
    (
        "Sviluppa interesse e passione, unisciti alla squadra di Ponteggi Euroedile!",
        {"entities": []}
    ),
    (
        "Contratto di lavoro: Tempo indeterminato, Tempo pieno, Tempo determinato",
        {"entities": []}
    ),
    (
        "Retribuzione: a partire da €1.600,00 al mese",
        {"entities": []}
    ),
    (
        "Orario: Dal lunedì al venerdì",
        {"entities": []}
    ),
    (
        "Benefit Estratto dalla descrizione completa della posizione Computer aziendale Convenzioni aziendali Lavoro da casa Orario flessibile Orario flessibile",
        {"entities": []}
    ),
    (
        "Descrizione completa della posizione",
        {"entities": []}
    ),
    (
        "La selezione è rivolta sia a candidati con profilo junior, neo laureati alla prima esperienza che candidati con media Seniority.",
        {"entities": []}
    ),
    (
        "La risorsa sarà inserita nel team di sviluppo di soluzioni software ERP, MES, WMS e BI;",
        {"entities": [(68, 71, "competenze"), (73, 76, "competenze"), (78, 81, "competenze"), (84, 86, "competenze")]}
    ),
    (
        "si occuperà di analizzare e realizzare strutture dati, procedure ETL finalizzate all'esposizione ed all'analisi dei dati.",
        {"entities": [(15, 53, "competenze"), (55, 68, "competenze"), (104, 120, "competenze")]}
    ),
    (
        "Le attività previste:",
        {"entities": []}
    ),
    (
        "Analisi tecnico/funzionale dei requisiti",
        {"entities": [(0, 40, "competenze")]}
    ),
    (
        "Sviluppo funzionalità di importazione, trasformazione ed esportazione dati",
        {"entities": [(0, 74, "competenze")]}
    ),
    (
        "Sviluppo di reportistica, cruscotti e widget con strumenti di BI",
        {"entities": [(0, 64, "competenze")]}
    ),
    (
        "Sviluppo di applicativi Web e Desktop con tecnologie .Net e/o Js",
        {"entities": [(0, 37, "competenze"), (53, 57, "competenze"), (62, 64, "competenze")]}
    ),
    (
        "I requisiti richiesti sono:",
        {"entities": []}
    ),
    (
        "Laurea in discipline informatiche e/o diploma in materie affini",
        {"entities": [(0, 63, "titoli_di_studio")]}
    ),
    (
        "Esperienza minima di un anno maturata nell’ambito del trattamento dati",
        {"entities": [(54, 70, "competenze")]}
    ),
    (
        "Buona conoscenza di SQL",
        {"entities": [(20, 23, "competenze")]}
    ),
    (
        "Preferibile conoscenza di PowerBI",
        {"entities": [(26, 33, "competenze")]}
    ),
    (
        "Oltre a precisione e proattività sono richieste buone capacità relazionali e predisposizione al lavoro in team.",
        {"entities": []}
    ),
    (
        "Offriamo:",
        {"entities": []}
    ),
    (
        "Contratto a tempo indeterminato",
        {"entities": []}
    ),
    (
        "Corsi di formazione con piattaforme e-learning e training on the job",
        {"entities": []}
    ),
    (
        "Flessibilità oraria e possibilità di smart working",
        {"entities": []}
    ),
    (
        "Convenzioni aziendali",
        {"entities": []}
    ),
    (
        "Il presente annuncio è rivolto a candidati di ambi i sessi.",
        {"entities": []}
    ),
    (
        "Contratto di lavoro: Tempo pieno, Tempo indeterminato",
        {"entities": []}
    ),
    (
        "Retribuzione: €1.700,00 - €2.300,00 al mese",
        {"entities": []}
    ),
    (
        "Benefit: Computer aziendale Lavoro da casa",
        {"entities": []}
    ),
    (
        "Orario: Orario flessibile",
        {"entities": []}
    ),
    (
        "Tipi di retribuzione supplementare:",
        {"entities": []}
    ),
    (
        "Bonus Premio di produzione Tredicesima",
        {"entities": []}
    ),
    (
        "Scuola Secondaria di II livello (Superiori) (Preferenziale)",
        {"entities": [(0, 43, "titoli_di_studio")]}
    ),
    (
        "Database: 1 anno (Preferenziale)",
        {"entities": [(0, 8, "competenze")]}
    ),
    (
        "Sviluppo software: 1 anno (Preferenziale)",
        {"entities": [(0, 17, "competenze")]}
    ),

]

# Tokenizza il testo parola per parola
nlp = spacy.blank("it")

for text, data in TRAIN_DATA:
    doc = nlp(text)
    tokens = [(token.text, token.idx, token.idx + len(token)) for token in doc]
    print("Token e relativi indici:")
    for token, start, end in tokens:
        print(f"Token: '{token}', Inizio: {start}, Fine: {end}")
    print()
