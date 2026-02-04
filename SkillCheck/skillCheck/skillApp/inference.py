# inference.py
import torch
from transformers import BertTokenizer, BertForSequenceClassification

# Carica il modello salvato
model = BertForSequenceClassification.from_pretrained('path/to/save/model')

# Testa il modello su un nuovo testo
def infer(text):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    encoding = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        output = model(**encoding)
    label = torch.argmax(output.logits, dim=1).item()
    return label

# Esempio di utilizzo
new_text = "Esempio di curriculum con competenze e laurea."
result = infer(new_text)
print(f"Etichetta predetta: {result}")
