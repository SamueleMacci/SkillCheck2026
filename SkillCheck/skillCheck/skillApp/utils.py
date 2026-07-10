import os
import hmac
import hashlib
from io import BytesIO
from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Any, Callable
from django.conf import settings
from pdfminer.high_level import extract_text
from transformers import pipeline

# -------------------------
# Helpers per i modelli NLP
# -------------------------


@lru_cache(maxsize=None)
def get_device():
    import torch

    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


# spaCy: modello NER "recognizer" addestrato nel repo
@lru_cache(maxsize=None)
def get_recognizer():
    import spacy

    model_path = Path(settings.MODELS_DIR) / "recognizer"
    return spacy.load(model_path.as_posix())


# spaCy: modello italiano base per la sola segmentazione in frasi
@lru_cache(maxsize=None)
def get_it_core():
    import spacy

    try:
        return spacy.load("it_core_news_sm")
    except OSError:
        # Se il modello non è installato, ripiega su un italiano "blank"
        # (segmentazione naive; per la demo va bene)
        return spacy.blank("it")


# BERT comparatore: modello + tokenizer
@lru_cache(maxsize=None)
def get_comparer():
    from transformers import BertForSequenceClassification, BertTokenizer

    model_dir = Path(settings.MODELS_DIR) / "comparer"
    model = BertForSequenceClassification.from_pretrained(model_dir.as_posix())
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model.to(get_device())
    model.eval()
    return model, tokenizer


# Question generator (T5 custom)
from transformers import T5ForConditionalGeneration


class T5WithCategories(T5ForConditionalGeneration):
    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        decoder_input_ids=None,
        decoder_attention_mask=None,
        head_mask=None,
        decoder_head_mask=None,
        encoder_outputs=None,
        past_key_values=None,
        inputs_embeds=None,
        decoder_inputs_embeds=None,
        labels=None,
        use_cache=None,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
        categories=None,
        cross_attn_head_mask=None,
    ):
        return super().forward(
            input_ids=input_ids,
            attention_mask=attention_mask,
            decoder_input_ids=decoder_input_ids,
            decoder_attention_mask=decoder_attention_mask,
            head_mask=head_mask,
            decoder_head_mask=decoder_head_mask,
            encoder_outputs=encoder_outputs,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            decoder_inputs_embeds=decoder_inputs_embeds,
            labels=labels,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            cross_attn_head_mask=cross_attn_head_mask,
        )


@lru_cache(maxsize=None)
def get_questioner():
    from transformers import T5Tokenizer

    model_dir = Path(settings.MODELS_DIR) / "questioner"
    model = T5WithCategories.from_pretrained(model_dir.as_posix())
    tokenizer = T5Tokenizer.from_pretrained("t5-small")
    model.to(get_device())
    model.eval()
    return model, tokenizer


# -------------------------
# Utility PDF
# -------------------------


def extract_text_from_pdf_content(pdf_content: bytes) -> str:
    return extract_text(BytesIO(pdf_content))


def extract_text_from_pdf(pdf_file) -> str:
    pdf_content = pdf_file.read()
    return extract_text(BytesIO(pdf_content))


# -------------------------
# NLP: frasi ed entità
# -------------------------


def divide_in_frasi(testo: str):
    nlp = get_it_core()
    doc = nlp(testo)

    frasi = []
    frase_corrente = ""
    for token in doc:
        if token.text in [
            "\n",
            ".",
            "\n\n",
            "\r",
            "\r\n",
            "\r\n\r\n",
            "\r\n \r",
            "\r\n\n",
            "!",
            "?",
            ";",
        ]:
            if frase_corrente:
                frasi.append(frase_corrente.strip())
                frase_corrente = ""
        else:
            # token.text_with_ws mantiene gli spazi originali
            frasi.append(token.text_with_ws) if False else None
            frase_corrente += token.text_with_ws

    if frase_corrente.strip():
        frasi.append(frase_corrente.strip())

    return frasi


def extract_entities_resume(text: str):
    # normalizzazione minima
    testo_pulito = " ".join(text.replace("\r", " ").replace("\n", " ").split())

    nlp = get_recognizer()
    doc = nlp(testo_pulito)

    esperienze, competenze, titoli_di_studio = [], [], []
    for ent in doc.ents:
        if ent.label_ == "esperienze":
            esperienze.append(ent.text)
        elif ent.label_ == "competenze":
            competenze.append(ent.text)
        elif ent.label_ == "titoli_di_studio":
            titoli_di_studio.append(ent.text)

    return list(set(esperienze)), list(set(competenze)), list(set(titoli_di_studio))


def extract_entities_from_text(text: str):
    nlp = get_recognizer()
    frasi = divide_in_frasi(text)

    entities = []
    for frase in frasi:
        doc = nlp(frase)
        for ent in doc.ents:
            entities.append((ent.text, ent.label_))

    esperienze = list(set([e for e, l in entities if l == "esperienze"]))
    competenze = list(set([e for e, l in entities if l == "competenze"]))
    titoli_di_studio = list(set([e for e, l in entities if l == "titoli_di_studio"]))

    return esperienze, competenze, titoli_di_studio


# -------------------------
# Comparator (BERT)
# -------------------------


def compute_satisfaction_percentage(job_desc_cat, curriculum_cat):
    import random
    import torch

    model, tokenizer = get_comparer()
    device = get_device()

    job_desc_cat1 = str(job_desc_cat).strip("[]").replace("'", "")
    lista_job = job_desc_cat1.split(", ")

    if len(lista_job) == 0 or lista_job[0] == "":
        return 10.0, []

    if len(curriculum_cat) == 0:
        random_indices = random.sample(range(len(lista_job)), min(3, len(lista_job)))
        random_elements = [lista_job[i] for i in random_indices]
        return 0.0, random_elements

    max_values = []
    max_elements = []

    for elem_job_desc in lista_job:
        max_value = float("-inf")
        for elem_curriculum in curriculum_cat:
            encoded_inputs = tokenizer(
                [elem_job_desc],
                [elem_curriculum],
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=64,
            )
            encoded_inputs = {k: v.to(device) for k, v in encoded_inputs.items()}

            with torch.no_grad():
                outputs = model(**encoded_inputs)
                prediction = round(outputs.logits.item() * 10)

            if prediction > max_value:
                max_value = prediction

        max_values.append(max_value)
        max_elements.append(elem_job_desc)

    if not max_values:
        return 10.0, []

    sorted_indices = sorted(range(len(max_values)), key=lambda k: max_values[k])
    lowest_three_indices = sorted_indices[: min(3, len(sorted_indices))]
    lowest_three_elements = [max_elements[i] for i in lowest_three_indices]

    sum_of_max_values = sum(max_values)
    max_possible_values = len(lista_job)
    satisfaction_percentage = sum_of_max_values / max_possible_values

    return satisfaction_percentage, lowest_three_elements


# -------------------------
# Questioner (T5)
# -------------------------


def generate_questions(esperienze, competenze, titoli_di_studio):
    import torch
    from transformers import T5Tokenizer  # type only (già usato sopra)

    model_q, tokenizer_q = get_questioner()
    device = get_device()

    generated_questions = {"esperienze": [], "competenze": [], "titoli_di_studio": []}

    categories_data = [
        ("esperienze", esperienze),
        ("competenze", competenze),
        ("titoli_di_studio", titoli_di_studio),
    ]

    questions_with_data = []

    for category, data_list in categories_data:
        if not data_list:
            continue
        for data in data_list:
            cleaned_data = data.strip("'")
            with torch.no_grad():
                inputs = tokenizer_q(
                    cleaned_data, return_tensors="pt", max_length=512, truncation=True
                )
                inputs = {k: v.to(device) for k, v in inputs.items()}
                inputs["categories"] = category
                output_ids = model_q.generate(
                    inputs["input_ids"], max_length=32, num_beams=4, early_stopping=True
                )
                generated_question = tokenizer_q.decode(
                    output_ids[0], skip_special_tokens=True
                )
                generated_questions[category].append(generated_question)
                questions_with_data.append((generated_question, data))

    return (
        generated_questions["esperienze"],
        generated_questions["competenze"],
        generated_questions["titoli_di_studio"],
        questions_with_data,
    )


# -------------------------
# Helpers varie su domande
# -------------------------


def parse_domande_con_data(stringa_domande_con_data):
    s = stringa_domande_con_data.strip("[]")
    tuples = s.split("), ")
    tuple_divise = [t.strip("()") for t in tuples]

    domande_con_data = []
    for t in tuple_divise:
        parts = [part.strip("'") for part in t.split("', ")]
        if len(parts) == 1:
            domande_con_data.append((parts[0], None))
        else:
            domande_con_data.append((parts[0], parts[1]))

    return domande_con_data


def filter_new_questions(job_description, lowest_elements):
    import random

    existing_questions = (
        set(job_description.domande_selezionate.split("\n"))
        if job_description.domande_selezionate
        else set()
    )
    new_questions = []

    domande_correct = parse_domande_con_data(job_description.domande_con_data)

    for question, data in domande_correct:
        full_question = question
        if full_question not in existing_questions and (
            data is None or data in lowest_elements
        ):
            new_questions.append(full_question)

    random.shuffle(new_questions)
    num_questions_to_select = min(3, len(new_questions))
    selected_questions = new_questions[:num_questions_to_select]

    return selected_questions


def _compare_pair_0_10(a: str, b: str) -> float:
    """
    Wrapper minimale che usa il comparer già caricato in get_comparer() per
    ottenere un punteggio 0..10 per la coppia (a,b), coerente con il resto del progetto.
    """
    import torch

    model, tokenizer = get_comparer()
    device = get_device()
    encoded = tokenizer(
        [a], [b], return_tensors="pt", padding=True, truncation=True, max_length=64
    )
    encoded = {k: v.to(device) for k, v in encoded.items()}
    with torch.no_grad():
        out = model(**encoded)
        score = round(
            out.logits.item() * 10
        )  # stesso scaling di compute_satisfaction_percentage
    return max(0.0, min(10.0, float(score)))


def build_jd_cv_matrix(
    jd_skills: List[str],
    cv_skills: List[str],
    score_fn: Callable[[str, str], float] | None = None,
) -> Dict[str, Any]:
    """
    Crea una matrice explainable: per ogni skill JD tutte le corrispondenze CV con punteggio 0..10.
    """
    if score_fn is None:
        score_fn = _compare_pair_0_10

    matrix = []
    for j in jd_skills:
        row = []
        for c in cv_skills:
            s = score_fn(j, c)
            row.append({"cv_skill": c, "score": round(s, 2)})
        row_sorted = sorted(row, key=lambda x: x["score"], reverse=True)
        best = row_sorted[0] if row_sorted else None
        matrix.append({"jd_skill": j, "matches": row_sorted, "best": best})

    best_scores = [r["best"]["score"] for r in matrix if r.get("best")]
    overall = round(sum(best_scores) / max(1, len(best_scores)), 2)
    return {"overall": overall, "matrix": matrix}


def extract_skill_gaps(matrix_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Estrae le TOP-K skill JD con best-score più basso, sotto soglia COMPARATOR_GAP_THRESHOLD.
    Ritorna [{jd_skill, score, best_cv_skill}]
    """
    thr = float(getattr(settings, "COMPARATOR_GAP_THRESHOLD", 6.0))
    k = int(getattr(settings, "COMPARATOR_TOP_K_GAPS", 3))

    candidates = []
    for row in matrix_payload.get("matrix", []):
        best = row.get("best")
        if not best:
            continue
        if best["score"] < thr:
            candidates.append(
                {
                    "jd_skill": row["jd_skill"],
                    "score": best["score"],
                    "best_cv_skill": best["cv_skill"],
                }
            )
    candidates.sort(key=lambda x: x["score"])  # più basso = gap più importante
    return candidates[:k]


# ========== QUESTIONER: domande dai GAP ==========
def generate_gap_questions_t5(
    jd_title: str, gaps: List[Dict[str, Any]], max_questions: int | None = None
) -> List[Dict[str, Any]]:
    """
    Genera domande con il modello Questioner (T5) + guardrail:
    - prompt in italiano
    - estrazione prima frase interrogativa
    - rimozione di meta-testo (es. "Genera una domanda...")
    - fallback template-based se il modello fallisce
    Ritorna fino a 3 domande: 2 Sì/No + 1 short (se possibile).
    """
    import re, unicodedata, torch

    model_q, tokenizer_q = get_questioner()
    device = get_device()

    def _clean(txt: str) -> str:
        if not isinstance(txt, str):
            return ""
        # rimuovi eventuali blocchi tra [] in coda
        txt = re.sub(r"\s*\[[^\]]*\]\s*$", "", txt).strip()
        # rimuovi istruzioni tipo "genera una domanda..." all'inizio
        txt = re.sub(r"^\s*(genera\s+.*?\?)\s*", "", txt, flags=re.I)
        # prendi la prima frase che termina con ? oppure il primo punto
        m = re.search(r"(.+?\?)", txt)
        if not m:
            m = re.search(r"(.+?\.)", txt)
        txt = (m.group(1) if m else txt).strip()
        # capitalizza la prima lettera
        if txt and txt[0].islower():
            txt = txt[0].upper() + txt[1:]
        return txt

    def _gen(prompt: str) -> str:
        with torch.no_grad():
            inputs = tokenizer_q(
                prompt, return_tensors="pt", truncation=True, max_length=256
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}
            ids = model_q.generate(
                inputs["input_ids"],
                max_length=48,
                num_beams=5,
                early_stopping=True,
                no_repeat_ngram_size=3,
            )
            out = tokenizer_q.decode(ids[0], skip_special_tokens=True)
            return _clean(out)

    if not gaps:
        return []

    if max_questions is None:
        max_questions = 3
    gaps = gaps[:max_questions]

    out: List[Dict[str, Any]] = []
    try:
        # 1) due sì/no
        for i, g in enumerate(gaps[:2]):
            skill = g["jd_skill"]
            prompt = (
                f"Ruolo: {jd_title}.\n"
                f"Competenza da verificare: {skill}.\n"
                "Scrivi UNA sola domanda CHIUSA (risposta Sì/No), concreta e specifica, in italiano, max 20 parole."
            )
            q = _gen(prompt)
            if not q.endswith("?"):
                q = q.rstrip(".") + "?"
            out.append({"skill": skill, "type": "yesno", "question": q})

        # 2) una short (se abbiamo almeno 3 gap)
        if len(gaps) >= 3:
            skill = gaps[2]["jd_skill"]
            # Forziamo una domanda breve deterministica, così non esce una chiusa
            q = f"Descrivi in una riga un’attività concreta che hai svolto con {skill}."
            out.append({"skill": skill, "type": "short", "question": q})

    except Exception:
        # Fallback deterministico se il modello non risponde
        out = []
        if len(gaps) >= 1:
            out.append(
                {
                    "skill": gaps[0]["jd_skill"],
                    "type": "yesno",
                    "question": f"Hai esperienza pratica con {gaps[0]['jd_skill']}?",
                }
            )
        if len(gaps) >= 2:
            out.append(
                {
                    "skill": gaps[1]["jd_skill"],
                    "type": "yesno",
                    "question": f"Hai usato {gaps[1]['jd_skill']} in un progetto reale negli ultimi 12 mesi?",
                }
            )
        if len(gaps) >= 3:
            out.append(
                {
                    "skill": gaps[2]["jd_skill"],
                    "type": "short",
                    "question": f"Descrivi in una riga un'attività che hai svolto con {gaps[2]['jd_skill']}.",
                }
            )

    return out

# use local ai model
modello_path = os.path.join("modelli", "qwen_hr")

try:
    print("Caricamento del modello IA locale in corso (potrebbe impiegare qualche secondo)...")
    generatore_hr = pipeline(
        "text-generation",
        model=modello_path, 
        device="cpu" 
    )
    print("Modello IA caricato e pronto all'uso!")
except Exception as e:
    print(f"Errore caricamento IA: {e}")
    generatore_hr = None

def genera_consiglio_ia(skills_mancanti):
    if not skills_mancanti or not generatore_hr:
        return "Ti invitiamo comunque a continuare a perfezionare le tue competenze per le sfide future."

    messaggi = [
        {"role": "system", "content": "Sei un recruiter professionale. Scrivi una sola frase cortese e diretta (massimo 20 parole) per consigliare a un candidato di studiare le competenze che gli mancano."},
        {"role": "user", "content": f"Le competenze da consigliare sono: {skills_mancanti}. Scrivi solo la frase finale."}
    ]

    risultato = generatore_hr(messaggi, max_new_tokens=70, temperature=0.3, do_sample=True)
    return risultato[0]['generated_text'][-1]['content'].strip()

def hash_personality(personality_str: str) -> str:
    """Transform the personality type (e.g. 'INTJ?) into an hash HMAC_SHA256 deterministic 
    and not reversible without the key PERSONALITY_HASH_PEPPER."""
    normalized = (personality_str or '').strip().upper()
    return hmac.new(
        settings.PERSONALITY_HASH_PEPPER.encode('utf-8'),
        normalized.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
