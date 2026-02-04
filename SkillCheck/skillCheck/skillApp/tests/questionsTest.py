import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Carica il modello addestrato
output_dir = "C:/Users/termi/PycharmProjects/skillCheck/modelli/questioner"
model = T5ForConditionalGeneration.from_pretrained(output_dir)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# Tokenizzatore
tokenizer = T5Tokenizer.from_pretrained('t5-small')

# Liste delle esperienze, competenze e titoli di studio
esperienze = ['analisi dei dati', 'Corso di formazione in Data Science', 'sviluppatore full-stack',
              'Sviluppatore mobile', 'Esperienza in progetti di machine learning', 'Analista di sistema',
              'Esperienza pluriennale nella progettazione e sviluppo di sistemi embedded', 'Project manager',
              'Esperienza di lavoro con reti neurali artificiali', 'Sviluppatore web', 'cuoco nel']

competenze = ['sviluppo di applicazioni web e gestionali', 'Python', 'Django', 'PostgreSQL', 'Python',
              'Pandas', 'scikit-learn', 'React', 'Node.js', 'MongoDB', 'Android', 'Kotlin', 'Python',
              'TensorFlow', 'Keras', 'Java', 'Spring Boot', 'Hibernate', 'C', 'C++',
              'esperienza nella gestione di progetti Agile e Scrum', 'TensorFlow', 'Keras', 'PHP',
              'Laravel', 'MySQL', "esperienza nell'accudire bambini"]

titoli_di_studio = ['Laurea in Informatica', 'Master in Ingegneria del Software', 'Diploma di Perito Informatico',
                    'Laurea in psicologia', 'certificati nello stesso ambito', 'laurea in ingegneria informatica']

# Funzione per generare domande
def generate_questions(texts, category=None):
    print(f"Domande{' per la categoria ' + category if category else ''}:")
    for text in texts:
        print(f"Testo: {text}")
        input_text = f"{text}"
        with torch.no_grad():
            inputs = tokenizer(input_text, return_tensors='pt', max_length=512, truncation=True)
            inputs = {k: v.to(device) for k, v in inputs.items()}
            if category:
                inputs['categories'] = category
            output_ids = model.generate(inputs['input_ids'], max_length=32, num_beams=4, early_stopping=True)
            generated_question = tokenizer.decode(output_ids[0], skip_special_tokens=True)
            print(f"Domanda: {generated_question}")
        print()


# Genera domande per le esperienze
generate_questions(esperienze, "esperienze")

# Genera domande per le competenze
generate_questions(competenze, "competenze")

# Genera domande per i titoli di studio
generate_questions(titoli_di_studio, "titoli_di_studio")
