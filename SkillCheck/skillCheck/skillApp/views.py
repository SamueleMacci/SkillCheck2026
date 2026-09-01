import base64
import time
from rest_framework import generics
import json
from .forms import JobDescriptionForm, ResumeForm
from .models import Resume
from .serializers import JobDescriptionSerializer
from django.shortcuts import render, redirect, get_object_or_404
from .models import JobDescription
from django.http import HttpResponseRedirect
from .utils import build_jd_cv_matrix, extract_skill_gaps, generate_gap_questions_t5
import re, unicodedata
import random
from django.conf import settings
from .models import PersonalityQuestion


def index(request):
    return redirect("/skillcheck/")


def job_description_list(request):
    job_descriptions = JobDescription.objects.all()
    return render(
        request, "job_description_list.html", {"job_descriptions": job_descriptions}
    )


def job_description_details(request, pk):
    job_description = get_object_or_404(JobDescription, pk=pk)
    return render(
        request, "job_description_details.html", {"job_description": job_description}
    )


def create_job_description(request):
    if request.method == "POST":
        form = JobDescriptionForm(request.POST)
        if form.is_valid():
            job_description = form.save(commit=False)
            job_description.save()  # Salva la job description per ottenere un ID
            return redirect(
                "select_questions_for_job_description",
                job_description_id=job_description.pk,
            )
    else:
        form = JobDescriptionForm()
    return render(request, "create_job_description_form.html", {"form": form})


def _clean_generated_question(question):
    return question.strip("[]{}' ").strip('"')


def parse_generated_questions(job_description):
    """Estrae le domande auto-generate (esperienze/competenze/titoli di studio)
    dai campi testuali salvati sulla JobDescription."""
    esperienze_questions = [
        _clean_generated_question(question)
        for questions_chunk in job_description.domande_esperienze.split("',")
        for question in questions_chunk.split('",')
    ]
    competenze_questions = [
        _clean_generated_question(question)
        for questions_chunk in job_description.domande_competenze.split("',")
        for question in questions_chunk.split('",')
    ]
    titoli_di_studio_questions = [
        _clean_generated_question(question)
        for questions_chunk in job_description.domande_titoli_di_studio.split("',")
        for question in questions_chunk.split('",')
    ]
    return {
        "esperienze_questions": esperienze_questions,
        "competenze_questions": competenze_questions,
        "titoli_di_studio_questions": titoli_di_studio_questions,
    }


def select_questions_for_job_description(request, job_description_id):
    job_description = JobDescription.objects.get(pk=job_description_id)

    context = {"job_description": job_description}
    context.update(parse_generated_questions(job_description))
    return render(request, "select_questions_for_job_description.html", context)


def save_selected_questions(request, pk):
    if request.method != "POST":
        return redirect("index")

    job_description = JobDescription.objects.get(pk=pk)

    # domande selezionate
    selected_esperienze = request.POST.getlist("selected_esperienze")
    selected_competenze = request.POST.getlist("selected_competenze")
    selected_titoli_di_studio = request.POST.getlist("selected_titoli_di_studio")

    # nuove domande aggiunte dall’utente
    new_questions_esperienze = request.POST.getlist("new_questions[esperienze][][text]")
    new_questions_competenze = request.POST.getlist("new_questions[competenze][][text]")
    new_questions_titoli_di_studio = request.POST.getlist(
        "new_questions[titoli_di_studio][][text]"
    )

    # unione
    all_selected_esperienze = selected_esperienze + new_questions_esperienze
    all_selected_competenze = selected_competenze + new_questions_competenze
    all_selected_titoli_di_studio = (
        selected_titoli_di_studio + new_questions_titoli_di_studio
    )

    # salvataggio
    job_description.save_selected_questions(
        all_selected_esperienze, all_selected_competenze, all_selected_titoli_di_studio
    )
    ts = int(time.time())
    destinazione = "dashboard" if getattr(job_description, "is_public", True) else "SkillPath"
    return HttpResponseRedirect(f"/skillcheck/#/{destinazione}?r={ts}")


def apply_for_job(request, job_description_id):
    job_description = JobDescription.objects.get(
        pk=job_description_id
    )  # Ottieni la descrizione del lavoro

    if request.method == "POST":
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            job_description = JobDescription.objects.get(pk=job_description_id)
            resume.job_description = job_description
            print("pre save")
            resume.save()
            print("post save")
            job_description.resumes.add(resume)
            return redirect(
                "mostra_domande",
                resume_id=resume.id,
                job_description_id=job_description_id,
            )
    else:
        form = ResumeForm()
    return render(
        request,
        "apply_for_job.html",
        {"form": form, "job_description": job_description},
    )


def _normalize(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
    return s


def canon_skill(s: str) -> str:
    """
    Estrae il 'cuore' della skill da una domanda JD tipica.
    Esempi:
    'Sai programmare in C++?' -> 'C++'
    'Hai mai utilizzato Git?' -> 'Git'
    'Hai esperienza con PostgreSQL?' -> 'PostgreSQL'
    """
    if not isinstance(s, str):
        return ""
    s0 = s.strip()

    # 1) pattern "sai programmare in X"
    m = re.search(r"sai programmare in\s+([A-Za-z0-9\+\#\.\-_ ]+)", s0, flags=re.I)
    if m:
        return m.group(1).strip(" ?.,")

    # 2) pattern "hai (mai )?utilizzato X"
    m = re.search(
        r"hai (mai )?utilizzato\s+([A-Za-z0-9\+\#\.\-_ ]+)", s0, flags=re.I
    )
    if m:
        return m.group(2).strip(" ?.,")

    # 3) pattern "hai esperienza con X"
    m = re.search(r"hai esperienza con\s+([A-Za-z0-9\+\#\.\-_ ]+)", s0, flags=re.I)
    if m:
        return m.group(1).strip(" ?.,")

    # 4) fallback: togli boilerplate comuni e punteggiatura finale
    s1 = re.sub(
        r"^(sai|conosci|hai esperienza|hai mai utilizzato|hai competenze)\s+(in|con)?\s*",
        "",
        s0,
        flags=re.I,
    )
    return s1.strip(" ?.,")


def _get_domande_job_desc_resume(resume, job_description):
    domande_job_desc = []
    if job_description.domande_selezionate:
        domande_job_desc = [
            r for r in job_description.domande_selezionate.split("\n") if r.strip()
        ]

    resume_questions_raw = (resume.domande_personali or "").strip("[]")
    domande_resume = [
        d.strip().strip("'").strip()
        for d in resume_questions_raw.split("',")
        if d.strip().strip("'")
    ]
    return domande_job_desc, domande_resume


def save_domande_risposte(resume, domande_job_desc, domande_resume, risposte):
    """Salva le risposte alle domande JD/resume/gap per un resume.
    `risposte` è un dict-like (request.POST oppure request.data)."""
    punteggio_affinita = 0
    totale_domande_si_no = 0
    domande_e_risposte = {}

    for chiave, valore in risposte.items():
        if chiave.startswith("domanda_job_desc_"):
            try:
                idx = int(chiave.split("_")[-1]) - 1
                testo_domanda = domande_job_desc[idx]
            except Exception:
                continue
            domande_e_risposte[testo_domanda] = valore
            totale_domande_si_no += 1
            if valore == "si":
                punteggio_affinita += 1

        elif chiave.startswith("domanda_resume_"):
            try:
                idx = int(chiave.split("_")[-1]) - 1
                testo_domanda = domande_resume[idx]
            except Exception:
                continue
            domande_e_risposte[testo_domanda] = valore
            totale_domande_si_no += 1
            if valore == "si":
                punteggio_affinita += 1

    # Risposte GAP
    gap_answers, yes_count, no_count = [], 0, 0
    i = 0
    while True:
        key = f"gap_yesno_{i}"
        if key not in risposte:
            break
        val = risposte.get(key)
        if val == "si":
            yes_count += 1
        elif val == "no":
            no_count += 1
        gap_answers.append({"type": "yesno", "index": i, "value": val})
        i += 1

    j = 0
    while True:
        key = f"gap_short_{j}"
        if key not in risposte:
            break
        text = (risposte.get(key) or "").strip()
        skill = risposte.get(f"gap_short_skill_{j}") or None
        gap_answers.append(
            {"type": "short", "index": j, "value": text, "skill": skill}
        )
        j += 1

    gap_summary = {
        "yes": yes_count,
        "no": no_count,
        "total_yesno": yes_count + no_count,
    }

    # (opzionale) salva anche matrix/gaps per audit
    jd_skills = [str(s) for s in domande_job_desc]
    cv_skills = [str(s) for s in domande_resume]
    matrix_payload = build_jd_cv_matrix(jd_skills, cv_skills)
    gaps = extract_skill_gaps(matrix_payload)

    # normalizza su scala 0..10, coerente con score_similarity (altrimenti la
    # "Media totale" media un conteggio grezzo di risposte con un punteggio 0..10)
    if totale_domande_si_no > 0:
        resume.domande_affinity = round((punteggio_affinita / totale_domande_si_no) * 10, 2)
    else:
        resume.domande_affinity = 0.0
    base = domande_e_risposte if isinstance(domande_e_risposte, dict) else {}
    base["gap_answers"] = gap_answers
    base["gap_summary"] = gap_summary
    base["gap_overall"] = None
    base["skill_alignment"] = matrix_payload
    base["skill_gaps"] = gaps
    resume.domande_e_risposte = base
    resume.save_affinity()


def build_mostra_domande_context(resume, job_description, domande_job_desc, domande_resume):
    """Genera le domande GAP (IA) e assembla il contesto per la pagina 'mostra domande'."""
    resume_start = len(domande_job_desc)

    # -------------------- genera domande GAP --------------------
    jd_skills_raw = [str(s) for s in domande_job_desc]
    jd_skills = [canon_skill(s) for s in jd_skills_raw]
    cv_skills = [str(s) for s in domande_resume]

    matrix_payload = build_jd_cv_matrix(jd_skills, cv_skills)
    gaps = extract_skill_gaps(matrix_payload)

    # DEBUG A
    print("DEBUG_MATRIX_OVERALL:", matrix_payload.get("overall", None))
    print("DEBUG_GAPS_COUNT:", len(gaps))
    print("DEBUG_GAPS_ITEMS:", [g.get("jd_skill") for g in gaps])

    job_title = getattr(job_description, "title", "Posizione")

    # --- T5 + "polish" con template puliti ---
    def extract_skill_from_text(q: str) -> str:
        if not isinstance(q, str):
            return ""
        # prova a prendere la skill dal testo di T5 (es: "... in C++?" / "... con Git?")
        m = re.search(r"\b(in|con)\s+([A-Za-z0-9\+\#\.\-_ ]+)\??$", q, flags=re.I)
        if m:
            return m.group(2).strip(" ?.,")
        return q.strip(" ?.,")

    def normalize_qtype(t: str) -> str:
        t = (t or "").lower()
        # se T5 dice "short/open" mappo a short, altrimenti default yes/no
        if "short" in t or "aperta" in t or "open" in t:
            return "short"
        return "yesno"

    def to_clean_templates(items: list[dict]) -> list[dict]:
        cleaned = []
        for it in items or []:
            # prendo la skill da campo o la estraggo dal testo
            raw_skill = it.get("skill") or extract_skill_from_text(
                it.get("question") or ""
            )
            skill = canon_skill(raw_skill) or raw_skill
            qtype = normalize_qtype(it.get("type"))

            if not skill:
                continue

            if qtype == "yesno":
                text = f"Hai utilizzato {skill} negli ultimi 12 mesi in un contesto lavorativo o universitario?"
            else:
                text = f"In una riga, descrivi un’attività concreta in cui hai usato {skill}."
            cleaned.append({"skill": skill, "type": qtype, "question": text})
        return cleaned

    gap_questions = []
    try:
        tmp = generate_gap_questions_t5(job_title, gaps, max_questions=3)
        # mapping su template puliti (AI decide cosa chiedere; i template curano la forma)
        gap_questions = to_clean_templates(tmp if isinstance(tmp, list) else [])
    except Exception as e:
        print("DEBUG_T5_ERROR:", repr(e))
        # fallback deterministico già "pulito"
        try:
            gap_questions = [
                {
                    "skill": canon_skill(g.get("jd_skill")),
                    "type": "yesno",
                    "question": f"Hai utilizzato {canon_skill(g.get('jd_skill'))} negli ultimi 12 mesi in un contesto lavorativo o universitario?",
                }
                for g in (gaps or [])
            ][:3]
        except Exception as e2:
            print("DEBUG_FALLBACK_ERROR:", repr(e2))
            gap_questions = []

    # DEBUG B
    print("DEBUG_GAP_QUESTIONS_RAW:", [q.get("question") for q in gap_questions])

    # ---- DEDUP SOFT: elimina SOLO uguaglianze esatte normalizzate ----------------

    def _clean_question_text(q: str) -> str:
        if not isinstance(q, str):
            return ""
        # rimuovi [ ... ] finali e il boilerplate più comune
        q = re.sub(r"\s*\[[^\]]*\]\s*$", "", q).strip()
        q_low = q.lower()
        q_low = re.sub(
            r"^(hai esperienza nella competenza da verificare|verifica competenza|competenza da verificare)\s*:\s*",
            "",
            q_low,
            flags=re.I,
        )
        # ripristina capitalizzazione semplice
        q = (q_low[0].upper() + q_low[1:]).strip() if q_low else ""
        # togli doppie spaziature e normalizza ?! finali
        q = re.sub(r"\s+", " ", q).strip()
        q = re.sub(r"[?.!]+$", "", q).strip() + "?"
        return q

    existing_texts = [str(x) for x in (domande_job_desc + domande_resume)]
    existing_norm = {_normalize(t) for t in existing_texts}

    filtered = []
    seen = set()
    for item in gap_questions or []:
        raw_q = item.get("question") or ""
        clean_q = _clean_question_text(raw_q)
        n = _normalize(clean_q)

        # elimina SOLO se identico a qualcosa già in pagina o già visto tra GAP
        if n in existing_norm or n in seen or not clean_q:
            continue

        item["question"] = clean_q
        seen.add(n)
        filtered.append(item)

    gap_questions = filtered
    # ------------------------------------------------------------------------------

    # --- Garantisci almeno 2 yes/no non duplicate rispetto a JD/Resume ---
    used_norm = set(existing_norm) | {
        _normalize(q.get("question", "")) for q in gap_questions
    }

    def _add_yesno_for(skill: str) -> bool:
        skill = canon_skill(skill)
        if not skill:
            return False
        templates = [
            f"Hai utilizzato {skill} negli ultimi 12 mesi in un contesto lavorativo o universitario?",
            f"Hai esperienza pratica recente con {skill} in progetti reali?",
        ]
        for q in templates:
            n = _normalize(q)
            if n not in used_norm:
                gap_questions.append({"skill": skill, "type": "yesno", "question": q})
                used_norm.add(n)
                return True
        return False

    # quante yes/no abbiamo dopo la dedup?
    ysn = sum(1 for q in gap_questions if q.get("type") == "yesno")
    if ysn < 2:
        for g in gaps or []:
            if ysn >= 2:
                break
            if _add_yesno_for(g.get("jd_skill")):
                ysn += 1

    # se ancora zero short, prova ad aggiungerne UNA con frase migliore
    has_short = any(q.get("type") == "short" for q in gap_questions)
    if not has_short:
        for g in gaps or []:
            skill = g.get("jd_skill")
            if not skill:
                continue
            short_q = f"Descrivi in una riga un’attività concreta in cui hai usato {canon_skill(skill)}."
            n = _normalize(short_q)
            if n not in used_norm:
                gap_questions.append(
                    {"skill": skill, "type": "short", "question": short_q}
                )
                used_norm.add(n)
                break

    # -- Fallback: se tutto scartato, proponi fino a 2 yes/no + 1 short NON identiche alla JD --
    if not gap_questions:
        used_norm = set(existing_norm)
        added = 0
        for g in gaps or []:
            skill = g.get("jd_skill")
            if not skill:
                continue
            q = f"Hai esperienza pratica recente con {skill}?"
            n = _normalize(q)
            if n in used_norm:
                continue
            gap_questions.append({"skill": skill, "type": "yesno", "question": q})
            used_norm.add(n)
            added += 1
            if added >= 2:
                break

        # short fissa su una skill rimanente (se disponibile)
        for g in gaps or []:
            skill = g.get("jd_skill")
            if not skill:
                continue
            q = f"Descrivi in una riga un’attività concreta che hai svolto con {skill}."
            n = _normalize(q)
            if n in used_norm:
                continue
            gap_questions.append({"skill": skill, "type": "short", "question": q})
            break

    # DEBUG C
    print(
        "DEBUG_GAP_QUESTIONS_AFTER_DEDUP:", [q.get("question") for q in gap_questions]
    )

    gap_questions = (gap_questions or [])[:3]

    return {
        "domande_job_desc": domande_job_desc,
        "domande_resume": domande_resume,
        "resume_start": resume_start,
        "gap_questions": gap_questions,
    }


def mostra_domande(request, resume_id, job_description_id):
    resume = get_object_or_404(Resume, pk=resume_id)
    job_description = get_object_or_404(JobDescription, pk=job_description_id)

    # --- JD & Resume questions prep ---
    domande_job_desc, domande_resume = _get_domande_job_desc_resume(resume, job_description)

    if request.method == "POST":
        save_domande_risposte(resume, domande_job_desc, domande_resume, request.POST)
        return redirect("personality_test", resume_id=resume.id)

    # -------------------- GET: genera domande GAP e mostra pagina --------------------
    context = build_mostra_domande_context(resume, job_description, domande_job_desc, domande_resume)
    context["resume"] = resume
    return render(request, "mostra_domande.html", context)


def mostra_risposte(request, resume_id):
    resume = get_object_or_404(Resume, pk=resume_id)

    data = resume.domande_e_risposte or {}
    INTERNAL_KEYS = {
        "gap_answers",
        "gap_summary",
        "gap_overall",
        "skill_alignment",
        "skill_gaps",
    }

    qa_pairs = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k in INTERNAL_KEYS:
                continue
            qa_pairs.append((str(k), str(v)))

    # 2) Sezione GAP
    gap_answers = data.get("gap_answers") or []
    gap_summary = data.get("gap_summary") or {}
    gap_overall = data.get("gap_overall")

    context = {
        "qa_pairs": qa_pairs,
        "gap_answers": gap_answers,
        "gap_summary": gap_summary,
        "gap_overall": gap_overall,
        "job_id": resume.job_description_id,
    }
    return render(request, "risposte_domande.html", context)


def view_applied_resumes(request, pk):
    job_description = get_object_or_404(JobDescription, pk=pk)
    resumes = Resume.objects.filter(job_description=job_description)

    for resume in resumes:
        voti = [
            resume.titoli_di_studio_similarity,
            resume.competenze_similarity,
            resume.esperienze_similarity,
        ]
        # escludi None
        voti = [v for v in voti if v is not None]
        media_voti = (sum(voti) / len(voti)) if voti else 0.0
        resume.media_voti = round(media_voti, 2)

        aff = resume.domande_affinity if resume.domande_affinity is not None else 0.0
        avg_tot = (float(media_voti) + float(aff)) / 2.0
        resume.media_tot = round(avg_tot, 2)

        # salva solo se vuoi persistere il valore
        resume.save(update_fields=["media_voti", "media_tot"])

    return render(
        request,
        "view_applied_resumes.html",
        {"job_description": job_description, "resumes": resumes},
    )


def view_pdf(request, resume_id):
    resume = get_object_or_404(Resume, pk=resume_id)
    pdf_data = (
        resume.pdf_file
    )  # Supponendo che 'pdf_file' contenga i dati binari del PDF

    # Converti i dati binari del PDF in una stringa codificata in Base64
    base64_pdf = base64.b64encode(pdf_data).decode("utf-8")

    return render(request, "view_pdf.html", {"base64_pdf": base64_pdf})

def personality_test(request, resume_id):
    resume = get_object_or_404(Resume, pk=resume_id)
    
    if request.method == "GET":
        # 1. MODIFICA CHIAVE: Niente più 'list()' e niente più 'random.shuffle()'.
        # Chiediamo direttamente al database di darci le domande in ordine di ID.
        domande = PersonalityQuestion.objects.all().order_by('id')
        
        return render(request, 'personality_test.html', {'domande': domande, 'resume': resume})
    
    elif request.method == "POST":
        risposte = {}
        
        # 2. LOGICA POST: Raccoglie i valori (domanda_1, domanda_2...) e li mette nel dizionario
        for i in range(1, 51):
            campo_form = f"domanda_{i}"
            if campo_form in request.POST:
                risposte[str(i)] = int(request.POST.get(campo_form))
        
        # 3. SALVATAGGIO: Qui entra in gioco la magia del campo che abbiamo appena creato!
        # Django prenderà questo dizionario 'risposte', lo trasformerà in testo
        # e la libreria cryptography lo salverà in formato binario illeggibile nel database.
        resume.risposte_personalita_raw = risposte
        resume.save(update_fields=['risposte_personalita_raw'])

        # Renderizza direttamente il messaggio di completamento
        context = {
            'resume': resume,
            'message': 'Grazie per aver completato il test di personalità! Le tue risposte sono state salvate in modo sicuro.'
        }
        return render(request, 'personality_test_complete.html', context)