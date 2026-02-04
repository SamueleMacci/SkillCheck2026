from transformers import BertForSequenceClassification, BertTokenizer
import torch

# Directory in cui hai salvato il modello addestrato
saved_model_dir = "C:/Users/termi/PycharmProjects/skillCheck/modelli/comparer"

# Carica il modello salvato
model = BertForSequenceClassification.from_pretrained(saved_model_dir)
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Definisci le liste di titoli di studio, competenze ed esperienze da confrontare
titoli_studio_1 = ["Laurea in informatica", "Master in data science", "Dottorato in intelligenza artificiale"]
titoli_studio_2 = ["Laurea in ingegneria informatica", "Diploma in programmazione", "Certificato in machine learning"]

competenze_1 = ["Python", "Machine learning", "Analisi dei dati"]
competenze_2 = ["Java", "C++", "Database management"]

esperienze_1 = ["Stage come sviluppatore software", "Lavoro come data scientist", "Progetti di analisi dati"]
esperienze_2 = ["Tirocinio in azienda informatica", "Corso di formazione in programmazione", "Progetto di database"]

# Muovi il modello su GPU se disponibile
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# Definisci le liste da confrontare
categorie = [titoli_studio_1, competenze_1, esperienze_1]
categorie2 = [titoli_studio_2, competenze_2, esperienze_2]

# Itera attraverso le categorie
for cat, cat2 in zip(categorie, categorie2):
    # Itera attraverso gli elementi della prima categoria
    for elem in cat:
        # Itera attraverso gli elementi della seconda categoria
        for elem2 in cat2:
            # Tokenizzazione delle coppie di elementi
            encoded_inputs = tokenizer(
                [elem],
                [elem2],
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=64
            )

            # Muovi i dati su GPU se disponibile
            encoded_inputs = {key: tensor.to(device) for key, tensor in encoded_inputs.items()}

            # Ottieni le previsioni del modello per i dati
            model.eval()
            with torch.no_grad():
                outputs = model(**encoded_inputs)
                predictions = outputs.logits.squeeze().tolist()

            # Stampa le previsioni del modello per la coppia di elementi
            print(f"\nCoppia:")
            print(f"Elemento 1: {elem}")
            print(f"Elemento 2: {elem2}")
            print(f"Previsione del modello: {predictions}")

# Inizializza un dizionario per memorizzare il valore più alto associato a ciascun elemento delle prime liste
max_predictions = {}

# Itera attraverso le categorie
for cat, cat2 in zip(categorie, categorie2):
    # Itera attraverso gli elementi della prima categoria
    for elem in cat:
        # Inizializza il massimo valore per questo elemento
        max_value = float('-inf')

        # Itera attraverso gli elementi della seconda categoria
        for elem2 in cat2:
            # Tokenizzazione delle coppie di elementi
            encoded_inputs = tokenizer(
                [elem],
                [elem2],
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=64
            )

            # Muovi i dati su GPU se disponibile
            encoded_inputs = {key: tensor.to(device) for key, tensor in encoded_inputs.items()}

            # Ottieni le previsioni del modello per i dati
            model.eval()
            with torch.no_grad():
                outputs = model(**encoded_inputs)
                prediction = outputs.logits.item()  # Ottieni un singolo valore float

            # Controlla se la previsione corrente è maggiore del massimo valore per questo elemento
            if prediction > max_value:
                max_value = prediction

        # Salva il massimo valore per questo elemento
        max_predictions[elem] = max_value

# Stampa il valore più alto associato a ciascun elemento delle prime liste
print("\nValori più alti associati agli elementi delle prime liste:")
for elem, max_pred in max_predictions.items():
    print(f"{elem}: {max_pred}")




# Calcola la somma dei valori massimi per ogni categoria
sum_of_max_values_by_category = {category: 0 for category in ["Titoli di studio", "Competenze", "Esperienze"]}

# Calcola la somma dei valori massimi per ogni categoria
sum_of_max_values_by_category = {category: 0 for category in ["Titoli di studio", "Competenze", "Esperienze"]}

# Calcola la somma dei valori massimi per ogni categoria
for cat, cat2, category in zip(categorie, categorie2, ["Titoli di studio", "Competenze", "Esperienze"]):
    # Inizializza una lista per memorizzare i valori massimi per questa categoria
    max_values = []

    # Itera attraverso gli elementi della prima categoria
    for elem in cat:
        # Inizializza il massimo valore per questo elemento
        max_value = float('-inf')

        # Itera attraverso gli elementi della seconda categoria
        for elem2 in cat2:
            # Tokenizzazione delle coppie di elementi
            encoded_inputs = tokenizer(
                [elem],
                [elem2],
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=64
            )

            # Muovi i dati su GPU se disponibile
            encoded_inputs = {key: tensor.to(device) for key, tensor in encoded_inputs.items()}

            # Ottieni le previsioni del modello per i dati
            model.eval()
            with torch.no_grad():
                outputs = model(**encoded_inputs)
                prediction = outputs.logits.item()  # Ottieni un singolo valore float

            # Controlla se la previsione corrente è maggiore del massimo valore per questo elemento
            if prediction > max_value:
                max_value = prediction

        # Aggiungi il massimo valore per questo elemento alla lista
        max_values.append(max_value)

    # Calcola la somma dei valori massimi per questa categoria
    sum_of_max_values_by_category[category] = sum(max_values)

# Calcola la percentuale di soddisfazione per ogni categoria rispetto al massimo possibile per quella categoria
max_possible_values = {
    "Titoli di studio": len(titoli_studio_1),
    "Competenze": len(competenze_1),
    "Esperienze": len(esperienze_1)
}

print("\nPercentuale di soddisfazione per ogni categoria:")
for category, sum_of_max_values in sum_of_max_values_by_category.items():
    satisfaction_percentage = (sum_of_max_values / max_possible_values[category]) * 100
    print(f"{category}: {satisfaction_percentage:.2f}%")
